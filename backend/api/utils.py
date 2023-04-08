import io
from typing import Dict

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import exceptions, status, permissions
from rest_framework.response import Response

from recipes.models import RecipeIngredient


def get_end_letter(value):
    end_lib: Dict[int, str] = {5: '', 2: 'а', 0: ''}

    for my_key in end_lib:

        if value % 10 >= my_key:
            return end_lib[my_key]

    return ''


def get_recipe_serializer():
    from api.serializers import RecipeFavoriteSerializer

    return RecipeFavoriteSerializer


def create_or_delete_record(request, record, serializer_data, params):
    if request.method == 'POST':

        if record.exists():
            raise exceptions.ValidationError('records already exists.')

        record.create(user=request.user, **params)
        return Response(serializer_data, status=status.HTTP_201_CREATED)

    if request.method == 'DELETE':
        if not record.exists():
            raise exceptions.ValidationError('records does not exists.')
        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


def get_shopping_list_text(
        ingredient__name, ingredient__measurement_unit__name, amount
):
    return (
        f'{ingredient__name}'
        f' ({ingredient__measurement_unit__name}) - {amount}'
    )


def create_pdf_from_queryset(queryset, username):
    pdfmetrics.registerFont(TTFont('DejaVuSerif', 'DejaVuSerif.ttf', 'UTF-8'))
    pdf_file = io.BytesIO()
    w, h = A4
    p = canvas.Canvas(pdf_file, pagesize=A4)
    text = p.beginText(50, h - 50)
    text.setFont('DejaVuSerif', 20)
    text.textLine(f'Список покупок для {username}')
    text.textLine(' ')
    text.textLine(' ')
    text.setFont('DejaVuSerif', 12)
    for items in queryset:
        text.textLine(get_shopping_list_text(**items))
    p.drawText(text)
    p.showPage()
    p.save()
    pdf_file.seek(0)
    return pdf_file


def create_recipe_ingredients(ingredients, recipe):
    RecipeIngredient.objects.bulk_create(
        [
            RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount'],
            )
            for ingredient in ingredients
        ]
    )

