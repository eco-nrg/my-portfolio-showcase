import pytest
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import User

from chat.booking import BookSpaceParams, book_space
from chat.charge_session import StartSessionParams, start_session
from main.models.parking_space import SPACE_MODES
from tests.helpers import (
    add_money,
    create_parking_space,
    create_parking_space2,
    create_user,
    receive_json,
)


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
async def test_book_space_unauthorized(ws: WebsocketCommunicator):
    await ws.send_json_to(
        {
            'type': 'book_space',
            'data': {
                'space_id': '1',
                'connector_type': 'TES_US',
            },
        },
    )

    resp = await receive_json(ws)
    await ws.receive_nothing()

    assert resp['type'] == 'error_response'
    assert resp['data.message'] == 'Пользователь не авторизован'


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
async def test_book_space_nonexisting_station(
    ws: WebsocketCommunicator,
    authorized_user: User,
):
    await ws.send_json_to(
        {
            'type': 'book_space',
            'data': {
                'space_id': '1',
                'connector_type': 'TES_US',
            },
        },
    )

    resp = await receive_json(ws)
    await ws.receive_nothing()

    assert resp['type'] == 'error_response'
    assert resp['data.message'] == 'Парковочное место не найдено'


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
@pytest.mark.parametrize(
    'test_space_mode',
    [
        SPACE_MODES.TEST,
        SPACE_MODES.PRODUCTION,
    ],
)
async def test_book_space_nonexisting_connector(
    ws: WebsocketCommunicator,
    authorized_user_with_money: User,
    test_space_mode,
):
    parking_space = await create_parking_space(test_space_mode)
    await ws.send_json_to(
        {
            'type': 'book_space',
            'data': {
                'space_id': parking_space.id,
                'connector_type': '__BAD_CONNECTOR__',
            },
        },
    )

    resp = await receive_json(ws)
    await ws.receive_nothing()

    assert resp['type'] == 'error_response'
    assert resp['data.message'] == 'Коннектор не найден'


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
@pytest.mark.parametrize(
    'test_input',
    [
        {'space_mode': SPACE_MODES.TEST, 'data': None},
        {'space_mode': SPACE_MODES.TEST, 'data': {}},
        {
            'space_mode': SPACE_MODES.TEST,
            'data': {
                'space_id': 'asdads',
                'connector_type': 'TES_US',
            },
        },
        {'space_mode': SPACE_MODES.TEST, 'data': {'connector_type': 'TES_US'}},
        {'space_mode': SPACE_MODES.TEST, 'data': {'space_id': 1}},
        {'space_mode': SPACE_MODES.PRODUCTION, 'data': None},
        {'space_mode': SPACE_MODES.PRODUCTION, 'data': {}},
        {
            'space_mode': SPACE_MODES.PRODUCTION,
            'data': {
                'space_id': 'asdads',
                'connector_type': 'TES_US',
            },
        },
        {
            'space_mode': SPACE_MODES.PRODUCTION,
            'data': {
                'connector_type': 'TES_US',
            },
        },
        {'space_mode': SPACE_MODES.PRODUCTION, 'data': {'space_id': 1}},
    ],
)
async def test_book_space_bad_format(
    ws: WebsocketCommunicator,
    authorized_user_with_money: User,
    test_input,
):
    await create_parking_space(test_input.get('space_mode'))
    await ws.send_json_to(
        {
            'type': 'book_space',
            'data': test_input.get('data'),
        },
    )

    resp = await receive_json(ws)
    await ws.receive_nothing()

    assert resp['type'] == 'error_response'
    assert resp['data.message'] == 'Неверный формат запроса'


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
@pytest.mark.parametrize(
    'test_space_mode',
    [
        SPACE_MODES.TEST,
        SPACE_MODES.PRODUCTION,
    ],
)
async def test_book_space_positive(
    ws: WebsocketCommunicator,
    authorized_user: User,
    test_space_mode,
):
    authorized_user.profile.free_seconds = 18000
    await add_money(authorized_user, 1000)

    parking_space = await create_parking_space(test_space_mode)
    await ws.send_json_to(
        {
            'type': 'book_space',
            'data': {
                'space_id': parking_space.id,
                'connector_type': 'TES_US',
            },
        },
    )

    br = await receive_json(ws)
    rr = await receive_json(ws)
    pa = await receive_json(ws)
    await ws.receive_nothing()

    await database_sync_to_async(parking_space.refresh_from_db)()
    assert parking_space.is_on is False
    assert (
        await database_sync_to_async(
            lambda: parking_space.is_booked,
        )()
        is True
    )
    assert (
        await database_sync_to_async(
            lambda: authorized_user.bookings.count(),
        )()
        == 1
    )

    assert br['type'] == 'book_space_response'
    assert br['data.space_id'] == parking_space.id
    assert br['data.connector_type'] == 'TES_US'

    assert rr['type'] == 'refill_response'
    assert pa['type'] == 'phone_auth_response'

    if test_space_mode == SPACE_MODES.TEST:
        assert pa['data.cashData.freeTime'] == 14400  # 4 hours after booking
        assert pa['data.cashData.money'] == 1000
    elif test_space_mode == SPACE_MODES.PRODUCTION:
        assert pa['data.cashData.freeTime'] == 18000
        assert pa['data.cashData.money'] == 900


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
@pytest.mark.parametrize(
    'test_space_mode',
    [
        SPACE_MODES.TEST,
        SPACE_MODES.PRODUCTION,
    ],
)
async def test_book_space_when_space_is_disabled(
    ws: WebsocketCommunicator,
    authorized_user_with_money: User,
    test_space_mode,
):
    parking_space = await create_parking_space(test_space_mode)
    await database_sync_to_async(parking_space.disable)()
    await ws.send_json_to(
        {
            'type': 'book_space',
            'data': {
                'space_id': parking_space.id,
                'connector_type': 'TES_US',
            },
        },
    )

    resp = await receive_json(ws)
    await ws.receive_nothing()

    assert resp['type'] == 'error_response'
    assert resp['data.message'] == 'Парковочное место выключено'


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
@pytest.mark.parametrize(
    'test_space_mode',
    [
        SPACE_MODES.TEST,
        SPACE_MODES.PRODUCTION,
    ],
)
async def test_book_space_when_space_is_busy(
    ws: WebsocketCommunicator,
    authorized_user_with_money: User,
    test_space_mode,
):
    parking_space = await create_parking_space(test_space_mode)
    another_user = await create_user(phone='79991234567')
    await add_money(another_user, 1000)
    await database_sync_to_async(start_session)(
        params=StartSessionParams(
            id=parking_space.id,
            type='TES_US',
        ),
        user=another_user,
    )
    await database_sync_to_async(parking_space.refresh_from_db)()
    assert parking_space.is_on is True

    await ws.send_json_to(
        {
            'type': 'book_space',
            'data': {
                'space_id': parking_space.id,
                'connector_type': 'TES_US',
            },
        },
    )

    resp = await receive_json(ws)
    await ws.receive_nothing()

    assert resp['type'] == 'error_response'
    assert resp['data.message'] == 'Парковочное место занято'


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
@pytest.mark.parametrize(
    'test_space_mode',
    [
        SPACE_MODES.TEST,
        SPACE_MODES.PRODUCTION,
    ],
)
async def test_book_space_when_space_is_booked(
    ws: WebsocketCommunicator,
    authorized_user_with_money: User,
    test_space_mode,
):
    parking_space = await create_parking_space(test_space_mode)
    another_user = await create_user(phone='79991234567')
    await add_money(another_user, 1000)
    await database_sync_to_async(book_space)(
        user=another_user,
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
            'type': 'book_space',
            'data': {
                'space_id': parking_space.id,
                'connector_type': 'TES_US',
            },
        },
    )

    resp = await receive_json(ws)
    await ws.receive_nothing()

    assert resp['type'] == 'error_response'
    assert resp['data.message'] == 'Парковочное место забронированно'


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
@pytest.mark.parametrize(
    'test_space_mode',
    [
        SPACE_MODES.TEST,
        SPACE_MODES.PRODUCTION,
    ],
)
async def test_book_space_when_already_booked_another(
    ws: WebsocketCommunicator,
    authorized_user_with_money: User,
    test_space_mode,
):
    parking_space = await create_parking_space(test_space_mode)
    another_space = await create_parking_space2(test_space_mode)

    await database_sync_to_async(book_space)(
        user=authorized_user_with_money,
        params=BookSpaceParams(
            space_id=another_space.id,
            connector_type='J1772',
        ),
    )

    await ws.send_json_to(
        {
            'type': 'book_space',
            'data': {
                'space_id': parking_space.id,
                'connector_type': 'TES_US',
            },
        },
    )
    resp = await receive_json(ws)
    await ws.receive_nothing()

    assert resp['type'] == 'error_response'
    assert resp['data.message'] == 'Можно бронировать только одну станцию'


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
@pytest.mark.parametrize(
    'test_space_mode',
    [
        SPACE_MODES.TEST,
        SPACE_MODES.PRODUCTION,
    ],
)
async def test_book_space_when_already_booked_today(
    ws: WebsocketCommunicator,
    authorized_user_with_money: User,
    test_space_mode,
):
    parking_space = await create_parking_space(test_space_mode)
    await database_sync_to_async(book_space)(
        user=authorized_user_with_money,
        params=BookSpaceParams(
            space_id=parking_space.id,
            connector_type='TES_US',
        ),
    )
    await database_sync_to_async(parking_space.refresh_from_db)()

    await database_sync_to_async(lambda: parking_space.booking.cancel())()
    await database_sync_to_async(parking_space.refresh_from_db)()
    assert (
        await database_sync_to_async(
            lambda: parking_space.is_booked,
        )()
        is False
    )

    await ws.send_json_to(
        {
            'type': 'book_space',
            'data': {
                'space_id': parking_space.id,
                'connector_type': 'TES_US',
            },
        },
    )
    resp = await receive_json(ws)
    await ws.receive_nothing()

    assert resp['type'] == 'error_response'
    assert resp['data.message'] == 'В день можно бронировать один раз'


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
@pytest.mark.parametrize(
    'test_space_mode',
    [
        SPACE_MODES.TEST,
        SPACE_MODES.PRODUCTION,
    ],
)
async def test_book_space_when_already_has_active(
    ws: WebsocketCommunicator,
    authorized_user_with_money: User,
    test_space_mode,
):
    parking_space = await create_parking_space(test_space_mode)
    parking_space2 = await create_parking_space2(test_space_mode)
    await database_sync_to_async(start_session)(
        StartSessionParams(
            id=parking_space.id,
            type=parking_space.charge_type,
        ),
        authorized_user_with_money,
    )

    await ws.send_json_to(
        {
            'type': 'book_space',
            'data': {
                'space_id': parking_space2.id,
                'connector_type': parking_space2.charge_type,
            },
        },
    )
    resp = await receive_json(ws)
    await ws.receive_nothing()

    await database_sync_to_async(parking_space2.refresh_from_db)()
    assert (
        await database_sync_to_async(
            lambda: parking_space2.is_booked,
        )()
        is False
    )

    assert resp['type'] == 'error_response'
    assert (
        resp['data.message']
        == 'Нельзя бронировать станцию, пока есть активная сессия зарядки'
    )
