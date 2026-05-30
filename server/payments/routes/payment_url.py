from http import HTTPStatus

from django.contrib.auth.models import User
from ninja import Router
from ninja.errors import HttpError

from account.auth.bearer_token import AuthBearerUser
from payments.services.models.exceptions import PaymentError
from payments.schemas import PaymentLinkRequest, PaymentLinkResponse
from payments.services.payments_service import create_payment_link

router = Router(tags=['payments'])


@router.post(
    path='/payment_url',
    response=PaymentLinkResponse,
    auth=AuthBearerUser(),
)
def payment_url_endpoint(
    request,
    body: PaymentLinkRequest,
) -> PaymentLinkResponse:
    user: User = request.auth

    try:
        return PaymentLinkResponse(
            url=create_payment_link(user, body.amount, body.type),
        )
    except PaymentError as payment_err:
        raise HttpError(
            HTTPStatus.BAD_REQUEST,
            payment_err.msg,
        ) from payment_err
    except Exception as err:
        raise HttpError(
            HTTPStatus.BAD_REQUEST,
            'Что-то пошло не так. Попробуйте повторить операцию позже',
        ) from err
