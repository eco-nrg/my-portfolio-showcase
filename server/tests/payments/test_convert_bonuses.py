import pytest
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import User

from tests.helpers import add_bonuses, receive_json


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
async def test_success(
    ws: WebsocketCommunicator,
    authorized_user: User,
):
    current_bonuses = 100
    bonuses_to_convert = 30.51
    expected_bonuses = current_bonuses - bonuses_to_convert
    expected_money = bonuses_to_convert

    await add_bonuses(authorized_user, current_bonuses)

    await ws.send_json_to(
        {
            'type': 'convert_bonuses',
            'data': {
                'amount': bonuses_to_convert,
            },
        },
    )

    resp = await receive_json(ws)
    auth_response = await receive_json(ws)
    await ws.receive_nothing()

    assert resp['type'] == 'convert_bonuses_response'
    assert resp['data.balance'] == expected_money
    assert resp['data.bonus_balance'] == expected_bonuses

    assert auth_response['type'] == 'phone_auth_response'
    assert auth_response['data.cashData.money'] == expected_money
    assert auth_response['data.cashData.bonus'] == expected_bonuses


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
async def test_not_enough_bonuses(
    ws: WebsocketCommunicator,
    authorized_user: User,
):
    current_bonuses = 20
    bonuses_to_convert = 30

    await add_bonuses(authorized_user, current_bonuses)

    await ws.send_json_to(
        {
            'type': 'convert_bonuses',
            'data': {
                'amount': bonuses_to_convert,
            },
        },
    )

    resp = await receive_json(ws)
    await ws.receive_nothing()

    assert resp['type'] == 'error_response'
    assert resp['data.message'] == 'Недостаточно бонусов на счету'
    assert resp['data.request'] == 'convert_bonuses'


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
@pytest.mark.parametrize(
    'test_input',
    [
        {'amount': None},
        {'amount': 0},
        {'amount': -10},
    ],
)
async def test_incorrect_amount(
    ws: WebsocketCommunicator,
    authorized_user: User,
    test_input,
):
    current_bonuses = 100
    bonuses_to_convert = test_input.get('amount')

    await add_bonuses(authorized_user, current_bonuses)

    await ws.send_json_to(
        {
            'type': 'convert_bonuses',
            'data': {
                'amount': bonuses_to_convert,
            },
        },
    )

    resp = await receive_json(ws)
    await ws.receive_nothing()

    assert resp['type'] == 'error_response'
    assert resp['data.message'] == 'Неверный формат запроса'
    assert resp['data.request'] == 'convert_bonuses'
