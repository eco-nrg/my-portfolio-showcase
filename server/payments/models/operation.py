"""Модель лога операция со счетом.

Работа со счетом пользователя по стандартам бухгалтерского учета.
- https://ru.wikipedia.org/wiki/Дебет_и_кредит
- https://senior-sigan.ru/notes/2017-01-30-finance-planing/

Платежи хранятся отдельно и являются объектами, которые могут меняться:
- обновляется статус платежа
- платеж может быть отменен и тд.

Операции же являются логом событий и их запрещено редактировать.
Вместо редактирования - создание новой операции.
Поэтому успешный платеж создает Операцию Пополнения счета.
А списание - создает Операцию Списания с пометкой что это возврат.

Главная идея заключается в том, чтобы сделать простую сумму
по всем операциям пользователя и получит его текущий баланс счета.

Бонусы можно начислять созданием записи.
Вручную начислить деньги можно записью.
Списать тоже можно.

Возможная проблема - какой-то платеж не запишется в лог операций.
В этом случае можно считать, что система потерял консистенстность.
Надо предусмотреть способы отлавливать такие ситуации.
"""

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class OperationType(models.TextChoices):
    CREDIT = 'CREDIT', _('Списание')  # списание со счета пользователя
    DEBIT = 'DEBIT', _('Пополнение')  # пополнение счета пользователя


class OperationAction(models.TextChoices):
    PAYMENT = 'PAYMENT', _('Пополнение счета картой')
    BONUS = 'BONUS', _('Пополнение счёт бонусами')
    BOOKING = 'BOOKING', _('Бронирование')
    ORDER = 'ORDER', _('Оплата заказа')
    REFUND = 'REFUND', _('Возврат средств')
    CANCEL_ORDER = 'CANCEL_ORDER', _('Отмена оплаты')


class Operation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='operations',
        verbose_name='Пользователь',
    )
    kind = models.CharField(
        verbose_name='Тип',
        max_length=6,
        choices=OperationType.choices,
    )
    action = models.CharField(
        verbose_name='Действие',
        max_length=16,
        choices=OperationAction.choices,
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

    # Вместо полиморфного типа, я сделал две колонки payment и order.
    # Лучше так, чем разбираться с типом ассоциированного объекта.
    # Иногда payment и order оба будут null, если это бонус

    # Платеж, который ассоциируется с этой операцией.
    # Или списание, если это возврат.
    # Может быть пустым, если операция из-за чего-то другого
    payment = models.ForeignKey(
        to='payments.Payment',
        related_name='operations',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    # Заказ, который оплатил клиент
    order = models.ForeignKey(
        to='main.Order',
        related_name='operations',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    # Бронь, которую оплатил клиент
    booking = models.ForeignKey(
        to='main.Booking',
        related_name='operations',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Операция'
        verbose_name_plural = 'Операции'

    def __str__(self) -> str:
        return f'{self.id} ${self.kind} {self.amount}'
