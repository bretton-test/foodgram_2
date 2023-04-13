from django.db.models.signals import pre_delete, m2m_changed, pre_save, post_save
from django.dispatch import receiver
from rest_framework.exceptions import ValidationError

from recipes.models import Recipe


@receiver(pre_delete, sender=Recipe.ingredients.through)
def delete_ingredients(sender, instance, **kwargs):
    if instance.recipe.ingredients.count() <= 1:
        raise ValidationError('Нужно добавить ингредиенты')
