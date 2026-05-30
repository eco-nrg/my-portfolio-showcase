from http import HTTPStatus
from typing import Optional, TypedDict

from django.contrib.auth.models import User
from pydantic import BaseModel

from account.reset_code_helper import reset_user_code
from main.phone_number import check_number
from main.sms import send_sms
from payments.bonus import add_fixed_bonus_singleton
from payments.models import BonusSource


class SignupResponse(BaseModel):
    new_user: bool
    code: int  # 200 or 400 TODO: we dont need codes here...
    detail: str


class SignupParams(TypedDict):
    phone: Optional[str]


def signup(data: SignupParams) -> SignupResponse:
    phone = data.get('phone')
    err = check_number(phone)
    if err is not None:
        return SignupResponse(
            new_user=True,
            code=HTTPStatus.BAD_REQUEST,
            detail=err,
        )

    user = User.objects.filter(username=phone).first()
    if user is None:
        user = User.objects.create(username=phone)

        add_fixed_bonus_singleton(BonusSource.SIGN_UP, user)

        code = reset_user_code(user)

        text = f'Код для входа: {code}'

        send_sms(text, phone)
        return SignupResponse(
            new_user=True,
            code=HTTPStatus.OK,
            detail='СМС успешно отправлено',
        )

    return SignupResponse(new_user=False, code=HTTPStatus.OK, detail='')
