from datetime import timedelta

import structlog
from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from pydantic import PositiveFloat
from requests import post

from payments.schemas import PaymentLinkType
from payments.services.models.alfa_get_sbp_link_response import AlfaGetSbpLinkResponse
from payments.services.models.exceptions import PaymentError
from payments.models import (Payment, PaymentProcessingStatus, PaymentStatus, Operation, OperationType,
                             OperationAction, PaymentApiLog, PaymentApiLogType, PaymentApiLogStatus)
from payments.services.models.alfa_register_order_response import AlfaRegisterOrderResponse

__logger = structlog.get_logger(__name__)
__base_url: str = settings.ALFA_BASE_URL
__register_order_url: str = f'{__base_url}{settings.ALFA_REGISTER_PAYMENT}'
__get_sbp_link_url: str = f'{__base_url}{settings.ALFA_GET_SBP_LINK}'
__order_ttl: timedelta = timedelta(days=2)
__minimum_payment = settings.MINIMUM_PAYMENT
__maximum_payment = settings.MAXIMUM_PAYMENT
__card_commission = settings.CARD_COMMISSION
__return_url = f"{settings.FRONTEND_BASE_URL}{settings.ALFA_RETURN_URL}"
__fail_url = f"{settings.FRONTEND_BASE_URL}{settings.ALFA_FAIL_URL}"


def __generate_register_order_params(
    order_number: str,
    email: str,
    amount: PositiveFloat,
) -> dict[str, any]:
    return {
        'userName': settings.ALFA_API_USERNAME,
        'password': settings.ALFA_API_PASSWORD,
        'orderNumber': order_number,
        'amount': int(amount * 100),
        'currency': settings.CURRENCY,
        'language': settings.ALFA_LANGUAGE,
        'returnUrl': __return_url,
        'failUrl': __fail_url,
        'email': email,
        'sessionTimeoutSecs': __order_ttl.seconds,
    }


def __register_order(
    params: dict[str, any],
) -> AlfaRegisterOrderResponse:
    try:
        raw_response = post(
            url=__register_order_url,
            params=params,
        )
    except Exception as api_err:
        __logger.exception(
            'Unable to register order in Alfa bank',
            url=__register_order_url,
        )
        raise PaymentError(
            'Не удалось подключиться к платежному серверу',
        ) from api_err

    try:
        json_response = raw_response.json()
    except Exception as read_err:
        __logger.exception(
            'Unable to get json data from response',
            url=__register_order_url,
            status_code=raw_response.status_code,
        )
        raise PaymentError(
            'Не удалось получить информацию о заказе с платежного сервера'
        ) from read_err

    try:
        register_order_response = AlfaRegisterOrderResponse.parse_obj(json_response)
    except Exception as parse_err:
        __logger.exception(
            'Unable to parse AlfaRegisterOrderResponse from json',
            url=__register_order_url,
            status_code=raw_response.status_code,
            data=json_response,
        )
        raise PaymentError(
            'Не удалось получить информацию о заказе с платежного сервера'
        ) from parse_err

    if (register_order_response.errorCode is not None and
        register_order_response.errorCode != '0'):
        __logger.exception(
            'Error was received from Alfa',
            url=__register_order_url,
            error_code=register_order_response.errorCode,
            error_message=register_order_response.errorMessage,
        )

        raise PaymentError(
            'Не удалось получить информацию о заказе с платежного сервера'
        )

    if register_order_response.formUrl is None or register_order_response.orderId is None:
        __logger.exception(
            'Invalid response received from Alfa',
            url=__register_order_url,
            error_code=register_order_response.errorCode,
            error_message=register_order_response.errorMessage,
        )

        raise PaymentError(
            'Неправильный формат ответа от платежного сервера'
        )

    return register_order_response


def __generate_get_sbp_link_params(
    order_id: str
) -> dict[str, any]:
    return {
        'userName': settings.ALFA_API_USERNAME,
        'password': settings.ALFA_API_PASSWORD,
        'mdOrder': order_id,
    }


def __get_sbp_link(
    params: dict[str, any],
) -> AlfaGetSbpLinkResponse:
    try:
        raw_response = post(
            url=__get_sbp_link_url,
            params=params,
        )
    except Exception as api_err:
        __logger.exception(
            'Unable to get SBP QR-code',
            url=__get_sbp_link_url,
        )
        raise PaymentError(
            'Не удалось получить зарегестрированный в СБП QR-код',
        ) from api_err

    try:
        json_response = raw_response.json()
    except Exception as read_err:
        __logger.exception(
            'Unable to get json data from response',
            url=__get_sbp_link_url,
            status_code=raw_response.status_code,
        )
        raise PaymentError(
            'Не удалось получить зарегестрированный в СБП QR-код',
        ) from read_err

    try:
        get_sbp_link_response = AlfaGetSbpLinkResponse.parse_obj(json_response)
    except Exception as parse_err:
        __logger.exception(
            'Unable to parse AlfaGetSbpLinkResponse from json',
            url=__get_sbp_link_url,
            status_code=raw_response.status_code,
            data=json_response,
        )
        raise PaymentError(
            'Не удалось получить зарегестрированный в СБП QR-код',
        ) from parse_err

    if (get_sbp_link_response.errorCode is not None and
        get_sbp_link_response.errorCode != '0'):
        __logger.exception(
            'Error was received from Alfa',
            url=__get_sbp_link_url,
            error_code=get_sbp_link_response.errorCode,
            error_message=get_sbp_link_response.errorMessage,
        )

        raise PaymentError(
            'Не удалось получить зарегестрированный в СБП QR-код',
        )

    if get_sbp_link_response.payload is None:
        __logger.exception(
            'Invalid response received from Alfa',
            url=__get_sbp_link_url,
            error_code=get_sbp_link_response.errorCode,
            error_message=get_sbp_link_response.errorMessage,
        )

        raise PaymentError(
            'Неправильный формат ответа от платежного сервера'
        )

    return get_sbp_link_response


