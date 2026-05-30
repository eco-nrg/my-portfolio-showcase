import secrets
import string

from django.contrib.auth.models import User
from django.utils import timezone


def gen_code(length=6):
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def reset_user_code(user: User) -> str:
    code = gen_code()

    user.set_password(code)
    user.save()

    user.profile.code = code
    user.profile.last_code_sent = timezone.now()
    user.profile.save(update_fields=['code', 'last_code_sent'])

    return code
