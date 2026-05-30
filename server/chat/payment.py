from enum import Enum
from typing import List

import structlog
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, Paginator
from ninja import Schema
from pydantic import BaseModel, Field, PositiveFloat

from chat.orders_history import _format_db_time
from payments.models.payment import Payment, PaymentStatus

logger = structlog.get_logger(__name__)

class PaymentSuccessResponse(Schema):
    uuid: str
    pay_amount: PositiveFloat
    status: PaymentStatus

class OrderEnum(str, Enum):
    desc = 'desc'
    asc = 'asc'


class GetPaymentsParams(BaseModel):
    page_number: int = Field(
        default=1,
        ge=1,
    )
    page_size: int = Field(default=100, ge=1, le=1000)
    order_direction: OrderEnum = OrderEnum.desc


class PaymentHistoryView(BaseModel):
    uuid: str
    cost_total: float
    created_at: int
    status: str


class PaymentsHistory(BaseModel):
    data: List[PaymentHistoryView]


def present_payment_history(payment: Payment) -> PaymentHistoryView:
    return PaymentHistoryView(
        uuid=str(payment.uuid),
        cost_total=float(payment.pay_amount),
        created_at=_format_db_time(payment.created_at),
        status=payment.status,
    )


def get_payments_of_user(
    user: User,
    params: GetPaymentsParams,
) -> PaymentsHistory:
    payments = Payment.objects.filter(
        user=user,
    )

    if params.order_direction == 'asc':
        payments = payments.order_by('created_at')
    else:
        payments = payments.order_by('-created_at')

    paginator = Paginator(payments, params.page_size)

    try:
        payments = paginator.page(params.page_number)
    except EmptyPage:
        payments = []

    return PaymentsHistory(
        data=[present_payment_history(payment) for payment in payments],
    )
