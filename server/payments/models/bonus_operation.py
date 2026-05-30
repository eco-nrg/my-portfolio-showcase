from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class BonusSource(models.TextChoices):
    MANUAL = 'MANUAL', _('Добавлен админом')
    SIGN_UP = 'SIGN_UP', _('Стартовый бонус')
    FILL_PROFILE = 'FILL_PROFILE', _('Бонус заполнения профиля')


class BonusOperationType(models.TextChoices):
    CREDIT = 'CREDIT', _('Списание')  # списание бонусов со счета пользователя
    DEBIT = 'DEBIT', _('Пополнение')  # пополнение бонусами счета пользователя


class BonusOperation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bonus_operations',
        verbose_name='Пользователь',
    )
    kind = models.CharField(
        verbose_name='Тип',
        max_length=32,
        choices=BonusOperationType.choices,
    )
    source = models.CharField(
        verbose_name='За что',
        max_length=32,
        choices=BonusSource.choices,
        default=BonusSource.MANUAL,
    )
    description = models.CharField(
        verbose_name='Описание',
        max_length=255,
    )
    amount = models.DecimalField(
        verbose_name='Сумма',
        default=Decimal(0),
        max_digits=19,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    created_at = models.DateTimeField(
        verbose_name='Создан',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Бонус'
        verbose_name_plural = 'Бонусы'

    def __str__(self) -> str:
        return f'{self.id} ${self.description} {self.amount}'
