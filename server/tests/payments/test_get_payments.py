from decimal import Decimal

import pytest
import responses
import structlog
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.conf import settings
from django.contrib.auth.models import User
from pydantic import PositiveFloat

from chat.payment import (
    GetPaymentsParams,
    OrderEnum,
    PaymentHistoryView,
    PaymentsHistory,
    get_payments_of_user,
)
from payments.models import Operation, Payment, PaymentStatus
from payments.models.webhook_parameters import WebhookParameters, WebhookTypes
from payments.services.payments_service import create_payment_link, full_refund_operation
from payments.services.webhook_service import __webhook_parameters_to_verify_string, __calculate_checksum, verify_event

from tests.helpers import SuperDict

logger = structlog.get_logger(__name__)
__base_url = settings.ALFA_BASE_URL
__register_order_url = f'{__base_url}{settings.ALFA_REGISTER_PAYMENT}'


@responses.activate
@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
async def test_get_payments_of_user__when_user_has_five_paymets__should_return_all_using_pagination(
    ws: WebsocketCommunicator,
):
    # Validate that user doesn't have any payments
    await ws.send_json_to(
        {
            'type': 'get_payments',
            'data': {
                'page_number': 1,
                'page_size': 3,
                'order_direction': 'desc',
            },
        },
    )

    resp = SuperDict(await ws.receive_json_from())
    await ws.receive_nothing()

    assert resp['data'] == []

    # Mock rquest to Alfa bank
    responses.add(
        responses.POST,
        url=__register_order_url,
        json={
            'formUrl': 'test_url',
            'orderId': 'test_id',
            'errorCode': '0'
        },
        status=200,
    )

    # Create payment 5 payments
    amount_to_pays = [100.55, 200.55, 400.55, 500.55, 600.55]
    for amount_to_pay in amount_to_pays:
        await ws.send_json_to(
            {
                'type': 'create_payment_url',
                'data': {
                    'amount': amount_to_pay,
                },
            },
        )

        resp = SuperDict(await ws.receive_json_from())
        await ws.receive_nothing()

        assert resp['type'] == 'payment_url_response'
        assert resp['data.url'] == 'mock_url'

        payment: Payment = await database_sync_to_async(
            lambda: Payment.objects.first(),
        )()

        webhook_params = WebhookParameters(
            mdOrder='1',
            orderNumber=str(payment.uuid),
            callbackCreationDate='2023-12-12',
            operation=WebhookTypes.deposited,
            status=1,
        )
        check_sum_str = __webhook_parameters_to_verify_string(webhook_params)
        webhook_params.checkSum = __calculate_checksum(check_sum_str)
        await database_sync_to_async(verify_event)(webhook_params)

        phone_auth = SuperDict(await ws.receive_json_from())
        paym_resp = SuperDict(await ws.receive_json_from())

        await ws.receive_nothing()
        assert phone_auth['type'] == 'phone_auth_response'

        assert paym_resp['type'] == 'payment_response'
        assert paym_resp['data.uuid'] == str(payment.uuid)
        assert paym_resp['data.status'] == PaymentStatus.PAID
        assert paym_resp['data.pay_amount'] == PositiveFloat(amount_to_pay)

        operation: Operation = await database_sync_to_async(
            lambda: Operation.objects.first(),
        )()
        assert operation is not None
        assert operation.amount == Decimal(str(amount_to_pay))

        # TODO: переписать этот цикл так как operation не копируется
        operation_payment: Payment = await database_sync_to_async(
            lambda: operation.payment,
        )()
        assert operation_payment == payment
        assert operation_payment.pay_amount == Decimal(str(amount_to_pay))

    await ws.send_json_to(
        {
            'type': 'get_payments',
            'data': {
                'page_number': 1,
                'page_size': 3,
                'order_direction': 'desc',
            },
        },
    )

    resp = SuperDict(await ws.receive_json_from())
    await ws.receive_nothing()

    assert resp['type'] == 'get_payments_response'
    assert len(resp['data']) == 3

    # Validate that user gets 2 more payments
    await ws.send_json_to(
        {
            'type': 'get_payments',
            'data': {
                'page_number': 2,
                'page_size': 3,
                'order_direction': 'desc',
            },
        },
    )

    resp = SuperDict(await ws.receive_json_from())
    await ws.receive_nothing()

    assert resp['type'] == 'get_payments_response'
    assert len(resp['data']) == 2


