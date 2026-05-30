import pytest
from channels.testing import WebsocketCommunicator

from tests.helpers import (
    create_empty_user,
    create_parking_space,
    create_user,
    find_token,
    jms,
)
from tests.test_init_msg import receive_init_messages


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
async def test_login_when_user_no_filled(ws: WebsocketCommunicator):
    space = await create_parking_space()
    user = await create_empty_user()

    token = await find_token(user)
    assert token is None

    await ws.send_json_to(
        {
            'type': 'phone_auth',
            'data': {
                'phone': user.username,
                'code': user.profile.code,
            },
        },
    )
    (
        profile,
        phone_auth,
        refill,
        _,
        sessions_history,
    ) = await receive_init_messages(ws)

    assert jms('data.profileData.phone', profile) == user.username

    assert jms('data.cashData.freeTime', phone_auth) == 18000
    assert jms('data.alertMessanger[0].command', phone_auth) == 'fill_profile'

    assert len(refill['data']) == 1
    assert jms('data[0].name', refill) == space.lot.city.name
    assert jms('data[0].station[0].name', refill) == space.lot.name
    assert jms('data[0].station[0].address', refill) == space.lot.address
    assert jms('data[0].station[0].spaces[0].name', refill) == space.name
    assert jms('data[0].station[0].spaces[0].status', refill) == space.status

    assert not sessions_history['data']

    token = await find_token(user)
    assert token is not None


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
async def test_login_when_user_is_full(ws: WebsocketCommunicator):
    space = await create_parking_space()
    user = await create_user()

    token = await find_token(user)
    assert token is None

    await ws.send_json_to(
        {
            'type': 'phone_auth',
            'data': {
                'phone': user.username,
                'code': user.profile.code,
            },
        },
    )

    (
        profile,
        phone_auth,
        refill,
        _,
        sessions_history,
    ) = await receive_init_messages(ws)

    assert jms('data.profileData.phone', profile) == user.username

    assert jms('data.cashData.freeTime', phone_auth) == 18000
    assert not phone_auth['data']['alertMessanger']

    assert len(refill['data']) == 1
    assert jms('data[0].name', refill) == space.lot.city.name
    assert jms('data[0].station[0].name', refill) == space.lot.name
    assert jms('data[0].station[0].address', refill) == space.lot.address
    assert jms('data[0].station[0].spaces[0].name', refill) == space.name
    assert jms('data[0].station[0].spaces[0].status', refill) == space.status

    assert not sessions_history['data']

    token = await find_token(user)
    assert token is not None
