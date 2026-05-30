"""
Модель платежа.

Оплата производится посредством генерации платежных ссылок
и оплате по ним пользователем на строне платежного сервера. При создании ссылки
в платежный сервер передается id Payment объекта в нашей БД.

С нашей стороны работы с настоящими деньгами не происходит, вместо этого
в системе есть "баланс" пользователя, который пополняется при получении
уведомления от платежного сервера об успешной оплате (вебхук). Или спустя какое-то вермя
с помощью cron-задачи.

Это уведомление содержит id Payment объекта в нашей БД, что позволяет
пополнить боланс корректной суммой и изменить статус платежа.
"""
import enum
import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class PaymentStatus(str, enum.Enum):
    # платеж инициализирован, но еще не оплачен пользователем
    PENDING = 'PENDING'

    # платеж оплачен
    PAID = 'PAID'

    # платеж отменен, как правило если прошло много времени
    CANCELED = 'CANCELED'

    # сделан возврат денежных средств пользователем,
    # на данный момент это не возможно, может потребоваться в будущем
    REFUNDED = 'REFUNDED'


class PaymentProcessingStatus(models.TextChoices):
    # Поступил запрос на оплату от клиента
    CREATED = 'CREATED', _('Создан')

    # Ждем создания платежной ссылки
    PENDING_LINK = 'PENDING_LINK', _('Ожидание ссылки')

    # Ждем подтверждения оплаты
    PENDING_WEBHOOK = 'PENDING_WEBHOOK', _('Ожидание вебхука')

    # Успешно получили вебхук
    SUCCESS = 'SUCCESS', _('Успех')

    # Платеж не состоялся
    CANCELLED = 'CANCELLED', _('Отменен')

    # АПИ создания ссылки ответило ошибкой
    FAILED_LINK = 'FAILED_LINK', _('Ошибка получения ссылки')

    # Вебхук пришел, но в процессе обработки возникла ошибка
    FAILED_WEBHOOK = 'FAILED_WEBHOOK', _('Ошибка вебхука')

    # Ошибка
    FAILED = 'FAILED', _('Ошибка')


class Payment(models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

    # Relationship Fields
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        related_name='payments',
        verbose_name='Пользователь',
    )

    # Fields
    invoice_id = models.CharField(
        blank=True,
        default='',
        max_length=50,
        verbose_name='ID счета в платежном сервере',
    )
    invoice_url = models.CharField(
        blank=True,
        default='',
        max_length=255,
        verbose_name='URL для оплаты',
    )
    pay_amount = models.DecimalField(
        'Размер платежа',
        default=Decimal(0),
        max_digits=19,
        decimal_places=2,
    )
    processing_status = models.CharField(
        max_length=20,
        choices=PaymentProcessingStatus.choices,
        verbose_name='Статус',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время создания',
    )
    expire_at = models.DateTimeField(
        verbose_name='Дата просрочивания',
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Время активации',
    )
    canceled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Время отмены',
    )
    refunded_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Время возврата денег',
    )

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'

    def __str__(self) -> str:
        return f'{self.invoice_id} {self.pay_amount}'

    @property
    def status(self) -> PaymentStatus:
        # TODO: проверить дату просрочки платежа
        if self.refunded_at is not None:
            return PaymentStatus.REFUNDED
        if self.paid_at is not None:
            return PaymentStatus.PAID
        if self.canceled_at is not None:
            return PaymentStatus.CANCELED
        if timezone.now() > self.expire_at:
            return PaymentStatus.CANCELED
        return PaymentStatus.PENDING

    @property
    def is_closed(self):
        return self.status != PaymentStatus.PENDING
