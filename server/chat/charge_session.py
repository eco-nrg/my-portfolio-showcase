from typing import Optional

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from pydantic import BaseModel

from account.models import Profile
from chat.presenters.order import OrderInfoView, present_order
from main.models import (
    ORDER_STATUSES,
    SPACE_STATUSES,
    Camera,
    Order,
    ParkingSpace,
    ParkingSpaceConnector,
)
from main.models.booking import Booking
from main.models.parking_space import SPACE_MODES
from payments.models.operation import Operation, OperationAction, OperationType

DEFAULT_TRIAL_TIME = 5 * 60  # 5 min in seconds


class StartSessionParams(BaseModel):
    id: int
    type: str

    @property
    def space_id(self):
        return self.id

    @property
    def connector_type(self):
        return self.type


class StartSessionError(Exception):
    msg: str = "Ошибка активации зарядки"

    def __init__(self, msg: str) -> None:
        self.msg = msg


ALLOWED_SPACE_MODE = frozenset((SPACE_MODES.TEST, SPACE_MODES.PRODUCTION))


@transaction.atomic
def start_session(params: StartSessionParams, user: User) -> Order:
    user.refresh_from_db()
    user.profile.refresh_from_db()
    profile: Profile = user.profile
    try:
        space: ParkingSpace = ParkingSpace.objects.get(id=params.space_id)
    except ParkingSpace.DoesNotExist as not_found_err:
        raise StartSessionError(
            "Парковочное место не найдено",
        ) from not_found_err

    if space.is_disabled:
        raise StartSessionError("Место не работает")
    if space.is_on:
        raise StartSessionError("Место не свободно")

    booking: Optional[Booking] = space.booking
    if (
        space.status == SPACE_STATUSES.BOOKED
        and booking is not None
        and booking.user.id != user.id
    ):
        raise StartSessionError("Место забронировано")

    if space.mode not in ALLOWED_SPACE_MODE:
        raise StartSessionError("Станция недоступна для активации")

    if not user.operations.exists() and profile.trial_time == 0:
        profile.trial_time = DEFAULT_TRIAL_TIME
        profile.save(update_fields=["trial_time"])

    if space.mode == SPACE_MODES.TEST and profile.free_seconds <= 0:
        raise StartSessionError("Недостаточно бесплатных минут")
    if (
        space.mode == SPACE_MODES.PRODUCTION and
        profile.balance <= 0
    ):
        raise StartSessionError("Недостаточно средств на счете")

    user_booking: Booking = (
        user.bookings.filter(
            _is_active=True,
        )
        .order_by("-created_at")
        .first()
    )
    if user_booking is not None and user_booking != booking:
        # можно активировать только забронированную станцию
        raise StartSessionError(
            "Нельзя активировать станцию, имея другую забронированную",
        )

    if user.orders.filter(
        Q(status=ORDER_STATUSES.ACTIVE) | Q(status=ORDER_STATUSES.PARKING),
    ).exists():
        raise StartSessionError(
            "Одновременно может быть активная только одна сессия зарядки",
        )

    # TODO: проверяем соответсвие коннектора активации коннектору бронирования?
    # Вообще зачем мы спрашиваем коннектор?
    # Мы же и так понимаем какой использует клиент

    try:
        connector = space.connectors.get(connector_type=params.connector_type)
    except ParkingSpaceConnector.DoesNotExist as not_found_err:
        raise StartSessionError("Коннектор не найден") from not_found_err

    order = Order()
    order.user = user
    order.space = space
    order.start_kw = space.total_kw
    order.last_kw = space.total_kw
    order.status = ORDER_STATUSES.ACTIVE
    order.connector_type = connector
    order.created_at = timezone.now()
    order.last_process_time = order.created_at
    if space.mode == SPACE_MODES.PRODUCTION:
        # На продакшене все только за деньги
        order.start_payed = order.created_at
    space_cam = Camera.objects.filter(space=space).first()
    if space_cam is not None:
        order.selected_camera = space_cam
    else:
        lot_cam = Camera.objects.filter(lot=space.lot, space=None).first()
        if lot_cam is not None:
            order.selected_camera = lot_cam

    space.status = SPACE_STATUSES.CHARGING
    space.save(update_fields=["status"])

    order.save()
    if booking:
        booking.activated_at = timezone.now()
        booking.order = order

        if space.mode == SPACE_MODES.TEST and not profile.can_book:
            # Когда пользователь активирует свою забронированную станцию, то ему
            # возвращаются бесплатные секунды, зарезервированые на бронирование.
            profile.free_seconds += int(booking.left_time.total_seconds())
        elif space.mode == SPACE_MODES.PRODUCTION and profile.can_book:
            booking.cost = space.price_hour
            Operation.objects.create(
                kind=OperationType.CREDIT,
                action=OperationAction.BOOKING,
                amount=space.price_hour,
                created_at=booking.created_at,
                user=booking.user,
                booking=booking,
            )

        profile.can_book = False
        booking.save(update_fields=["activated_at", "order", "cost"])
        profile.save(update_fields=["can_book", "free_seconds"])

    return order


def get_active_session(user: User) -> Optional[OrderInfoView]:
    order = Order.objects.filter(
        Q(user=user),
        Q(status=ORDER_STATUSES.ACTIVE) | Q(status=ORDER_STATUSES.PARKING),
    ).first()
    if order is None:
        return None
    return present_order(order)
