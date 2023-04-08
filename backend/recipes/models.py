from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    """Foodgram tag model"""

    name = models.CharField(
        max_length=settings.NAME_FIELD_MAX_LENGTH,
        unique=True,
        blank=False,
        verbose_name='Название тега',
        help_text='Название тега',
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет для тега',
        help_text='Цвет для тега',
    )
    slug = models.SlugField(
        max_length=settings.SLUG_FIELD_MAX_LENGTH,
        unique=True,
        verbose_name='Идентификатор тега',
        help_text='Идентификатор тега',
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Unit(models.Model):
    """Unit model for ingredients"""

    name = models.CharField(
        max_length=10,
        unique=True,
        blank=False,
        verbose_name='Единица измерения',
        help_text='Единица измерения',
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True,
    )

    class Meta:
        verbose_name = 'Единица измерения'
        verbose_name_plural = 'Единицы измерения'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Foodgram Ingredient Model"""

    name = models.CharField(
        max_length=settings.NAME_FIELD_MAX_LENGTH,
        verbose_name='Название ингредиента',
        help_text='Название ингредиента',
    )
    measurement_unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        related_name='units',
        verbose_name='Единица измерения ингредиента',
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'), name='unique_ingredient'
            ),
        )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Foodgram Recipe Model"""

    name = models.CharField(
        max_length=settings.NAME_FIELD_MAX_LENGTH,
        verbose_name='Название рецепта',
        help_text='Название рецепта',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Описание рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Игредиенты для рецепта',
        help_text='Игредиенты для рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(1),),
        verbose_name='Время приготовления',
        help_text='Время приготовления',
    )
    image = models.ImageField(
        verbose_name='Изображение для рецепта',
        help_text='Изображение для рецепта',
        upload_to='recipes/images/',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации рецепта',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        related_name='recipes',
        verbose_name='Теги рецепта',
        help_text='Теги рецепта',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'name'), name='unique__author_name'
            ),
        )

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Recipe -> ingredients many-to-many model"""

    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_ingredient',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.PROTECT, verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(1),), verbose_name='Количество'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique__recipe_ingredient',
            ),
        )

    def __str__(self):
        return f'{self.ingredient} in {self.recipe} ingredients list'


class RecipeTag(models.Model):
    """Recipe -> tags many-to-many model"""

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт'
    )
    tag = models.ForeignKey(Tag, on_delete=models.PROTECT, verbose_name='Тег')

    def __str__(self):
        return f'{self.tag} in {self.recipe} tags'


class Favorite(models.Model):
    """Users favorite model"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_favorite',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранное'

        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'), name='unique_favorite_recipe'
            ),
        )

    def __str__(self):
        return f'{self.recipe} in {self.user} favorite'


class ShoppingList(models.Model):
    """Users shopping lists model"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_list',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'Список покупок'

        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'), name='unique_shopping_list_recipe'
            ),
        )

    def __str__(self):
        return f'{self.recipe} in {self.user} shopping list'
