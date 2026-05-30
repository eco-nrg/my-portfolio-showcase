from datetime import timedelta, datetime
from decimal import Decimal
from typing import Optional

from django.db.models import Q
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from pydantic import BaseModel

from account.models import Profile
from chat.presenters.helpers import datetime_as_ms
from main.models import (
    SPACE_STATUSES,
    Booking,
    ParkingSpace,
    ParkingSpaceConnector,
)
from main.models.order import ORDER_STATUSES
from main.models.parking_space import SPACE_MODES

BOOKING_DURATION = timedelta(hours=1)
BOOKING_DURATION_TEXT = "1 час"


class BookSpaceParams(BaseModel):
    space_id: int
    connector_type: str


class BookSpaceResult(BaseModel):
    booking_id: str
    space_id: int
    connector_type: str
    created_at: int
    until: int
    cost: str


class BookingError(Exception):
    msg: str

    def __init__(self, msg: str = "Ошибка бронирования") -> None:
        self.msg = msg


def _present_booking_result(booking: Booking) -> BookSpaceResult:
    return BookSpaceResult(
        booking_id=str(booking.uuid),
        space_id=booking.space.id,
        connector_type=booking.connector.connector_type,
        created_at=int(booking.created_at.timestamp()),
        until=int(booking.booked_until.timestamp()),
        cost=str(booking.cost),
    )


@transaction.atomic
def book_space(user: User, params: BookSpaceParams) -> BookSpaceResult:
    """
    Бронирование места.

    Обязательно всё должно происходить в рамках одной транзакции
    Так как во время создания брони может сломаться станция,
    которую обновляют в фоне. У пользователя могут забрать
    деньги/бесплатное время в фоне

    0. check user is authenticated
    1. check space is active, i.e. not booked, not used
    2. check user is allowed to book a space
        a. user doesn't book today
        b. user isn't using any space right now
        c. user's profile is complete
        d. user has 60 free minutes
    3. create a book entry
    """
    profile: Profile = user.profile
    profile.refresh_from_db()

    try:
        space: ParkingSpace = ParkingSpace.objects.get(id=params.space_id)
    except ParkingSpace.DoesNotExist as not_found_err:
        raise BookingError("Парковочное место не найдено") from not_found_err

    # if not profile.is_filled:
    #     raise BookingError(
    #         "Профиль должен быть заполнен, чтобы забронировать место",
    #     )

    if space.mode == SPACE_MODES.TEST:
        if profile.free_seconds < BOOKING_DURATION.total_seconds():
            msg = "Недостаточно бесплатного времени для  бронирования на {0}"
            raise BookingError(msg.format(BOOKING_DURATION_TEXT))
    elif space.mode == SPACE_MODES.PRODUCTION:
        if profile.balance < space.price_hour:
            msg = "Недостаточно средств на счете для бронирования на {0}"
            raise BookingError(msg.format(BOOKING_DURATION_TEXT))
    else:
        raise BookingError("Невозможно забронировать выбранную станцию")

    if user.bookings.filter(_is_active=True).exists():
        raise BookingError("Можно бронировать только одну станцию")

    if user.orders.filter(
        Q(status=ORDER_STATUSES.ACTIVE) | Q(status=ORDER_STATUSES.PARKING),
    ).exists():
        raise BookingError(
            "Нельзя бронировать станцию, пока есть активная сессия зарядки",
        )

    if not profile.can_book:
        raise BookingError("В день можно бронировать один раз")

    if space.is_booked:
        raise BookingError("Парковочное место забронированно")
    if space.is_disabled:
        raise BookingError("Парковочное место выключено")
    if space.is_on:
        raise BookingError("Парковочное место занято")
    if space.status == SPACE_STATUSES.BUSY:
        raise BookingError("Парковочное место занято")
    if space.status != SPACE_STATUSES.AVAILABLE:
        raise BookingError("Парковочное место недоступно")

    try:
        connector = space.connectors.get(
            connector_type=params.connector_type,
        )
    except ParkingSpaceConnector.DoesNotExist as not_found_err:
        raise BookingError("Коннектор не найден") from not_found_err

    booking = Booking()
    booking.user = user
    booking.space = space
    booking.created_at = datetime.now(timezone.utc)
    booking.booked_until = datetime.now(timezone.utc) + BOOKING_DURATION
    booking.connector = connector
    booking.cost = Decimal(0)
    booking.save()

    space.status = SPACE_STATUSES.BOOKED
    space.save(update_fields=["status"])

    return _present_booking_result(booking)


def get_active_booking(user: User) -> Optional[BookSpaceResult]:
    booking = user.bookings.filter(_is_active=True).first()
    if booking is None:
        return None

    return _present_booking_result(booking)


class CancelBookingParams(BaseModel):
    booking_id: str


class CancelBookingResult(BaseModel):
    booking_id: str
    space_id: str
    cancelled_at: int
    created_at: int
    duration: int


@transaction.atomic
def cancel_bookings(user: User):
    for booking in user.bookings.all():
        booking.cancel()


@transaction.atomic
def cancel_booking(user: User, params: CancelBookingParams):
    # TODO: сейчас не используется, так как не имеет особого смысла
    #  У пользователя может быть только ОДНО брониварование
    #  Поэтому нет смысла запрашивать id, а проще все брони закрыть.
    #  Испольуезм сейчас cancel_bookings
    booking: Optional[Booking] = (
        user.bookings.filter(
            _is_active=True,
            id=params.booking_id,
        )
        .order_by("-created_at")
        .first()
    )

    if booking is None:
        raise BookingError("Бронирование не найдено")

    booking.cancel()

    return CancelBookingResult(
        space_id=booking.space.id,
        booking_id=str(booking.uuid),
        cancelled_at=datetime_as_ms(booking.cancelled_at),
        created_at=datetime_as_ms(booking.created_at),
        duration=booking.actual_duration.total_seconds(),
    )
