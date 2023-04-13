from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from api.utils import create_recipe_ingredients
from recipes.models import Ingredient, Recipe, Tag
from users.serializers import UserBaseSerializer


class RecipeFavoriteSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return {
            'id': instance.id,
            'name': instance.name,
            'image': instance.image.url,
            'cooking_time': instance.cooking_time,
        }


class TagSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return {
            'id': instance.id,
            'name': instance.name,
            'color': instance.color,
            'slug': instance.slug,
        }


class IngredientSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        measurement_unit = instance.measurement_unit.name

        return {
            'id': instance.id,
            'name': instance.name,
            'measurement_unit': measurement_unit,
        }


class RecipeIngredientSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        measurement_unit = instance.ingredient.measurement_unit.name

        return {
            'id': instance.ingredient.id,
            'name': instance.ingredient.name,
            'measurement_unit': measurement_unit,
            'amount': instance.amount,
        }


class RecipeSerializer(serializers.BaseSerializer):
    def validate(self, data):
        param = (
            'ingredients',
            'tags',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        for item in param:
            if not data.get(item):
                raise serializers.ValidationError(f'{item} required')
        if int(data.get('cooking_time')) <= 0:
            raise serializers.ValidationError(
                'cooking_time must be greater than zero'
            )
        try:
            recipe_id = self.instance.id
        except AttributeError:
            recipe_id = None

        user = self.context.get('request').user
        name = self.initial_data.get('name')
        ingredients_value = data.get('ingredients')
        ingredients = [item['id'] for item in ingredients_value]
        ing_count = Ingredient.objects.filter(id__in=ingredients).count()
        for item in ingredients_value:
            if int(item['amount']) <= 0:
                raise serializers.ValidationError(
                    'Ingredient amount must be greater than zero'
                )

        if len(ingredients) != len(set(ingredients)):
            raise serializers.ValidationError(
                'A recipe cannot have two of the same ingredient.'
            )
        if ing_count != len(set(ingredients)):
            raise serializers.ValidationError('ingredients not found')
        tags_value = data.get('tags', None)
        tags_count = Tag.objects.filter(id__in=tags_value).count()
        if tags_count != len(set(tags_value)):
            raise serializers.ValidationError('tags not found')

        if user.recipes.exclude(pk=recipe_id).filter(name=name).exists():
            raise serializers.ValidationError('A recipe name already exists')

        return data

    def to_internal_value(self, data):
        validated_data = self.validate(data)
        image = validated_data.pop('image', None)
        image64 = Base64ImageField()
        image_file = image64.to_internal_value(image)
        validated_data['image'] = image_file
        return validated_data

    def to_representation(self, instance):
        user = self.context['request'].user
        is_favorited = (
            False
            if user.is_anonymous
            else instance.in_favorite.filter(user_id=user.id).exists()
        )
        is_in_shopping_cart = (
            False
            if user.is_anonymous
            else instance.in_shopping_list.filter(user_id=user.id).exists()
        )
        tags = instance.tags.all()
        tags_serializer = TagSerializer(tags, many=True)
        author = instance.author
        author_serializer = UserBaseSerializer(author, context=self.context)
        ingredients_serializer = RecipeIngredientSerializer(
            instance.recipe_ingredient.all(), many=True
        )
        try:
            image = instance.image.url
        except ValueError:
            image = ''

        return {
            'id': instance.id,
            'name': instance.name,
            'text': instance.text,
            'image': image,
            'cooking_time': instance.cooking_time,
            'is_favorited': is_favorited,
            'is_in_shopping_cart': is_in_shopping_cart,
            'tags': tags_serializer.data,
            'author': author_serializer.data,
            'ingredients': ingredients_serializer.data,
        }

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.set(tags)

        ingredients = validated_data.pop('ingredients', None)
        if ingredients is not None:
            instance.ingredients.clear()
        create_recipe_ingredients(ingredients, instance)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance

    @transaction.atomic
    def create(self, validated_data):
        author = self.context.get('request').user
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags_data)
        create_recipe_ingredients(ingredients_data, recipe)
        return recipe
