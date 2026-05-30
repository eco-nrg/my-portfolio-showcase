import binascii
import os

from django.contrib.auth.models import User
from django.db import models

TOKEN_LEN = 20


class Token(models.Model):
    key = models.CharField(
        'Ключ',
        max_length=40,
        primary_key=True,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Токен'
        verbose_name_plural = 'Токены'

    def __str__(self):
        return f'{self.key} {self.user}'

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(TOKEN_LEN)).decode()


def get_user_token(user: User):
    token = Token.objects.filter(user=user, is_active=True).first()
    if token is None:
        return None
    return token.key
