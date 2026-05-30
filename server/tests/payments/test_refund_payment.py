from decimal import Decimal

import pytest
import responses
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.conf import settings
from django.contrib.auth.models import User
from pydantic import PositiveFloat

from account.models.profile import Profile
from payments.admin import full_refund_money
from payments.models import Operation, OperationAction, Payment
from payments.models.payment import PaymentStatus
from payments.models.webhook_parameters import WebhookParameters, WebhookTypes
from payments.services.webhook_service import __webhook_parameters_to_verify_string, __calculate_checksum, verify_event

from tests.helpers import SuperDict, receive_json

__base_url = settings.ALFA_BASE_URL
__register_order_url = f'{__base_url}{settings.ALFA_REGISTER_PAYMENT}'


@responses.activate
@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
async def test_force_full_refund(
    ws: WebsocketCommunicator,
    authorized_user: User,
):
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

    resp = await receive_json(ws)
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

    profile: Profile = authorized_user.profile
    balance = await database_sync_to_async(lambda: profile.balance)()
    assert balance == Decimal(str(amount_to_pay))

    selected_paymnet = await database_sync_to_async(
        lambda: Payment.objects.filter(pk=operation_payment.pk),
    )()
    await database_sync_to_async(
        lambda: full_refund_money(None, None, selected_paymnet),
    )()

    refund_operation: Operation = await database_sync_to_async(
        lambda: Operation.objects.get(
            payment=operation_payment.pk,
            action=OperationAction.REFUND,
        ),
    )()
    assert refund_operation.amount == Decimal(str(amount_to_pay))

    balance = await database_sync_to_async(lambda: profile.balance)()
    assert balance == 0
