from datetime import timedelta
from decimal import Decimal

import pytest
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
from django.utils import timezone

from chat.booking import BookSpaceParams, book_space
from chat.charge_session import StartSessionParams, start_session
from chat.orders_history import OrderHistoryView, present_order_history
from chat.stop_session import stop_session
from cron.cron_charge_orders import (
    FREE_TIME_THRESHOLD,
    charge_active_orders,
)
from main.models import (
    ORDER_STATUSES,
    Order,
    ParkingSpace,
    ParkingSpaceConnector,
)
from main.models.parking_space import SPACE_MODES
from tests.helpers import add_money, create_parking_space

HOUR_TO_SECONDS = 3600


@pytest.fixture()
def user():
    u = User.objects.create(username='79999999999')
    u.set_password('1234')
    u.save()
    u.profile.code = '1234'
    u.profile.last_code_sent = timezone.now()
    u.profile.first_name = 'first_name'
    u.profile.middle_name = 'middle_name'
    u.profile.car_manufacturer = 'Tesla'
    u.profile.car_model = 'Model X'
    u.profile.car_number = 'A777AA'
    u.profile.car_year = 2025
    u.profile.battery_power = 100
    u.profile.fast_type = 'CHADEMO'
    u.profile.slow_type = 'TESLA_US'
    u.profile.save()
    return u


