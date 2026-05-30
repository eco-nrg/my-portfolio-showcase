from typing import Optional, Union

from django.contrib.auth.models import User

from account.models import Token
from chat.booking import get_active_booking
from chat.charge_session import get_active_session
from chat.event.helpers import send_to
from chat.no_error import no_error


@no_error
def send_phone_auth_response(
    target: Union[str, User],
    user: User,
    token_value: Optional[str] = None,
):
    if token_value is None:
        token = Token.objects.filter(user=user, is_active=True).first()
        if token is not None:
            token_value = token.key

    booking = get_active_booking(user)
    session = get_active_session(user)
    user.refresh_from_db()

    resp = {
        'auth': token_value,
        'cashData': {
            'money': float(user.profile.balance),
            'bonus': float(user.profile.bonus_balance),
            'freeTime': user.profile.free_seconds,
        },
        'book_state': None,  # deprecated
        'bonusUser': [
            {
                'command': 'new_user',
                'summ': 100,
            },
        ],
        'alertMessanger': [],
        'booking': booking.dict() if booking is not None else None,
        'session_charging': session.dict() if session is not None else None,
    }

    if user.profile.is_filled:
        resp['bonusUser'].append(
            {
                'command': 'fill_profile',
                'summ': 200,
            },
        )
        # TODO Реализовать бонус за заполнение профиля, если это нужно

    else:
        resp['alertMessanger'].append(
            {
                'page': 'profile',
                'command': 'fill_profile',
                'icon': 'exclamation',
                'messanger': 'Заполните профиль чтобы получать скидки и бонусы',
            },
        )

    send_to(
        target,
        {
            'type': 'phone_auth_response',
            'data': resp,
        },
    )
