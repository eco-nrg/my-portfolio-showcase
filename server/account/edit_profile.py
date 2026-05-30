from enum import Enum

from django.contrib.auth.models import User
from pydantic import BaseModel, Field, validator

from account.models import Profile
from main.data import car_models
from payments.bonus import add_fixed_bonus_singleton
from payments.models import BonusSource


class FastTypeEnum(str, Enum):
    CHADEMO = 'CHADEMO'
    CCS_COMBO1 = 'CCS-Combo1'
    CCS_COMBO2 = 'CCS-Combo2'
    GB_T = 'GB-T'


class SlowTypeEnum(str, Enum):
    J1772 = 'J1772'
    IEC62196 = 'IEC62196'
    TESLA_US = 'TESLA_US'
    GB_T_AC = 'GB_T_AC'


class EditProfileForm(BaseModel):
    email: str = Field(max_length=50)
    first_name: str = Field(max_length=50)
    middle_name: str = Field(max_length=50)
    manufacturer: str = Field(max_length=50)
    model: str = Field(max_length=50)
    number: str = Field(max_length=20)
    year: int = Field(ge=1980, le=2100)
    power: float = Field(ge=0, le=100)
    fast_type: str = Field(max_length=15)
    slow_type: str = Field(max_length=15)

    # @validator('manufacturer')
    # def manufacturer_check(cls, value: str):
    #     if value not in car_models:
    #         manuf_list = list(car_models.keys())
    #         raise ValueError(
    #             f'Производитель должен быть из списка: {manuf_list}',
    #         )
    #     return value
    #
    # @validator('model')
    # def model_check(cls, value: str, values, **kwargs):
    #     if 'manufacturer' not in values:
    #         return value
    #     models = car_models.get(values['manufacturer'])
    #     if models is None:
    #         return value
    #     if value not in models:
    #         raise ValueError(f'Модель должна быть из списка: {models}')
    #     return value


def edit_profile(form: EditProfileForm, user: User) -> Profile:
    # TODO: add validation
    user.profile.email = form.email
    user.profile.first_name = form.first_name
    user.profile.middle_name = form.middle_name
    user.profile.car_manufacturer = form.manufacturer
    user.profile.car_model = form.model
    user.profile.car_number = form.number
    user.profile.car_year = form.year
    user.profile.battery_power = form.power
    user.profile.fast_type = form.fast_type
    user.profile.slow_type = form.slow_type
    user.profile.save()
    user.profile.refresh_from_db()
    if user.profile.is_filled:
        add_fixed_bonus_singleton(BonusSource.FILL_PROFILE, user)
    return user.profile
