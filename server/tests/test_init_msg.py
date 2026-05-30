import pytest
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator

from chat.booking import BookSpaceParams, book_space
from main.models.parking_space import ParkingSpace
from tests.helpers import create_token, create_user, jms, receive_init_messages


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
async def test_init__positive(ws):
    user = await create_user()
    token = await create_token(user)
    await ws.send_json_to(
        {
            'type': 'init',
            'data': {
                'token': token.key,
            },
        },
    )

    messages = await receive_init_messages(ws)
    profile = messages[0]
    phone_auth = messages[1]

    assert jms('data.profileData.phone', profile) == user.username
    assert jms('data.cashData.freeTime', phone_auth) == 18000


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
async def test_init__empty_token(ws):
    await ws.send_json_to(
        {
            'type': 'init',
            'data': {'token': ''},
        },
    )
    msg = await ws.receive_json_from()
    assert msg['type'] == 'error_response'


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
async def test_init_when_has_booking(
    ws: WebsocketCommunicator,
    parking_space: ParkingSpace,
):
    user = await create_user()
    token = await create_token(user)
    book_res = await database_sync_to_async(book_space)(
        user=user,
        params=BookSpaceParams(
            space_id=parking_space.id,
            connector_type='TES_US',
        ),
    )
    await database_sync_to_async(parking_space.refresh_from_db)()
    assert parking_space.is_on is False
    assert (
        await database_sync_to_async(
            lambda: parking_space.is_booked,
        )()
        is True
    )

    await ws.send_json_to(
        {
            'type': 'init',
            'data': {
                'token': token.key,
            },
        },
    )
    profile = await ws.receive_json_from()
    phone_auth = await ws.receive_json_from()
    refill = await ws.receive_json_from()
    map_res = await ws.receive_json_from()
    sessions_history = await ws.receive_json_from()
    booking = await ws.receive_json_from()
    get_payments = await ws.receive_json_from()
    await ws.receive_nothing()

    assert profile['type'] == 'profile_response'
    assert phone_auth['type'] == 'phone_auth_response'
    assert refill['type'] == 'refill_response'
    assert map_res['type'] == 'map_response'
    assert sessions_history['type'] == 'sessions_history_response'
    assert booking['type'] == 'book_space_response'
    assert get_payments['type'] == 'get_payments_response'

    assert jms('data.profileData.phone', profile) == user.username
    assert jms('data.cashData.freeTime', phone_auth) == 14400
    assert jms('data.booking_id', booking) == book_res.booking_id
