from datetime import timedelta

import pytest
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.utils import timezone

from tests.helpers import create_user, jms


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
@pytest.mark.parametrize(
    'test_input',
    [
        '79998887766',
        '7-999-888-77-66',
        '7(999)888-77-66',
        '+79998887766',
        '89998887766',
        '7999888776b',
        '',
        '776655',
        '799988877660',
    ],
)
async def test_send_code_handler__bad_phone(
    ws: WebsocketCommunicator,
    test_input: str,
):
    await ws.send_json_to(
        {
            'type': 'send_code',
            'data': {
                'phone': test_input,
            },
        },
    )

    resp = await ws.receive_json_from()
    await ws.receive_nothing()
    assert resp['type'] == 'error_response'
    assert jms('data.request', resp) == 'send_code'


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
@pytest.mark.parametrize('test_dt', [0, 30, 54])
async def test_send_code_handler__too_often_sms(
    ws: WebsocketCommunicator,
    test_dt: int,
):
    user = await create_user()
    user.profile.last_code_sent = timezone.now() - timedelta(seconds=test_dt)
    await database_sync_to_async(user.profile.save)(
        update_fields=['last_code_sent'],
    )

    await ws.send_json_to(
        {
            'type': 'send_code',
            'data': {
                'phone': user.username,
            },
        },
    )

    resp = await ws.receive_json_from()
    await ws.receive_nothing()
    assert resp['type'] == 'error_response'
    assert jms('data.request', resp) == 'send_code'
    assert jms('data.message', resp) == 'Слишком частая отправка. Попробуйте позже'


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
async def test_send_code_handler__good(
    ws: WebsocketCommunicator,
):
    user = await create_user()
    user.profile.last_code_sent = timezone.now() - timedelta(seconds=62)
    await database_sync_to_async(user.profile.save)(
        update_fields=['last_code_sent'],
    )

    await ws.send_json_to(
        {
            'type': 'send_code',
            'data': {
                'phone': user.username,
            },
        },
    )

    resp = await ws.receive_json_from()
    await ws.receive_nothing()
    assert resp['type'] == 'send_code_response'
    assert jms('data.success', resp) is True
    assert jms('data.message', resp) == 'СМС отправлено'
