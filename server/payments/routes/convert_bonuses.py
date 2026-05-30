from http import HTTPStatus

from django.contrib.auth.models import User
from ninja import Router
from ninja.errors import HttpError

from account.auth.bearer_token import AuthBearerUser
from chat.event import send_phone_auth_response
from payments.bonus import (
    BonusError,
    ConvertBonusesRequest,
    ConvertBonusesResponse,
    convert_bonuses,
)

router = Router(tags=['payments'])


@router.post(
    path='/convert_bonuses',
    response=ConvertBonusesResponse,
    auth=AuthBearerUser(),
)
def convert_bonuses_endpoint(
    request,
    body: ConvertBonusesRequest,
) -> ConvertBonusesResponse:
    user: User = request.auth

    try:
        balance_res = convert_bonuses(user, body)
    except BonusError as err:
        raise HttpError(HTTPStatus.BAD_REQUEST, err.msg) from err

    send_phone_auth_response(user, user)

    return balance_res