@pytest.mark.django_db(transaction=True)
def test_enough_money_to_pay_production_space(mocker, user: User):
    money = 200

    mock_time = timezone.now()
    mocked_now = mocker.patch(
        'django.utils.timezone.now',
        return_value=mock_time,
    )

    async_to_sync(add_money)(user, money)

    assert user.profile.balance == 200

    parking_space: ParkingSpace = async_to_sync(
        create_parking_space,
    )(mode=SPACE_MODES.PRODUCTION)
    connector: ParkingSpaceConnector = ParkingSpaceConnector.objects.first()

    params = StartSessionParams(
        id=parking_space.id,
        type=connector.connector_type,
    )
    order = start_session(params, user)

    parking_space.current_a = 0
    parking_space.total_kw = 0
    parking_space.save(update_fields=['current_a', 'total_kw'])
    mocked_now.return_value = mock_time + timedelta(hours=0.5)
    charge_active_orders()

    parking_space.current_a = 25
    parking_space.total_kw = 7
    parking_space.save(update_fields=['current_a', 'total_kw'])
    mocked_now.return_value = mock_time + timedelta(hours=2)
    charge_active_orders()

    # cost_total = time_cost * 30m + 7kw * kw_cost * 1.5h

    assert order.status == ORDER_STATUSES.ACTIVE

    stop_session(user)
    order.refresh_from_db()
    assert order.status == ORDER_STATUSES.FINISHED

    user.profile.refresh_from_db()
    cost_kw = parking_space.price_kw * 7
    cost_time = parking_space.price_hour * 0.5
    expected_cost = cost_kw + cost_time
    assert order.cost_total == expected_cost
    assert user.profile.balance == (money - expected_cost)


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    'test_space_mode',
    [
        SPACE_MODES.TEST,
        SPACE_MODES.PRODUCTION,
    ],
)
def test_cost_every_service(mocker, user: User, test_space_mode):
    free_seconds = 18000
    money = 500
    cost_booking_money = 100
    cost_booking_time = 3600

    mock_time = timezone.now()
    mocked_now = mocker.patch(
        'django.utils.timezone.now',
        return_value=mock_time,
    )

    user.profile.free_seconds = free_seconds

    async_to_sync(add_money)(user, money)

    assert user.profile.balance == money

    parking_space: ParkingSpace = async_to_sync(
        create_parking_space,
    )(mode=test_space_mode)
    connector: ParkingSpaceConnector = ParkingSpaceConnector.objects.first()

    book_params = BookSpaceParams(
        space_id=parking_space.id,
        connector_type='TES_US',
    )

    book_space(user=user, params=book_params)

    if test_space_mode == SPACE_MODES.TEST:
        assert user.profile.free_seconds == free_seconds - cost_booking_time

    start_params = StartSessionParams(
        id=parking_space.id,
        type=connector.connector_type,
    )
    order = start_session(params=start_params, user=user)

    # Бесплатное время возращается, если пользователь активировал станцию после брони
    assert user.profile.free_seconds == free_seconds

    if test_space_mode == SPACE_MODES.TEST:
        assert user.profile.balance == money
    elif test_space_mode == SPACE_MODES.PRODUCTION:
        assert user.profile.balance == money - cost_booking_money

    parking_space.current_a = 0
    parking_space.total_kw = 0
    before_charging = 0.05
    parking_space.save(update_fields=['current_a', 'total_kw'])
    mocked_now.return_value = mock_time + timedelta(hours=before_charging)
    charge_active_orders()

    # (TODO): Добавить тест проверку на то, что не ток пошел, но пистолет вставлен

    parking_space.current_a = 25
    parking_space.total_kw = 7
    time_charing = 2
    parking_space.save(update_fields=['current_a', 'total_kw'])
    mocked_now.return_value = mock_time + timedelta(
        hours=before_charging + time_charing,
    )
    charge_active_orders()

    parking_space.current_a = 0
    parking_space.total_kw = 7
    time_downtime = 0.5
    parking_space.save(update_fields=['current_a', 'total_kw'])
    mocked_now.return_value = mock_time + timedelta(
        hours=before_charging + time_charing + time_downtime,
    )
    charge_active_orders()
    order.refresh_from_db()

    assert order.status == ORDER_STATUSES.ACTIVE

    mocked_now.return_value = mock_time + timedelta(
        hours=(before_charging + time_charing + time_downtime),
    )
    stop_session(user)
    order.refresh_from_db()

    assert order.status == ORDER_STATUSES.FINISHED

    user.profile.refresh_from_db()

    order_info: Order = Order.objects.first()
    order_history: OrderHistoryView = present_order_history(order_info)

    cost_booking = Decimal(order_history.cost_booking)
    cost_kw = Decimal(order_history.cost_kw)
    cost_idle = Decimal(order_history.cost_idle)
    cost_total_with_booking_and_downtime = Decimal(order_history.cost_total)

    if test_space_mode == SPACE_MODES.TEST:
        assert cost_booking == 0
        assert cost_kw == 0
        assert cost_idle == 0
        assert cost_total_with_booking_and_downtime == 0

        assert user.profile.balance == money
        assert user.profile.free_seconds == (
            free_seconds
            - (before_charging + time_charing + time_downtime) * HOUR_TO_SECONDS
        )
    elif test_space_mode == SPACE_MODES.PRODUCTION:
        assert cost_booking == cost_booking_money
        assert cost_kw == parking_space.price_kw * 7
        assert cost_idle == parking_space.price_hour * time_downtime

        assert user.profile.balance == (money - cost_total_with_booking_and_downtime)
        assert user.profile.free_seconds == free_seconds


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    'test_space_mode',
    [
        SPACE_MODES.TEST,
        SPACE_MODES.PRODUCTION,
    ],
)
def test_downtime_not_taken_in_warm_up(mocker, user: User, test_space_mode):
    free_seconds = 18000
    money = 500

    mock_time = timezone.now()
    mocked_now = mocker.patch(
        'django.utils.timezone.now',
        return_value=mock_time,
    )

    user.profile.free_seconds = free_seconds

    async_to_sync(add_money)(user, money)

    assert user.profile.balance == money

    parking_space: ParkingSpace = async_to_sync(
        create_parking_space,
    )(mode=test_space_mode)
    connector: ParkingSpaceConnector = ParkingSpaceConnector.objects.first()

    start_params = StartSessionParams(
        id=parking_space.id,
        type=connector.connector_type,
    )
    order = start_session(params=start_params, user=user)

    TIME_PREPARE_CHARGING_THRESHOLD = 3 * 60

    parking_space.current_a = 0
    parking_space.total_kw = 0
    before_charging = (TIME_PREPARE_CHARGING_THRESHOLD - 30) / HOUR_TO_SECONDS
    parking_space.save(update_fields=['current_a', 'total_kw'])
    mocked_now.return_value = mock_time + timedelta(hours=before_charging)
    charge_active_orders()

    parking_space.current_a = 10
    parking_space.total_kw = 1
    time_warm_up_charing = (
        FREE_TIME_THRESHOLD - TIME_PREPARE_CHARGING_THRESHOLD
    ) / HOUR_TO_SECONDS
    parking_space.save(update_fields=['current_a', 'total_kw'])
    mocked_now.return_value = mock_time + timedelta(
        hours=before_charging + time_warm_up_charing,
    )
    charge_active_orders()

    parking_space.current_a = 25
    parking_space.total_kw = 5
    time_charing = 2
    parking_space.save(update_fields=['current_a', 'total_kw'])
    mocked_now.return_value = mock_time + timedelta(
        hours=before_charging + time_warm_up_charing + time_charing,
    )
    charge_active_orders()

    assert order.status == ORDER_STATUSES.ACTIVE

    stop_session(user)
    order.refresh_from_db()

    assert order.status == ORDER_STATUSES.FINISHED

    user.profile.refresh_from_db()

    order_info: Order = Order.objects.first()
    order_history: OrderHistoryView = present_order_history(order_info)

    cost_booking = Decimal(order_history.cost_booking)
    cost_kw = Decimal(order_history.cost_kw)
    cost_idle = Decimal(order_history.cost_idle)
    cost_total = Decimal(order_history.cost_total)

    if test_space_mode == SPACE_MODES.TEST:
        assert cost_booking == 0
        assert cost_kw == 0
        assert cost_idle == 0
        assert cost_total == 0

        assert user.profile.balance == money
        assert user.profile.free_seconds == (
            free_seconds
            - (before_charging + time_warm_up_charing + time_charing) * HOUR_TO_SECONDS
        )
    elif test_space_mode == SPACE_MODES.PRODUCTION:
        assert cost_booking == 0
        assert cost_kw == parking_space.price_kw * parking_space.total_kw
        assert cost_idle == 0

        assert user.profile.balance == (money - cost_total)
        assert user.profile.free_seconds == free_seconds


@pytest.mark.django_db(transaction=True)
def test_not_enough_money_to_pay_production_space(mocker, user):
    free_seconds = 1000
    money = 50

    user.profile.free_seconds = free_seconds
    user.profile.save(update_fields=['free_seconds'])
    mock_time = timezone.now()
    mocked_now = mocker.patch(
        'django.utils.timezone.now',
        return_value=mock_time,
    )

    async_to_sync(add_money)(user, money)

    parking_space: ParkingSpace = async_to_sync(
        create_parking_space,
    )(mode=SPACE_MODES.PRODUCTION)
    connector: ParkingSpaceConnector = ParkingSpaceConnector.objects.first()

    params = StartSessionParams(
        id=parking_space.id,
        type=connector.connector_type,
    )
    start_session(params, user)

    mocked_now.return_value = mock_time + timedelta(hours=1)
    charge_active_orders()

    order: Order = Order.objects.first()
    assert order.status == ORDER_STATUSES.NO_MONEY

    user.profile.refresh_from_db()
    assert user.profile.free_seconds == free_seconds
    # В реальности настолько большого минуса не будет, так как крон
    # запускается чаще
    assert user.profile.balance == -50
