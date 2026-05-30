import pytest
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import User

from tests.helpers import create_user, jms


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
async def test_phone_check__new_user(ws: WebsocketCommunicator):
    await ws.send_json_to(
        {
            'type': 'phone_check',
            'data': {
                'phone': '79998887766',
            },
        },
    )

    resp = await ws.receive_json_from()
    await ws.receive_nothing()

    assert resp['type'] == 'phone_check_response'
    assert jms('data.new_user', resp) is True
    assert jms('data.detail', resp) == 'СМС успешно отправлено'
    assert jms('data.code', resp) == 200

    user = await database_sync_to_async(User.objects.get)(
        username='79998887766',
    )
    assert user is not None


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
async def test_phone_check__old_user(ws: WebsocketCommunicator):
    user = await create_user()
    await ws.send_json_to(
        {
            'type': 'phone_check',
            'data': {
                'phone': user.username,
            },
        },
    )

    resp = await ws.receive_json_from()
    await ws.receive_nothing()

    assert resp['type'] == 'phone_check_response'
    assert jms('data.code', resp) == 200
    assert jms('data.new_user', resp) is False
    assert jms('data.detail', resp) == ''


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
@pytest.mark.parametrize(
    ('test_input', 'expected'),
    [
        ('79998887766', 200),
        ('7-999-888-77-66', 400),
        ('7(999)888-77-66', 400),
        ('+79998887766', 400),
        ('89998887766', 400),
        ('7999888776b', 400),
        ('', 400),
        ('776655', 400),
        ('799988877660', 400),
    ],
)
async def test_phone_check(
    test_input,
    expected,
    ws: WebsocketCommunicator,
):
    await ws.send_json_to(
        {
            'type': 'phone_check',
            'data': {
                'phone': test_input,
            },
        },
    )

    resp = await ws.receive_json_from()
    await ws.receive_nothing()

    assert resp['type'] == 'phone_check_response'
    assert jms('data.code', resp) == expected
