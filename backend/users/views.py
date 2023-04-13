from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import status, exceptions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.pagination import CustomPageNumberPagination
from users.serializers import  SubscriptionSerializer

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPageNumberPagination


@api_view(('POST', 'DELETE'))
@permission_classes((IsAuthenticated,))
def subscribe(request, pk):
    user = request.user
    author = get_object_or_404(User, pk=pk)
    in_follow = user.follower.filter(author=author)
    if request.method == 'POST':
        if user == author:
            raise exceptions.ValidationError('you can`t subscribe to yourself')
        if in_follow.exists():
            raise exceptions.ValidationError('records already exists.')
        serializer = SubscriptionSerializer(
            author, context={'request': request}
        )
        in_follow.create(user=request.user, author=author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    if request.method == 'DELETE':
        if not in_follow.exists():
            raise exceptions.ValidationError('records does not exists.')
        in_follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(('GET',))
@permission_classes((IsAuthenticated,))
def subscriptions(request):
    paginator = CustomPageNumberPagination()
    queryset = paginator.paginate_queryset(
        User.objects.filter(following__user=request.user), request
    )
    serializer = SubscriptionSerializer(
        queryset, many=True, context={'request': request}
    )

    return paginator.get_paginated_response(serializer.data)
