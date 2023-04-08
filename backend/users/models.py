from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Foodgram User Model"""

    username_validator = UnicodeUsernameValidator()
    email = models.EmailField(
        _('email address'),
        blank=False,
        unique=True,
        error_messages={
            'unique': _("Такой email уже используется."),
        },
    )
    username = models.CharField(
        _('username'),
        max_length=settings.USER_NAME_MAX_LENGTH,
        unique=True,
        help_text=_(
            'Обязательно к заполнению.'
            ' <=150 символов. Только буквы, цифры и @/./+/-/_.'
        ),
        validators=(username_validator,),
        error_messages={
            'unique': _("Это имя занято."),
        },
    )
    first_name = models.CharField(
        _('first name'), max_length=settings.USER_NAME_MAX_LENGTH, blank=False
    )
    last_name = models.CharField(
        _('last name'), max_length=settings.USER_NAME_MAX_LENGTH, blank=False
    )
    password = models.CharField(
        _('password'), max_length=settings.USER_NAME_MAX_LENGTH
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)


class Follow(models.Model):
    """Follow user to author model"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='авторы',
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'

        constraints = (
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='no_self_following',
            ),
            models.UniqueConstraint(
                fields=('user', 'author'), name='unique_follower'
            ),
        )

    def __str__(self):
        return f'Подписка {self.user} на {self.author}'
