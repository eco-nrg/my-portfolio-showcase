import asyncio

import pytest
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import User

from chat.booking import BookSpaceParams, book_space
from chat.charge_session import StartSessionParams, start_session
from main.models.booking import BookingStatus
from main.models.parking_space import SPACE_MODES, SPACE_STATUSES, ParkingSpace
from tests.helpers import (
    add_money,
    create_parking_space,
    create_parking_space2,
    create_user,
    receive_json,
)


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
async def test_start_session_unauthorized(ws: WebsocketCommunicator):
    await ws.send_json_to(
        {
            'type': 'start_session',
            'data': {
                'id': '1',
                'type': 'TES_US',
            },
        },
    )

    resp = await receive_json(ws)
    await ws.receive_nothing()

    assert resp['type'] == 'error_response'
    assert resp['data.message'] == 'Пользователь не авторизован'


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
async def test_start_session_nonexisting_station(
    ws: WebsocketCommunicator,
    authorized_user_with_money: User,
):
    await ws.send_json_to(
        {
            'type': 'start_session',
            'data': {
                'id': '1',
                'type': 'TES_US',
            },
        },
    )
    resp = await receive_json(ws)
    await ws.receive_nothing()

    assert resp['type'] == 'error_response'
    assert resp['data.message'] == 'Парковочное место не найдено'


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
async def test_start_session_bad_connector_type(
    ws: WebsocketCommunicator,
    authorized_user_with_money: User,
):
    space = await create_parking_space()
    await ws.send_json_to(
        {
            'type': 'start_session',
            'data': {
                'id': space.id,
                'type': '__BAD_TYPE__',
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
    'test_space_mode',
    [
        SPACE_MODES.TEST,
        SPACE_MODES.PRODUCTION,
    ],
)
async def test_start_session_empty_connector_type(
    ws: WebsocketCommunicator,
    authorized_user_with_money: User,
    test_space_mode,
):
    space = await create_parking_space(mode=test_space_mode)
    await ws.send_json_to(
        {
            'type': 'start_session',
            'data': {
                'id': space.id,
            },
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
    ],
)
async def test_start_session_with_free_seconds_test_station_positive(
    ws: WebsocketCommunicator,
    authorized_user: User,
    test_space_mode,
):
    space = await create_parking_space(mode=test_space_mode)
    assert space.is_on is False
    await ws.send_json_to(
        {
            'type': 'start_session',
            'data': {
                'id': space.id,
                'type': 'TES_US',
            },
        },
    )
    start_session_success = await receive_json(ws)
    sc = await receive_json(ws)
    ref = await receive_json(ws)
    history = await receive_json(ws)
    await ws.receive_nothing()

    await database_sync_to_async(space.refresh_from_db)()
    assert space.is_on is True

    assert start_session_success['type'] == 'start_session_success'
    assert start_session_success['data.connector_type'] == 'TES_US'
    assert start_session_success['data.total_kwh'] == 0

    assert sc['type'] == 'session_charging'
    assert sc['data.connector_type'] == 'TES_US'
    assert sc['data.total_kwh'] == 0

    assert ref['type'] == 'refill_response'
    assert ref['data[0].station[0].spaces[0].name'] == space.name
    assert ref['data[0].station[0].spaces[0].status'] == 'BU'

    assert history['type'] == 'sessions_history_response'
    assert history['data[0].status'] == 'ACT'


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
@pytest.mark.parametrize(
    'test_space_mode',
    [
        SPACE_MODES.PRODUCTION,
    ],
)
async def test_start_session_with_free_seconds_prod_station_negative(
    ws: WebsocketCommunicator,
    authorized_user: User,
    test_space_mode,
):
    space = await create_parking_space(mode=test_space_mode)
    assert space.is_on is False
    await ws.send_json_to(
        {
            'type': 'start_session',
            'data': {
                'id': space.id,
                'type': 'TES_US',
            },
        },
    )
    res = await receive_json(ws)
    await ws.receive_nothing()

    await database_sync_to_async(space.refresh_from_db)()
    assert space.is_on is False

    assert res['type'] == 'error_response'
    assert res['data.message'] == 'Недостаточно средств на счете'


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
@pytest.mark.parametrize(
    'test_space_mode',
    [
        SPACE_MODES.TEST,
    ],
)
async def test_start_session_with_money_test_station_negative(
    ws: WebsocketCommunicator,
    authorized_user: User,
    test_space_mode,
):
    authorized_user.profile.free_seconds = 0
    await database_sync_to_async(
        authorized_user.profile.save,
    )(update_fields=['free_seconds'])

    await add_money(authorized_user, 100)

    space = await create_parking_space(mode=test_space_mode)
    assert space.is_on is False
    await ws.send_json_to(
        {
            'type': 'start_session',
            'data': {
                'id': space.id,
                'type': 'TES_US',
            },
        },
    )
    res = await receive_json(ws)
    await ws.receive_nothing()

    await database_sync_to_async(space.refresh_from_db)()
    assert space.is_on is False

    assert res['type'] == 'error_response'
    assert res['data.message'] == 'Недостаточно бесплатных минут'


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
@pytest.mark.parametrize(
    'test_space_mode',
    [
        SPACE_MODES.PRODUCTION,
    ],
)
async def test_start_session_with_money_prod_station_positive(
    ws: WebsocketCommunicator,
    authorized_user: User,
    test_space_mode,
):
    authorized_user.profile.free_seconds = 0
    await database_sync_to_async(
        authorized_user.profile.save,
    )(update_fields=['free_seconds'])

    await add_money(authorized_user, 100)

    space = await create_parking_space(mode=test_space_mode)
    assert space.is_on is False
    await ws.send_json_to(
        {
            'type': 'start_session',
            'data': {
                'id': space.id,
                'type': 'TES_US',
            },
        },
    )
    start_session_success = await receive_json(ws)
    sc = await receive_json(ws)
    ref = await receive_json(ws)
    history = await receive_json(ws)
    await ws.receive_nothing()

    await database_sync_to_async(space.refresh_from_db)()
    assert space.is_on is True

    assert start_session_success['type'] == 'start_session_success'
    assert start_session_success['data.connector_type'] == 'TES_US'
    assert start_session_success['data.total_kwh'] == 0

    assert sc['type'] == 'session_charging'
    assert sc['data.connector_type'] == 'TES_US'
    assert sc['data.total_kwh'] == 0

    assert ref['type'] == 'refill_response'
    assert ref['data[0].station[0].spaces[0].name'] == space.name
    assert ref['data[0].station[0].spaces[0].status'] == 'BU'

    assert history['type'] == 'sessions_history_response'
    assert history['data[0].status'] == 'ACT'


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
@pytest.mark.parametrize(
    'test_space_mode',
    [
        SPACE_MODES.TEST,
        SPACE_MODES.PRODUCTION,
    ],
)
async def test_start_session_when_is_disabled(
    ws: WebsocketCommunicator,
    authorized_user_with_money: User,
    test_space_mode,
):
    space = await create_parking_space(mode=test_space_mode)
    space.status = SPACE_STATUSES.DISABLED
    await database_sync_to_async(space.save)(update_fields=['status'])

    await ws.send_json_to(
        {
            'type': 'start_session',
            'data': {
                'id': space.id,
                'type': 'TES_US',
            },
        },
    )
    res = await receive_json(ws)
    await ws.receive_nothing()

    await database_sync_to_async(space.refresh_from_db)()
    assert space.is_on is False

    assert res['type'] == 'error_response'
    assert res['data.message'] == 'Место не работает'


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
@pytest.mark.parametrize(
    'test_space_mode',
    [
        SPACE_MODES.TEST,
        SPACE_MODES.PRODUCTION,
    ],
)
async def test_start_session_when_busy(
    ws: WebsocketCommunicator,
    authorized_user_with_money: User,
    test_space_mode,
):
    space = await create_parking_space(mode=test_space_mode)
    another_user = await create_user(phone='79991234567')
    await add_money(another_user, 1000)
    await database_sync_to_async(start_session)(
        params=StartSessionParams(
            id=space.id,
            type='TES_US',
        ),
        user=another_user,
    )
    await database_sync_to_async(space.refresh_from_db)()
    assert space.is_on is True

    await ws.send_json_to(
        {
            'type': 'start_session',
            'data': {
                'id': space.id,
                'type': 'TES_US',
            },
        },
    )
    res = await receive_json(ws)
    await ws.receive_nothing()

    await database_sync_to_async(space.refresh_from_db)()
    assert space.is_on is True

    assert res['type'] == 'error_response'
    assert res['data.message'] == 'Место не свободно'


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
@pytest.mark.parametrize(
    'test_space_mode',
    [
        SPACE_MODES.TEST,
        SPACE_MODES.PRODUCTION,
    ],
)
async def test_start_session_when_no_free_minutes_and_money(
    ws: WebsocketCommunicator,
    authorized_user: User,
    test_space_mode,
):
    space = await create_parking_space(mode=test_space_mode)
    authorized_user.profile.free_seconds = 0
    await database_sync_to_async(
        authorized_user.profile.save,
    )(update_fields=['free_seconds'])

    await ws.send_json_to(
        {
            'type': 'start_session',
            'data': {
                'id': space.id,
                'type': 'TES_US',
            },
        },
    )
    res = await receive_json(ws)
    await ws.receive_nothing()

    await database_sync_to_async(space.refresh_from_db)()
    assert space.is_on is False

    assert res['type'] == 'error_response'
    if test_space_mode == SPACE_MODES.TEST:
        assert res['data.message'] == 'Недостаточно бесплатных минут'
    elif test_space_mode == SPACE_MODES.PRODUCTION:
        assert res['data.message'] == 'Недостаточно средств на счете'


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
@pytest.mark.parametrize(
    'test_space_mode',
    [
        SPACE_MODES.TEST,
        SPACE_MODES.PRODUCTION,
    ],
)
async def test_start_session_when_booked(
    ws: WebsocketCommunicator,
    authorized_user_with_money: User,
    test_space_mode,
):
    space = await create_parking_space(mode=test_space_mode)
    another_user = await create_user(phone='79991234567')
    await add_money(another_user, 1000)
    await database_sync_to_async(book_space)(
        user=another_user,
        params=BookSpaceParams(
            space_id=space.id,
            connector_type='TES_US',
        ),
    )
    await database_sync_to_async(space.refresh_from_db)()
    assert space.is_on is False
    assert space.status == SPACE_STATUSES.BOOKED
    assert (await database_sync_to_async(lambda: space.is_booked)()) is True

    await ws.send_json_to(
        {
            'type': 'start_session',
            'data': {
                'id': space.id,
                'type': 'TES_US',
            },
        },
    )
    res = await receive_json(ws)
    await ws.receive_nothing()

    await database_sync_to_async(space.refresh_from_db)()
    assert space.is_on is False

    assert res['type'] == 'error_response'
    assert res['data.message'] == 'Место забронировано'


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
@pytest.mark.parametrize(
    'test_space_mode',
    [
        SPACE_MODES.TEST,
        SPACE_MODES.PRODUCTION,
    ],
)
async def test_start_session_when_booked_by_me(
    ws: WebsocketCommunicator,
    authorized_user: User,
    test_space_mode,
):
    authorized_user.profile.free_seconds = 18000
    await add_money(authorized_user, 1000)
    space = await create_parking_space(mode=test_space_mode)
    await database_sync_to_async(book_space)(
        user=authorized_user,
        params=BookSpaceParams(
            space_id=space.id,
            connector_type='TES_US',
        ),
    )
    await database_sync_to_async(space.refresh_from_db)()
    assert space.is_on is False
    assert space.status == SPACE_STATUSES.BOOKED
    assert (await database_sync_to_async(lambda: space.is_booked)()) is True

    booking = await database_sync_to_async(lambda: space.booking)()
    assert booking.status == BookingStatus.ACTIVE

    await database_sync_to_async(authorized_user.refresh_from_db)()
    if test_space_mode == SPACE_MODES.TEST:
        assert (
            await database_sync_to_async(
                lambda: authorized_user.profile.free_seconds,
            )()
        ) == 14400
    elif test_space_mode == SPACE_MODES.PRODUCTION:
        assert (
            await database_sync_to_async(
                lambda: authorized_user.profile.balance,
            )()
        ) == 900

    await asyncio.sleep(3)

    await ws.send_json_to(
        {
            'type': 'start_session',
            'data': {
                'id': space.id,
                'type': 'TES_US',
            },
        },
    )
    start_session_success = await receive_json(ws)
    sc = await receive_json(ws)
    ref = await receive_json(ws)
    history = await receive_json(ws)
    await ws.receive_nothing()

    await database_sync_to_async(space.refresh_from_db)()
    assert space.is_on is True
    assert space.status == SPACE_STATUSES.BUSY

    await database_sync_to_async(booking.refresh_from_db)()
    assert booking.status == BookingStatus.ACTIVATED

    await database_sync_to_async(authorized_user.profile.refresh_from_db)()
    if test_space_mode == SPACE_MODES.TEST:
        assert (
            await database_sync_to_async(
                lambda: authorized_user.profile.free_seconds,
            )()
        ) >= 17980  # Потратили не более 20 секунд, остальное вернули
    elif test_space_mode == SPACE_MODES.PRODUCTION:
        assert (
            await database_sync_to_async(
                lambda: authorized_user.profile.balance,
            )()
        ) == 900  # Списанные деньги не вернули

    assert start_session_success['type'] == 'start_session_success'
    assert start_session_success['data.connector_type'] == 'TES_US'
    assert start_session_success['data.total_kwh'] == 0

    assert sc['type'] == 'session_charging'
    assert sc['data.connector_type'] == 'TES_US'
    assert sc['data.total_kwh'] == 0

    assert ref['type'] == 'refill_response'
    assert ref['data[0].station[0].spaces[0].name'] == space.name
    assert ref['data[0].station[0].spaces[0].status'] == 'BU'

    assert history['type'] == 'sessions_history_response'
    assert history['data[0].status'] == 'ACT'


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
@pytest.mark.parametrize(
    'test_space_mode',
    [
        SPACE_MODES.TEST,
        SPACE_MODES.PRODUCTION,
    ],
)
async def test_start_session_when_has_active(
    ws: WebsocketCommunicator,
    authorized_user_with_money: User,
    parking_space: ParkingSpace,
    test_space_mode,
):
    parking_space2 = await create_parking_space2(mode=test_space_mode)
    await database_sync_to_async(start_session)(
        StartSessionParams(
            id=parking_space.id,
            type=parking_space.charge_type,
        ),
        authorized_user_with_money,
    )
    await database_sync_to_async(parking_space.refresh_from_db)()
    assert parking_space.is_on is True
    assert parking_space.status == SPACE_STATUSES.BUSY

    await ws.send_json_to(
        {
            'type': 'start_session',
            'data': {
                'id': parking_space2.id,
                'type': parking_space2.charge_type,
            },
        },
    )
    res = await receive_json(ws)
    await ws.receive_nothing()

    await database_sync_to_async(parking_space2.refresh_from_db)()
    assert parking_space2.is_on is False
    assert parking_space2.status == SPACE_STATUSES.AVAILABLE

    assert res['type'] == 'error_response'
    assert (
        res['data.message']
        == 'Одновременно может быть активная только одна сессия зарядки'
    )