@responses.activate
@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
async def test_get_payments_of_user__when_user_one_payment__should_return_one_payment_and_then_empty_list(
    ws: WebsocketCommunicator,
):
    # Validate that user doesn't have any payments
    await ws.send_json_to(
        {
            'type': 'get_payments',
            'data': {
                'page_number': 1,
                'page_size': 1,
                'order_direction': 'desc',
            },
        },
    )

    resp = SuperDict(await ws.receive_json_from())
    await ws.receive_nothing()

    assert resp['data'] == []

    # Mock rquest to Alfa bank
    responses.add(
        responses.POST,
        url=__register_order_url,
        json={
            'formUrl': 'test_url',
            'orderId': 'test_id',
            'errorCode': '0'
        },
        status=200,
    )

    amount_to_pay = 100.55

    await ws.send_json_to(
        {
            'type': 'create_payment_url',
            'data': {
                'amount': amount_to_pay,
            },
        },
    )

    resp = SuperDict(await ws.receive_json_from())
    await ws.receive_nothing()

    assert resp['type'] == 'payment_url_response'
    assert resp['data.url'] == 'mock_url'

    payment: Payment = await database_sync_to_async(
        lambda: Payment.objects.first(),
    )()

    webhook_params = WebhookParameters(
        mdOrder='1',
        orderNumber=str(payment.uuid),
        callbackCreationDate='2023-12-12',
        operation=WebhookTypes.deposited,
        status=1,
    )
    check_sum_str = __webhook_parameters_to_verify_string(webhook_params)
    webhook_params.checkSum = __calculate_checksum(check_sum_str)
    await database_sync_to_async(verify_event)(webhook_params)

    phone_auth = SuperDict(await ws.receive_json_from())
    paym_resp = SuperDict(await ws.receive_json_from())

    await ws.receive_nothing()
    assert phone_auth['type'] == 'phone_auth_response'

    assert paym_resp['type'] == 'payment_response'
    assert paym_resp['data.uuid'] == str(payment.uuid)
    assert paym_resp['data.status'] == PaymentStatus.PAID
    assert paym_resp['data.pay_amount'] == PositiveFloat(payment.pay_amount)

    operation: Operation = await database_sync_to_async(
        lambda: Operation.objects.first(),
    )()
    assert operation is not None
    assert operation.amount == Decimal(str(amount_to_pay))

    operation_payment: Payment = await database_sync_to_async(
        lambda: operation.payment,
    )()
    assert operation_payment == payment
    assert operation_payment.pay_amount == Decimal(str(amount_to_pay))

    # Validate that user gets last payments
    await ws.send_json_to(
        {
            'type': 'get_payments',
            'data': {
                'page_number': 1,
                'page_size': 1,
                'order_direction': 'desc',
            },
        },
    )

    resp = SuperDict(await ws.receive_json_from())
    await ws.receive_nothing()

    assert resp['type'] == 'get_payments_response'
    assert len(resp['data']) == 1

    # Validate that user gets empty list
    await ws.send_json_to(
        {
            'type': 'get_payments',
            'data': {
                'page_number': 2,
                'page_size': 1,
                'order_direction': 'desc',
            },
        },
    )

    resp = SuperDict(await ws.receive_json_from())
    await ws.receive_nothing()

    assert resp['type'] == 'get_payments_response'
    assert len(resp['data']) == 0


@pytest.mark.django_db(transaction=True)
def test_status_payments_of_user(
    authorized_user: User,
):
    amount_to_pay = 50
    responses.add(
        responses.POST,
        url=__register_order_url,
        json={
            'formUrl': 'test_url',
            'orderId': 'test_id',
            'errorCode': '0'
        },
        status=200,
    )
    create_payment_link(authorized_user, amount_to_pay)

    request = GetPaymentsParams(
            page_number=1,
            page_size=10,
            order_direction=OrderEnum.desc,
    )
    payments: PaymentsHistory = get_payments_of_user(authorized_user, request)
    payment_history: PaymentHistoryView = payments.data[0]

    payment: Payment = Payment.objects.first()

    assert payment_history.uuid == str(payment.uuid)
    assert payment_history.cost_total == amount_to_pay
    assert payment_history.status == PaymentStatus.PENDING

    webhook_params = WebhookParameters(
        mdOrder='1',
        orderNumber=str(payment.uuid),
        callbackCreationDate='2023-12-12',
        operation=WebhookTypes.deposited,
        status=1,
    )
    check_sum_str = __webhook_parameters_to_verify_string(webhook_params)
    webhook_params.checkSum = __calculate_checksum(check_sum_str)
    verify_event(webhook_params)

    payments: PaymentsHistory = get_payments_of_user(authorized_user, request)
    payment_history: PaymentHistoryView = payments.data[0]

    assert payment_history.cost_total == amount_to_pay
    assert payment_history.uuid == str(payment.uuid)
    assert payment_history.status == PaymentStatus.PAID

    payment: Payment = Payment.objects.first()

    full_refund_operation(payment)

    payments: PaymentsHistory = get_payments_of_user(authorized_user, request)
    payment_history: PaymentHistoryView = payments.data[0]

    assert payment_history.cost_total == amount_to_pay
    assert payment_history.uuid == str(payment.uuid)
    assert payment_history.status == PaymentStatus.REFUNDED
