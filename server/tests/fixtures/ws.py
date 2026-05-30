import pytest_asyncio
from channels.auth import AuthMiddlewareStack
from channels.testing import WebsocketCommunicator

from chat.consumers import ChatConsumer
from tests.helpers import (
    add_money,
    create_parking_space,
    create_parking_space2,
    create_token,
    create_user,
)


@pytest_asyncio.fixture
async def ws():
    communicator = WebsocketCommunicator(
        AuthMiddlewareStack(ChatConsumer.as_asgi()),
        '/ws/socket-server/',
    )
    connected, subprotocol = await communicator.connect()
    assert connected
    yield communicator
    await communicator.disconnect()


@pytest_asyncio.fixture
async def authorized_user(ws: WebsocketCommunicator):
    user = await create_user()
    token = await create_token(user)
    await ws.send_json_to(
        {
            'type': 'token_auth',
            'data': {
                'token': token.key,
            },
        },
    )
    await ws.receive_nothing()
    yield user


@pytest_asyncio.fixture
async def authorized_user_with_money(
    ws: WebsocketCommunicator,
    authorized_user,
):
    await add_money(authorized_user, 1000)
    yield authorized_user


@pytest_asyncio.fixture
async def parking_space():
    return await create_parking_space()


@pytest_asyncio.fixture
async def parking_space2():
    return await create_parking_space2()
