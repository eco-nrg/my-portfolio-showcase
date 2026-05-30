from http import HTTPStatus

from django.contrib.auth.models import User
from ninja import Router, Schema
from ninja.errors import HttpError
from pydantic import ValidationError

from account.auth.bearer_token import AuthBearerUser
from chat.charge_session import (
    StartSessionError,
    StartSessionParams,
    start_session,
)
from chat.event import (
    send_phone_auth_response,
    send_refills,
    send_sessions_history,
)
from chat.event.booking import send_cancel_bookings
from chat.event.session import send_session_charging
from chat.presenters import present_order
from chat.presenters.order import OrderInfoView
from chat.stop_session import StopSessionError, stop_session

router = Router(tags=['charging'])


class StartSessionRequest(Schema):
    space_id: int
    connector_type: str


class StopSessionRequest(Schema):
    space_id: int
    connector_type: str


class StopSessionResponse(Schema):
    id: int


@router.post(
    path='/session/start',
    auth=AuthBearerUser(),
    response=OrderInfoView,
)
def start_session_endpoint(request, data: StartSessionRequest) -> OrderInfoView:
    user: User = request.auth
    try:
        session_params = StartSessionParams(
            id=data.space_id,
            type=data.connector_type,
        )
    except ValidationError as val_err:
        raise HttpError(
            HTTPStatus.BAD_REQUEST,
            f'Неверный формат запроса: {val_err.errors()}',
        ) from val_err
    try:
        order = start_session(
            params=session_params,
            user=user,
        )
    except StartSessionError as sess_err:
        raise HttpError(HTTPStatus.BAD_REQUEST, sess_err.msg) from sess_err

    user.refresh_from_db()
    send_session_charging(user, user)
    send_refills('all')
    send_sessions_history(user, user)
    send_phone_auth_response(user, user)
    # так как активация бронирования подразумевает, что бронирования сняты
    send_cancel_bookings(user)

    return present_order(order)


@router.post(
    path='/session/stop',
    auth=AuthBearerUser(),
    response=StopSessionResponse,
)
def stop_session_endpoint(request):
    user: User = request.auth

    try:
        res = stop_session(user)
    except StopSessionError as err:
        raise HttpError(HTTPStatus.BAD_REQUEST, err.msg) from err

    user.refresh_from_db()
    send_phone_auth_response(user, user)
    send_sessions_history(user, user)

    return StopSessionResponse.parse_obj(res)
