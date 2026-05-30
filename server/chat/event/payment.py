from typing import Optional, Union

from django.contrib.auth.models import User

from chat.event.helpers import send_to
from chat.no_error import no_error
from chat.payment import GetPaymentsParams, OrderEnum, PaymentSuccessResponse, get_payments_of_user
from payments.bonus import ConvertBonusesResponse
from payments.models.payment import Payment
from payments.schemas import PaymentLinkResponse


@no_error
def send_payment_url(target: Union[str, User], payment_url: str):
    msg = {
        'type': 'payment_url_response',
        'data': PaymentLinkResponse(url=payment_url).dict(),
    }
    send_to(target, msg)


@no_error
def send_convert_bonuses_response(
    target: Union[str, User],
    response: ConvertBonusesResponse,
):
    msg = {
        'type': 'convert_bonuses_response',
        'data': response.dict(),
    }
    send_to(target, msg)


@no_error
def send_payments(
    target: Union[str, User],
    user: User,
    request: Optional[GetPaymentsParams] = None,
):
    if request is None:
        request = GetPaymentsParams(
            page_number=1,
            page_size=10,
            order_direction=OrderEnum.desc,
        )
    payments = get_payments_of_user(user, request)
    msg = {
        'type': 'get_payments_response',
        'data': payments.dict()['data'],
    }
    send_to(target, msg)


@no_error
def send_payment_response(
    target: User,
    payment: Payment,
):
    response = PaymentSuccessResponse(
        uuid=str(payment.uuid),
        pay_amount=payment.pay_amount,
        status=payment.status,
    )
    msg = {
        'type': 'payment_response',
        'data': response.dict(),
    }
    send_to(target, msg)