def __validate_pay_amount(
    pay_amount: PositiveFloat,
):
    if pay_amount < __minimum_payment:
        raise PaymentError('Сумма платежа меньше минимальной')
    if pay_amount > __maximum_payment:
        raise PaymentError('Сумма платежа больше максимальной')


def create_payment_link(
    user: User,
    pay_amount: PositiveFloat,
    payment_link_type: PaymentLinkType,
):
    __validate_pay_amount(pay_amount)
    payment_expire_date = timezone.now() + __order_ttl

    # Сохраняем платеж до указания всех полей, чтобы получить id,
    # который затем передадим в запросе к Альфе
    payment = Payment.objects.create(
        user=user,
        pay_amount=pay_amount,
        created_at=timezone.now(),
        expire_at=payment_expire_date,
        processing_status=PaymentProcessingStatus.CREATED,
    )

    # Генерируем query параметры для запроса
    if payment_link_type == PaymentLinkType.sbp:
        params = __generate_register_order_params(
            payment.uuid,
            f'{user.profile.email}',
            pay_amount,
        )
    else:
        params = __generate_register_order_params(
            payment.uuid,
            f'{user.profile.email}',
            __card_commission * pay_amount,
        )

    # Формируем запись-лог в БД
    api_log_payment = PaymentApiLog.objects.create(
        type=PaymentApiLogType.API_CALL,
        status=PaymentApiLogStatus.PENDING,
        url=__register_order_url,
        request=params,
        created_at=timezone.now(),
        payment=payment,
    )

    # Меняем статус на ожидаем ссылку.
    # В данной реализации это излишне, осталось от PayKeeper
    payment.processing_status = PaymentProcessingStatus.PENDING_LINK
    payment.save(update_fields=['processing_status'])

    try:
        # Регистрируем заказ в системе Альфа банка.
        # Получаем или успешный ответ с ссылкой.
        # Или ошибку
        register_order = __register_order(
            params,
        )
    except Exception as register_error:
        # В случае ошибки записываем её в логи.
        # И меняем статус платежа на неудалось получить ссылку
        api_log_payment.status = PaymentApiLogStatus.FAILED
        api_log_payment.save(update_fields=['status'])
        payment.processing_status = PaymentProcessingStatus.FAILED_LINK
        payment.save(update_fields=['processing_status'])
        raise register_error

    # Если все хорошо, то записываем ответ в логи
    api_log_payment.response = register_order.dict()
    api_log_payment.status = PaymentApiLogStatus.SUCCESS
    api_log_payment.save(update_fields=['response', 'status'])

    # Запоминаем внутренний номер заказа и ссылку.
    # Меняем статус на ожидаем ответ от вебхука
    payment.invoice_id = register_order.orderId
    payment.invoice_url = register_order.formUrl
    payment.processing_status = PaymentProcessingStatus.PENDING_WEBHOOK
    payment.save(
        update_fields=['invoice_id', 'invoice_url', 'processing_status'],
    )

    if payment_link_type == PaymentLinkType.sbp:
        get_sbp_link_params = __generate_get_sbp_link_params(register_order.orderId)
        api_log_sbp = PaymentApiLog.objects.create(
            type=PaymentApiLogType.API_CALL,
            status=PaymentApiLogStatus.PENDING,
            url=__get_sbp_link_url,
            request=get_sbp_link_params,
            created_at=timezone.now(),
            payment=payment,
        )
        try:
            get_sbp_link_response = __get_sbp_link(get_sbp_link_params)
        except Exception as get_sbp_link_error:
            api_log_sbp.status = PaymentApiLogStatus.FAILED
            api_log_sbp.save(update_fields=['status'])
            payment.processing_status = PaymentProcessingStatus.FAILED_LINK
            payment.save(update_fields=['processing_status'])
            raise get_sbp_link_error

        # Если все хорошо, то записываем ответ в логи
        api_log_sbp.response = get_sbp_link_response.dict()
        api_log_sbp.status = PaymentApiLogStatus.SUCCESS
        api_log_sbp.save(update_fields=['response', 'status'])
        # Запоминаем внутренний номер заказа и ссылку.
        # Меняем статус на ожидаем ответ от вебхука
        payment.invoice_url = get_sbp_link_response.payload
        payment.save(
            update_fields=['invoice_url'],
        )

    return payment.invoice_url


@transaction.atomic
def full_refund_operation(payment: Payment):
    if payment.status == PaymentStatus.PAID:
        payment.refunded_at = timezone.now()
        payment.save()
        Operation.objects.create(
            user=payment.user,
            kind=OperationType.CREDIT,
            action=OperationAction.REFUND,
            amount=payment.pay_amount,
            payment=payment,
        )
    else:
        raise PaymentError(
            'Платеж не находится в статусе "Оплачен"',
        )
