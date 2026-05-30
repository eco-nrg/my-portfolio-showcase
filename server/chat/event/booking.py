from typing import Union

from django.contrib.auth.models import User

from chat.booking import get_active_booking
from chat.event.helpers import send_to
from chat.no_error import no_error


@no_error
def send_bookings(target: Union[str, User], user: User, send_none=False):
    book_result = get_active_booking(user)
    data = book_result.dict() if book_result is not None else None
    if data is None and send_none is False:
        return
    msg = {
        'type': 'book_space_response',
        'data': data,
    }
    send_to(target, msg)


@no_error
def send_cancel_bookings(target: Union[str, User]):
    send_to(
        target,
        {
            'type': 'cancel_bookings_response',
        },
    )
