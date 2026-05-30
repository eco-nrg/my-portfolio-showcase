from django.db import models


class SmsSend(models.Model):
    # Fields
    number = models.CharField(max_length=20, verbose_name='Номер телефона')
    text = models.CharField(max_length=500, verbose_name='Текст')
    JSON_result = models.TextField(verbose_name='Результат')
    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Отправка СМС'
        verbose_name_plural = 'Отправки СМС'

    def __str__(self):
        return f'#{self.id} {self.number}'
