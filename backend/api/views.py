from django.db.models import Case, F, FloatField, Q, Sum, Value, When
from django.http import FileResponse
from django_filters.utils import translate_validation
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.permissions import IsOwnerOrStaffOrReadOnly, check_object_permissions
from api.report import create_pdf_from_queryset
from api.serializers import (
    IngredientSerializer, RecipeFavoriteSerializer, RecipeSerializer,
    TagSerializer,
)
from api.utils import create_or_delete_record
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.pagination import CustomPageNumberPagination


@api_view(('GET',))
@permission_classes((AllowAny,))
def tags(request, pk=None):
    queryset = (
        Tag.objects.all() if pk is None else get_object_or_404(Tag, pk=pk)
    )
    serializer = TagSerializer(queryset, many=pk is None)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(('GET',))
@permission_classes((AllowAny,))
def ingredients(request, pk=None):
    if pk is not None:
        serializer = IngredientSerializer(
            get_object_or_404(Ingredient, pk=pk), many=False
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    string = request.query_params.get('name', None)
    if string is not None:
        queryset = (
            Ingredient.objects.select_related('measurement_unit')
            .filter(Q(name__istartswith=string) | Q(name__icontains=string))
            .annotate(
                k1=Case(
                    When(name__istartswith=string, then=Value(1.0)),
                    default=Value(0.0),
                    output_field=FloatField(),
                ),
                k2=Case(
                    When(name__icontains=string, then=Value(1.0)),
                    default=Value(0.0),
                    output_field=FloatField(),
                ),
                rank=F("k1") + F("k2"),
            )
            .distinct()
            .order_by('-rank', 'name')
        )
    else:
        queryset = Ingredient.objects.all()

    serializer = IngredientSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(('POST', 'DELETE'))
@permission_classes((IsAuthenticated,))
def favorite(request, pk=None):
    recipe = get_object_or_404(Recipe, pk=pk)
    in_favorite = recipe.in_favorite.filter(user=request.user)
    return create_or_delete_record(
        request=request,
        record=in_favorite,
        serializer_data=RecipeFavoriteSerializer(recipe).data,
        params={'recipe': recipe},
    )


@api_view(('POST', 'DELETE'))
@permission_classes((IsAuthenticated,))
def shopping_cart(request, pk=None):
    recipe = get_object_or_404(Recipe, pk=pk)
    in_shopping_list = recipe.in_shopping_list.filter(user=request.user)
    return create_or_delete_record(
        request=request,
        record=in_shopping_list,
        serializer_data=RecipeFavoriteSerializer(recipe).data,
        params={'recipe': recipe},
    )


@api_view(('GET',))
@permission_classes((IsAuthenticated,))
def download_shopping_cart(request):
    user = request.user
    recipes = user.shopping_list.values('recipe__id')
    buy_list = (
        RecipeIngredient.objects.filter(recipe__in=recipes)
        .values('ingredient__name', 'ingredient__measurement_unit__name')
        .annotate(amount=Sum('amount'))
        .order_by('ingredient__name')
    )
    pdf_file = create_pdf_from_queryset(buy_list, user.username)
    return FileResponse(pdf_file, as_attachment=True, filename='buy_list.pdf')


@api_view(('GET', 'POST'))
@permission_classes((IsOwnerOrStaffOrReadOnly,))
def recipe_list(request):
    if request.method == 'GET':
        filterset = RecipeFilter(
            request.GET, queryset=Recipe.objects.all(), request=request
        )
        if not filterset.is_valid():
            raise translate_validation(filterset.errors)

        paginator = CustomPageNumberPagination()
        queryset = paginator.paginate_queryset(filterset.qs, request)
        serializer = RecipeSerializer(
            queryset, many=True, context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)

    if request.method == 'POST':
        return recipe_create(request)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


def recipe_create(request):
    serializer = RecipeSerializer(
        data=request.data, context={'request': request}
    )
    if serializer.is_valid(raise_exception=True):
        serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def recipe_update(request, recipe):
    serializer = RecipeSerializer(
        recipe, data=request.data, partial=True, context={'request': request}
    )
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(('GET', 'PATCH', 'DELETE'))
@permission_classes((IsOwnerOrStaffOrReadOnly,))
def recipe_detail(request, pk=None):
    if request.method == 'GET':
        queryset = get_object_or_404(Recipe, pk=pk)
        serializer = RecipeSerializer(queryset, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    obj = get_object_or_404(Recipe, pk=pk)
    if not check_object_permissions(request, obj):
        return Response(
            'You do not have permission to perform this action.',
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method == 'PATCH':
        return recipe_update(request, obj)

    if request.method == 'DELETE':
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
