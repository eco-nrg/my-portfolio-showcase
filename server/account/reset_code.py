import datetime
from typing import Optional, TypedDict

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from pydantic import BaseModel

from account.reset_code_helper import reset_user_code
from main.phone_number import check_number
from main.sms import send_sms

# клиент ждет 60 секунд. Сервер пусть ждет чуть по меньше на всякий случай,
# чтобы если клиент отправил раньше запрос н адолю секунды, то он не увидел ошибку
SEND_CODE_TIMEOUT = datetime.timedelta(seconds=55)


class ResetCodeError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__()
        self.msg = msg


class ResetCodeResponse(BaseModel):
    success: bool
    message: str


class ResetCodeParams(TypedDict):
    phone: Optional[str]


@transaction.atomic
def reset_code(data: ResetCodeParams) -> ResetCodeResponse:
    phone = data.get('phone')

    err = check_number(phone)
    if err is not None:
        raise ResetCodeError(msg=err)

    try:
        user = User.objects.get(username=phone)
    except User.DoesNotExist as find_err:
        raise ResetCodeError(
            msg='Нет пользователя с таким номером телефона',
        ) from find_err
        # TODO: нельзя отправлять информацию, что юзера нет.
        # Это раскрывает информацию о существовании юзеров!
        # Но я оставил как было пока что для совместимости

    dt = timezone.now() - user.profile.last_code_sent
    if dt < SEND_CODE_TIMEOUT:
        raise ResetCodeError(
            msg='Слишком частая отправка. Попробуйте позже',
        )

    code = reset_user_code(user)

    text = f'Код для входа: {code}'

    send_sms(text, phone)

    return ResetCodeResponse(
        success=True,
        message='СМС отправлено',
    )
