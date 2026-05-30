from typing import Union

from django.contrib.auth.models import User

from account.models import Profile
from chat.event.helpers import send_to
from chat.no_error import no_error
from main.data import car_models


def present_profile(user: User):
    car_keys = {}
    car_list = []
    for key, values in car_models.items():
        models = [
            {
                'value': x,
                'selected': (
                    x == user.profile.car_model and key == user.profile.car_manufacturer
                ),
            }
            for x in values
        ]
        car_keys[key] = models
        car_list.extend(models)

    return {
        'profileData': {
            'phone': user.username,
            'email': user.profile.email,
            'first_name': user.profile.first_name,
            'middle_name': user.profile.middle_name,
        },
        'carData': {
            'manufacturer': user.profile.car_manufacturer,
            'model': user.profile.car_model,
            'number': user.profile.car_number,
            'year': user.profile.car_year,
        },
        'batteryData': {
            'power': (
                float(user.profile.battery_power)
                if user.profile.battery_power
                else None
            ),
            'fast_type': user.profile.fast_type,
            'slow_type': user.profile.slow_type,
        },
        'listModel': car_keys,
        'listModelAll': car_list,
        'listManufacturer': [
            {
                'value': x,
                'selected': x == user.profile.car_manufacturer,
            }
            for x in car_models
        ],
        'fast_choices': dict(Profile.FAST_CHOICES),
        'slow_choices': dict(Profile.SLOW_CHOICES),
        'filledProfile': user.profile.is_filled,
    }


@no_error
def send_profile(target: Union[str, User], user: User) -> None:
    msg = {
        'type': 'profile_response',
        'data': present_profile(user),
    }
    send_to(target, msg)


@no_error
def send_edit_profile_response(target: Union[str, User]) -> None:
    msg = {'type': 'edit_profile_response', 'data': None}
    send_to(target, msg)
