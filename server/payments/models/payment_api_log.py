from django.db import models
from django.utils.translation import gettext_lazy as _

from payments.models.payment import Payment


class PaymentApiLogType(models.TextChoices):
    # Запрос с нашего сервера к платежному серверу
    API_CALL = 'API_CALL', _('API запрос')

    # Запрос с платежного сервера на наш сервер
    WEBHOOK = 'WEBHOOK', _('Вебхук')


class PaymentApiLogStatus(models.TextChoices):
    # Запрос обрабатывается
    PENDING = 'PENDING', _('Обрабатывается')

    # Успех
    SUCCESS = 'SUCCESS', _('Успех')

    # Ошибка в ходе обработки
    FAILED = 'FAILED', _('Ошибка')

    # В случае вебхука означает, что пришло повторное уведомление об оплате,
    # а сервер его проигнорировал
    IGNORED = 'IGNORED', _('Проигнорирован')


class PaymentApiLog(models.Model):
    # Relationship Fields
    payment = models.ForeignKey(
        Payment,
        verbose_name='Платеж',
        on_delete=models.DO_NOTHING,
        related_name='logs',
        null=True,
    )

    # Fields
    type = models.CharField(
        max_length=25,
        choices=PaymentApiLogType.choices,
        verbose_name='Тип',
    )
    status = models.CharField(
        max_length=25,
        choices=PaymentApiLogStatus.choices,
        verbose_name='Статус запроса',
    )
    url = models.CharField(
        max_length=255,
        verbose_name='URL запроса к платежному серверу',
        blank=True,
        default='',
    )
    request = models.TextField(
        verbose_name='Тело запроса к платежному серверу',
        blank=True,
    )
    response = models.TextField(
        verbose_name='Тело ответа от платежного сервера',
        blank=True,
    )
    response_status = models.IntegerField(
        verbose_name='Статус ответа от платежного сервера',
        null=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время создания',
    )

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'API лог платежей'
        verbose_name_plural = 'API лог платежей'

    def __str__(self) -> str:
        return f'{self.id} {self.type} ${self.status}'
