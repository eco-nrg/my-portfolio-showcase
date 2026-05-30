from typing import Optional

import structlog
from django.http import HttpResponse, HttpResponseBadRequest
from ninja import Router

from payments.models.webhook_parameters import WebhookParameters, WebhookTypes
from payments.services.models.exceptions import PaymentWebhookError
from payments.services.webhook_service import verify_event

router = Router(tags=['paykeeper_integration'])

logger = structlog.get_logger(__name__)


@router.get(
    path='/payment_webhook',
    response=str,
)
def payment_webhook_endpoint(
    request,
    checksum: str = None,
    orderNumber: str = None,
    mdOrder: str = None,
    operation: WebhookTypes = None,
    status: int = None,
    callbackCreationDate: Optional[str] = None,
    bindingId: Optional[str] = None,
    clientId: Optional[str] = None,
    enabled: Optional[bool] = None,
    operationRefundedAmount: Optional[str] = None,
    operationRefundedAmountFormatted: Optional[str] = None,
):
    webhook_parameters = WebhookParameters(
        mdOrder=mdOrder,
        orderNumber=orderNumber,
        checksum=checksum,
        callbackCreationDate=callbackCreationDate,
        operation=operation,
        status=status,
        bindingId=bindingId,
        clientId=clientId,
        enabled=enabled,
        operationRefundedAmount=operationRefundedAmount,
        operationRefundedAmountFormatted=operationRefundedAmountFormatted,
    )

    logger.info('payment_webhook', data=webhook_parameters.dict(), request=request)

    try:
        verify_event(webhook_parameters)
    except PaymentWebhookError:
        logger.exception('Failed to process webhook')
        return HttpResponseBadRequest()

    return HttpResponse(status=200)
