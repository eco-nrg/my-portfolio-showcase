import hashlib
import hmac

import structlog
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from chat.event import send_phone_auth_response
from chat.event.payment import send_payment_response
from payments.models import PaymentApiLog, Payment, PaymentApiLogType, PaymentApiLogStatus, \
    PaymentProcessingStatus, Operation, OperationType, OperationAction
from payments.models.webhook_parameters import WebhookParameters, WebhookTypes
from payments.services.models.exceptions import PaymentWebhookError

__logger = structlog.get_logger(__name__)
__webhook_secret_key: str = settings.ALFA_WEBHOOK_SECRET_KEY


def __webhook_parameters_to_verify_string(webhook_parameters: WebhookParameters) -> str:
    res = ''
    if webhook_parameters.bindingId is not None:
        res += f'bindingId;{webhook_parameters.bindingId};'

    if webhook_parameters.callbackCreationDate is not None:
        res += f'callbackCreationDate;{webhook_parameters.callbackCreationDate};'

    if webhook_parameters.clientId is not None:
        res += f'clientId;{webhook_parameters.clientId};'

    if webhook_parameters.enabled is not None:
        res += f'enabled;{webhook_parameters.enabled};'

    res += (f'mdOrder;{webhook_parameters.mdOrder};'
            f'operation;{webhook_parameters.operation.value};')

    if webhook_parameters.operationRefundedAmount is not None:
        res += f'operationRefundedAmount;{webhook_parameters.operationRefundedAmount};'

    if webhook_parameters.operationRefundedAmountFormatted is not None:
        res += f'operationRefundedAmountFormatted;{webhook_parameters.operationRefundedAmountFormatted};'

    res += (f'orderNumber;{webhook_parameters.orderNumber};'
            f'status;{webhook_parameters.status};')

    return res


def __calculate_checksum(message: str) -> str:
    return hmac.new(
        key=__webhook_secret_key.encode('utf-8'),
        msg=message.encode('utf-8'),
        digestmod=hashlib.sha256,
    ).hexdigest().upper()


@transaction.atomic
def confirm_payment(payment: Payment, api_log: PaymentApiLog):
    payment.paid_at = timezone.now()
    payment.processing_status = PaymentProcessingStatus.SUCCESS
    payment.save(update_fields=['paid_at', 'processing_status'])

    Operation.objects.create(
        kind=OperationType.DEBIT,
        action=OperationAction.PAYMENT,
        amount=payment.pay_amount,
        created_at=payment.paid_at,
        user=payment.user,
        payment=payment,
    )

    api_log.status = PaymentApiLogStatus.SUCCESS
    api_log.save(update_fields=['status'])


@transaction.atomic
def cancel_payment(payment: Payment, api_log: PaymentApiLog):
    payment.canceled_at = timezone.now()
    payment.processing_status = PaymentProcessingStatus.CANCELLED
    payment.save(update_fields=['canceled_at', 'processing_status'])

    api_log.status = PaymentApiLogStatus.SUCCESS
    api_log.save(update_fields=['status'])


@transaction.atomic
def __failed_payment(payment: Payment, api_log: PaymentApiLog):
    payment.canceled_at = timezone.now()
    payment.processing_status = PaymentProcessingStatus.FAILED
    payment.save(update_fields=['canceled_at', 'processing_status'])

    api_log.status = PaymentApiLogStatus.SUCCESS
    api_log.save(update_fields=['status'])


def __handle_deposited(
    webhook_parameters: WebhookParameters,
    payment: Payment,
    api_log: PaymentApiLog,
):
    if webhook_parameters.status == 0:
        __failed_payment(payment, api_log)
        __logger.info(
            'Operation failed',
            parameters=webhook_parameters.dict(),
        )
        return

    if webhook_parameters.status == 1:
        confirm_payment(payment, api_log)
        __logger.info(
            'Successfully paid for transaction',
            **webhook_parameters.dict(),
        )
        user = payment.user
        send_phone_auth_response(user, user)
        send_payment_response(user, payment)
        return


def __handle_decline_by_timeout(
    webhook_parameters: WebhookParameters,
    payment: Payment,
    api_log: PaymentApiLog,
):
    cancel_payment(payment, api_log)
    __logger.info(
        'Operation was declined by timeout',
        parameters=webhook_parameters.dict(),
    )
    return


def verify_event(webhook_parameters: WebhookParameters):
    api_log = PaymentApiLog.objects.create(
        type=PaymentApiLogType.WEBHOOK,
        status=PaymentApiLogStatus.PENDING,
        request=webhook_parameters.dict(),
        response_status=None,
    )

    __logger.info(
        'Start processing payment webhook',
        **webhook_parameters.dict(),
    )

    if (
        webhook_parameters.operation != WebhookTypes.deposited and
        webhook_parameters.operation != WebhookTypes.declinedByTimeout
    ):
        api_log.status = PaymentApiLogStatus.IGNORED
        api_log.save(update_fields=['status'])
        return

    parameters_str = __webhook_parameters_to_verify_string(webhook_parameters)
    checksum = __calculate_checksum(parameters_str)

    if checksum != webhook_parameters.checksum:
        __logger.warn(
            'Check sum doesn\'t match',
            parameters=webhook_parameters.dict(),
            checksum=checksum,
        )
        api_log.status = PaymentApiLogStatus.FAILED
        api_log.save(update_fields=['status'])
        raise PaymentWebhookError('Check sum doesn\'t match')

    try:
        payment = Payment.objects.get(uuid=webhook_parameters.orderNumber)
    except Payment.DoesNotExist as not_found_err:
        __logger.warn(
            'Transaction not found',
            transaction_id=webhook_parameters.orderNumber,
        )
        api_log.status = PaymentApiLogStatus.FAILED
        api_log.save(update_fields=['status'])
        raise PaymentWebhookError(
            'Transaction not found',
        ) from not_found_err

    api_log.payment = payment
    api_log.save(update_fields=['payment'])

    if payment.is_closed:
        __logger.warn(
            'Ignore payment_webhook: payment already finished',
            remote_id=webhook_parameters.mdOrder,
            transaction_id=webhook_parameters.orderNumber,
            payment_status=payment.status,
            client_id=webhook_parameters.clientId,
        )
        api_log.status = PaymentApiLogStatus.IGNORED
        api_log.save(update_fields=['status'])
        return

    if webhook_parameters.operation == WebhookTypes.deposited:
        __handle_deposited(webhook_parameters, payment, api_log)
        return

    if webhook_parameters.operation == WebhookTypes.declinedByTimeout:
        __handle_decline_by_timeout(webhook_parameters, payment, api_log)
        return
