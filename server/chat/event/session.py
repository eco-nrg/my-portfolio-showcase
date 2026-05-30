from typing import Union

from django.contrib.auth.models import User

from chat.charge_session import get_active_session
from chat.event.helpers import send_to
from chat.no_error import no_error
from chat.orders_history import present_history


@no_error
def send_start_session_success(target: Union[str, User], user: User):
    order = get_active_session(user)
    data = {}
    if order is not None:
        data = order.dict()
    msg = {
        'type': 'start_session_success',
        'data': data,
    }
    send_to(target, msg)


@no_error
def send_session_charging(target: Union[str, User], user: User):
    order = get_active_session(user)
    data = {}
    if order is not None:
        data = order.dict()
    msg = {
        'type': 'session_charging',
        'data': data,
    }
    send_to(target, msg)


@no_error
def send_sessions_history(target: Union[str, User], user: User):
    msg = {
        'type': 'sessions_history_response',
        'data': present_history(user).dict()['data'],
    }
    send_to(target, msg)


@no_error
def send_session_stop(target: Union[str, User], space_id: int):
    msg = {
        'type': 'session_stop',
        'data': {'id': space_id},
    }
    send_to(target, msg)
