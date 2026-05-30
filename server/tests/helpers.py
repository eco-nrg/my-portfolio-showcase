from typing import Any

import jmespath
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import User
from django.utils import timezone

from account.models import Token
from main.models import SPACE_STATUSES, ParkingLot, ParkingSpace
from main.models.city import City
from main.models.connector import ParkingSpaceConnector
from main.models.parking_space import SPACE_MODES
from payments.models import (
    BonusOperation,
    BonusOperationType,
    Operation,
    OperationAction,
    OperationType,
)


def jms(expression: str, data: Any):
    return jmespath.search(expression, data)


class SuperDict:
    def __init__(self, data: Any) -> None:
        self.data = data

    def __getitem__(self, expression: str):
        return jmespath.search(expression, self.data)

    def __str__(self) -> str:
        return str(self.data)


@database_sync_to_async
def create_user(phone: str = '79999999999', code: str = '1234'):
    # TODO: this must be a service function
    user = User.objects.create(username=phone)
    user.set_password(code)
    user.save()
    user.profile.code = code
    user.profile.last_code_sent = timezone.now()
    user.profile.first_name = 'first_name'
    user.profile.middle_name = 'middle_name'
    user.profile.car_manufacturer = 'Tesla'
    user.profile.car_model = 'Model X'
    user.profile.car_number = 'A777AA'
    user.profile.car_year = 2025
    user.profile.battery_power = 100
    user.profile.fast_type = 'CHADEMO'
    user.profile.slow_type = 'TESLA_US'
    user.profile.save()
    return user


@database_sync_to_async
def create_empty_user(phone='79999999999', code='1234'):
    # TODO: this must be a service function
    user = User.objects.create(username=phone)
    user.set_password(code)
    user.save()
    user.profile.code = code
    user.profile.last_code_sent = timezone.now()
    user.profile.save()
    return user


@database_sync_to_async
def create_token(user: User):
    return Token.objects.create(user=user)


@database_sync_to_async
def create_parking_space(mode: str = SPACE_MODES.TEST):
    city = City(
        name='Новотестинг',
        slug='newtesting',
    )
    city.save()
    lot = ParkingLot(
        uid='TEST_PARKING',
        name='Тестовая парковка',
        address='Тестовый сервер 1',
        city=city,
    )
    lot.save()
    parking_space = ParkingSpace(
        charge_type='TES_US',
        name='777',
        uid='TEST_PARKING_777',
        price_kw=10,
        price_hour=100,
        status=SPACE_STATUSES.AVAILABLE,
        mode=mode,
        lot=lot,
        meter_code='99',
        meter_com_port='/dev/ttyUSB0',
    )
    parking_space.save()
    connector = ParkingSpaceConnector(
        space=parking_space,
        connector_type='TES_US',
        phases_count=1,
        max_kw=20,
        max_a=80,
    )
    connector.save()
    return parking_space


@database_sync_to_async
def create_parking_space2(mode=SPACE_MODES.TEST):
    parking_space = ParkingSpace(
        charge_type='J1772',
        name='888',
        uid='TEST_PARKING_888',
        price_kw=10,
        price_hour=100,
        status=SPACE_STATUSES.AVAILABLE,
        mode=mode,
        lot=ParkingLot.objects.get(uid='TEST_PARKING'),
        meter_code='88',
        meter_com_port='/dev/ttyUSB0',
    )
    parking_space.save()
    connector = ParkingSpaceConnector(
        space=parking_space,
        connector_type='J1772',
        phases_count=1,
        max_kw=20,
        max_a=80,
    )
    connector.save()
    return parking_space


@database_sync_to_async
def add_money(user: User, amount: int):
    return Operation.objects.create(
        kind=OperationType.DEBIT,
        action=OperationAction.PAYMENT,
        amount=amount,
        created_at=timezone.now(),
        user=user,
        payment=None,
    )


@database_sync_to_async
def add_bonuses(user: User, amount: int):
    return BonusOperation.objects.create(
        kind=BonusOperationType.DEBIT,
        description='Зачисление бонусов',
        amount=amount,
        created_at=timezone.now(),
        user=user,
    )


@database_sync_to_async
def find_token(user: User):
    return Token.objects.filter(user=user).first()


async def receive_init_messages(ws: WebsocketCommunicator):
    profile = await ws.receive_json_from()
    phone_auth = await ws.receive_json_from()
    refill = await ws.receive_json_from()
    map_res = await ws.receive_json_from()
    sessions_history = await ws.receive_json_from()
    await ws.receive_nothing()
    return profile, phone_auth, refill, map_res, sessions_history


async def receive_json(ws: WebsocketCommunicator):
    return SuperDict(await ws.receive_json_from())
