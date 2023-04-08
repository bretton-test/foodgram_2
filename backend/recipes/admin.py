from django.contrib import admin

from api.utils import get_end_letter

from .models import Favorite, Ingredient, Recipe, ShoppingList, Tag, Unit


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    list_display_links = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name',)
    list_display_links = ('name',)


class RecipeIngredientsInLine(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1
    min_num = 1


class RecipeTagsInLine(admin.TabularInline):
    model = Recipe.tags.through
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_display_links = ('name',)
    list_filter = ('name', 'author__username', 'tags')
    search_fields = ('name',)
    inlines = (RecipeIngredientsInLine, RecipeTagsInLine)
    readonly_fields = ('in_favorite',)

    def in_favorite(self, obj):
        label = obj.in_favorite.count()
        end_letter = get_end_letter(label)
        return f'всего рецепт добавлен в избранное  {label} раз{end_letter}'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_display_links = ('user',)
    list_filter = ('user__username',)


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_display_links = ('user',)
    list_filter = ('user__username',)
