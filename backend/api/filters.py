import django_filters

from recipes.models import Recipe, Tag

FILTER_CHOICES = (('0', False), ('1', True))


def get_filtered_queryset(queryset, recipes, value):
    return (
        queryset.filter(id__in=recipes)
        if dict(FILTER_CHOICES)[value]
        else queryset.exclude(id__in=recipes)
    )


class RecipeFilter(django_filters.FilterSet):
    is_favorited = django_filters.ChoiceFilter(
        choices=FILTER_CHOICES, method='is_favorited_method'
    )

    is_in_shopping_cart = django_filters.ChoiceFilter(
        choices=FILTER_CHOICES, method='is_in_shopping_cart_method'
    )

    def is_favorited_method(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous:
            return Recipe.objects.none()
        recipes = user.favorites.values('recipe__id')
        return get_filtered_queryset(queryset, recipes, value)

    def is_in_shopping_cart_method(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous:
            return Recipe.objects.none()
        recipes = user.shopping_list.values('recipe__id')
        return get_filtered_queryset(queryset, recipes, value)

    author = django_filters.NumberFilter(
        field_name='author', lookup_expr='exact'
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags')
