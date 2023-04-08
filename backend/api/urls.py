from django.urls import include, path
from rest_framework import routers

from api.views import (
    download_shopping_cart,
    favorite,
    ingredients,
    shopping_cart,
    tags, recipe_list, recipe_detail,
)
from users.views import CustomUserViewSet, subscribe, subscriptions

router_v1 = routers.DefaultRouter()

router_v1.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('tags/', tags, name='tags'),
    path('tags/<int:pk>/', tags, name='tags_detail'),
    path('ingredients/', ingredients, name='ingredients'),
    path('ingredients/<int:pk>/', ingredients, name='ingredients_detail'),
    path('recipes/<int:pk>/favorite/', favorite, name='favorite'),
    path(
        'recipes/<int:pk>/shopping_cart/', shopping_cart, name='shopping_cart'
    ),
    path(
        'recipes/download_shopping_cart/',
        download_shopping_cart,
        name='download_shopping_cart',
    ),
    path('recipes/', recipe_list, name='recipes'),
    path('recipes/<int:pk>/', recipe_detail, name='recipes_detail'),
    path('users/<int:pk>/subscribe/', subscribe, name='users_subscribe'),
    path('users/subscriptions/', subscriptions, name='users_subscriptions'),
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
