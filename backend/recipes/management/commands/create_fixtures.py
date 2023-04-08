import random
import sys

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand
from django.db import IntegrityError

from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, RecipeTag, ShoppingList,
    Tag,
)
from users.models import Follow, User

small_gif = (
    b'\x47\x49\x46\x38\x39\x61\x01\x00'
    b'\x01\x00\x00\x00\x00\x21\xf9\x04'
    b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
    b'\x00\x00\x01\x00\x01\x00\x00\x02'
    b'\x02\x4c\x01\x00\x3b'
)


class Command(BaseCommand):
    help = 'Создание тестовых данных'

    @staticmethod
    def get_random_user():
        return User.objects.all()[random.randint(0, User.objects.count() - 1)]

    def handle(self, *args, **options):

        test_image = SimpleUploadedFile(
            name='small.gif', content=small_gif, content_type='image/gif'
        )
        try:
            user = User.objects.create_user(
                username='HasNoName',
                email='HasNoEmail@mail.com',
                first_name='HasNoFirstName',
                last_name='HasNoLastName',
                password='HasNoPassword',
            )
            another_user = User.objects.create_user(
                username='HasNoName1',
                email='HasNoEmail1@mail.com',
                first_name='HasNoFirstName1',
                last_name='HasNoLastName1',
                password='HasNoPassword',
            )

            Follow.objects.create(user=another_user, author=user)
            Follow.objects.create(user=user, author=another_user)

            if not Tag.objects.exists():
                Tag.objects.create(
                    name='Завтрак', color='#E26C2D', slug='breakfast'
                )
                Tag.objects.create(name='Обед', color='#E26C2D', slug='lunch')
                Tag.objects.create(name='Ужин', color='#E26C2D', slug='dinner')

            for rec_num in range(24):
                recipe = Recipe.objects.create(
                    name=f'Recipe # {rec_num}',
                    text=f'Тестовый рецепт {rec_num}',
                    cooking_time=random.randint(1, 25),
                    image=test_image,
                    author=self.get_random_user(),
                )
                Favorite.objects.create(
                    recipe=recipe, user=self.get_random_user()
                )
                ShoppingList.objects.create(
                    recipe=recipe, user=self.get_random_user()
                )

                for num in range(random.randint(1, 3)):
                    RecipeTag.objects.create(
                        recipe=recipe, tag=Tag.objects.all()[num]
                    )
                for num in range(random.randint(1, 5)):
                    try:
                        RecipeIngredient.objects.create(
                            recipe=recipe,
                            ingredient=Ingredient.objects.all()[
                                random.randint(
                                    0,
                                    Ingredient.objects.count() - 1
                                )
                            ],
                            amount=random.randint(1, 200),
                        )
                    except IntegrityError as error:
                        self.stdout.write(
                            self.style.ERROR(error),
                        )

        except Exception as error:
            self.stdout.write(
                self.style.ERROR(f'Error loading model {error}'),
            )
            sys.exit()

        self.stdout.write(self.style.SUCCESS(' Foodgram Objects Created'))
