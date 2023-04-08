from django.contrib.auth import get_user_model
from django.utils.datastructures import MultiValueDictKeyError
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import LowercaseEmailField
from rest_framework import serializers

from api.utils import get_recipe_serializer

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    email = LowercaseEmailField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
        )


class UserBaseSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        user = self.context['request'].user
        is_subscribed = (
            False
            if user.is_anonymous
            else instance.following.filter(user_id=user.id).exists()
        )
        return {
            'id': instance.id,
            'username': instance.username,
            'first_name': instance.first_name,
            'last_name': instance.last_name,
            'email': instance.email,
            'is_subscribed': is_subscribed,
        }


class SubscriptionSerializer(UserBaseSerializer):
    def to_representation(self, instance, user=None):
        data = super(SubscriptionSerializer, self).to_representation(instance)
        data['recipes_count'] = instance.recipes.count()
        author_recipes = instance.recipes.all()
        try:
            recipes_limit = self.context.get('request').GET['recipes_limit']
            author_recipes = author_recipes[: int(recipes_limit)]
        except (MultiValueDictKeyError, ValueError):
            pass

        recipes = get_recipe_serializer()(
            author_recipes,
            many=True,
        )
        data['recipes'] = recipes.data

        return data
