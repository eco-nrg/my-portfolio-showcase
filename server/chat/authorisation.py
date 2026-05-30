from typing import Optional

from django.contrib.auth import authenticate
from django.contrib.auth.models import User


class AuthError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__()
        self.msg = msg


def auth_user_by_code(phone: Optional[str], code: Optional[str]) -> User:
    if not phone or not code:
        raise AuthError('Должен включать "Логин" и "Пароль".')

    user = authenticate(username=phone, password=code)

    if not user:
        raise AuthError('Невозможно войти с предоставленными данными.')

    if not user.is_active:
        raise AuthError('Аккаунт не активен.')

    return user
