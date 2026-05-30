from typing import Any
import structlog
from django.conf import settings
from django.utils import timezone
from requests import post

from payments.models import (
    Payment,
    PaymentProcessingStatus,
    PaymentApiLog,
    PaymentApiLogType,
    PaymentApiLogStatus,
)
from payments.services.models.alfa_get_order_response import (
    AlfaGetOrderResponse
)
from payments.services.models.exceptions import PaymentError
from payments.services.webhook_service import confirm_payment, cancel_payment

__logger = structlog.get_logger(__name__)
__base_url: str = settings.ALFA_BASE_URL
__get_order_url: str = f'{__base_url}{settings.ALFA_REGISTER_PAYMENT}'


def __generate_get_order_params(
    order_number: str,
) -> dict[str, Any]:
    return {
        'userName': settings.ALFA_API_USERNAME,
        'password': settings.ALFA_API_PASSWORD,
        'orderNumber': order_number,
        'language': settings.ALFA_LANGUAGE,
    }


def __get_alfa_order(
    params: dict[str, Any],
) -> AlfaGetOrderResponse:
    try:
        raw_response = post(
            url=__get_order_url,
            params=params,
        )
    except Exception as api_error:
        __logger.exception(
            'Unable to get order from Alfa bank',
            url=__get_order_url,
        )
        raise PaymentError(
            'Не удалось подключиться к платежному серверу'
        ) from api_error

    try:
        json_response = raw_response.json()
    except Exception as json_error:
        __logger.exception(
            'Unable to get json data from response',
            url=__get_order_url,
            status_code=raw_response.status_code,
        )
        raise PaymentError(
            'Не удалось получить информацию о заказе с платежного сервера'
        ) from json_error

    try:
        get_order_response = AlfaGetOrderResponse.parse_obj(json_response)
    except Exception as parse_error:
        __logger.exception(
            'Unable to parse AlfaGetOrderResponse from json',
            url=__get_order_url,
            status_code=raw_response.status_code,
            data=json_response,
        )
        raise PaymentError(
            'Не удалось получить информацию о заказе с платежного сервера'
        ) from parse_error

    if (
        get_order_response.errorCode is not None and
        get_order_response.errorCode != '0'
    ):
        __logger.exception(
            'Error was received from Alfa',
            url=__get_order_url,
            error_code=get_order_response.errorCode,
            error_message=get_order_response.errorMessage,
        )
        raise PaymentError(
            'Не удалось получить информацию о заказе с платежного сервера'
        )

    return get_order_response


def __check_alfa_payment_status(payment: Payment):
    params = __generate_get_order_params(str(payment.uuid))
    api_log = PaymentApiLog.objects.create(
        type=PaymentApiLogType.API_CALL,
        status=PaymentApiLogStatus.PENDING,
        payment=payment,
        url=__get_order_url,
        request=params,
        response_status=None,
    )

    try:
        alfa_payment = __get_alfa_order(params)
        if (
            alfa_payment.orderStatus == 3 or
            alfa_payment.orderStatus == 6
        ):  # платеж отменен/отклонен
            cancel_payment(payment, api_log)
            return

        if alfa_payment.orderStatus == 4:  # платеж вернули
            payment.refunded_at = timezone.now()
            payment.processing_status = PaymentProcessingStatus.SUCCESS
            payment.save(update_fields=['refunded_at', 'processing_status'])

            api_log.status = PaymentApiLogStatus.SUCCESS
            api_log.save(update_fields=['status'])
            return

        if alfa_payment.orderStatus == 2:  # платеж прошел
            confirm_payment(payment, api_log)
            return

        api_log.status = PaymentApiLogStatus.IGNORED
        api_log.save(update_fields=['status'])
        return

    except PaymentError:
        api_log.status = PaymentApiLogStatus.FAILED
        api_log.save(update_fields=['status'])
        return


def check_payments():
    payments = Payment.objects.filter(
        processing_status=PaymentProcessingStatus.PENDING_WEBHOOK,
    ).all()
    for payment in payments:
        __check_alfa_payment_status(payment)
