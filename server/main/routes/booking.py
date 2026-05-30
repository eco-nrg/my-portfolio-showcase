from ninja import Router

from account.auth.bearer_token import AuthBearerUser
from chat.booking import BookSpaceParams, BookSpaceResult, book_space, cancel_bookings
from chat.event.booking import send_bookings, send_cancel_bookings
from chat.event.phone_auth import send_phone_auth_response
from chat.event.refill import send_refills

router = Router(tags=['booking'])


@router.post(
    path='/booking/book',
    auth=AuthBearerUser(),
    response=BookSpaceResult,
)
def book_station_endpoint(request, params: BookSpaceParams):
    user = request.auth

    booking = book_space(user, params)
    user.refresh_from_db()

    send_bookings(user, user)
    send_refills('all')
    send_phone_auth_response(user, user)

    return booking


@router.post(
    path='/booking/cancel',
    auth=AuthBearerUser(),
)
def cancel_bookings_endpoint(request):
    user = request.auth

    cancel_bookings(user)
    user.refresh_from_db()

    send_cancel_bookings(user)
    send_refills('all')
    send_phone_auth_response(user, user)

    return {}
