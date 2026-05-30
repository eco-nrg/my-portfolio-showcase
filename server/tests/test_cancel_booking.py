import pytest
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import User

from chat.booking import BookSpaceParams, book_space
from main.models.parking_space import SPACE_STATUSES, ParkingSpace
from tests.helpers import receive_json


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio()
async def test_cancel_booking_when_some_booked(
    ws: WebsocketCommunicator,
    authorized_user: User,
    parking_space: ParkingSpace,
):
    await database_sync_to_async(book_space)(
        user=authorized_user,
        params=BookSpaceParams(
            space_id=parking_space.id,
            connector_type='TES_US',
        ),
    )
    await database_sync_to_async(parking_space.refresh_from_db)()

    await ws.send_json_to(
        {
            'type': 'cancel_bookings',
        },
    )
    cbr = await receive_json(ws)
    rr = await receive_json(ws)
    await ws.receive_nothing()

    await database_sync_to_async(parking_space.refresh_from_db)()
    assert (
        await database_sync_to_async(
            lambda: parking_space.is_booked,
        )()
    ) is False

    assert cbr['type'] == 'cancel_bookings_response'
    assert rr['type'] == 'refill_response'
    assert rr['data[0].station[0].spaces[0].status'] == SPACE_STATUSES.AVAILABLE
