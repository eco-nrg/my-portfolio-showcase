from django.conf import settings
from django.db import models


class Connection(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='connections',
        blank=True,
        null=True,
        verbose_name='Пользователь',
    )
    channel_name = models.CharField('Канал', max_length=255)
    created_at = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Соединение'
        verbose_name_plural = 'Соединения'

    def __str__(self) -> str:
        return self.channel_name
