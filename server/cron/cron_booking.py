"""
Обновление статуса Бронирования у Станций.

Факт бронирования отражается в записи о бронировании.
Статус бронирования автоматически вычислется по времени, но
так же статус `BO` выставляется у Станции (ParkingSpace),
который нужно обновить.

Кроме того надо разослать уведомления о том, что бронирвоание просрочилось
и Станция освободилась.

В будущем можно переделать на Celery scheduler.
"""

from datetime import datetime, timedelta, timezone
import structlog
from django.db import transaction

from account.models.profile import Profile
from chat.booking import BOOKING_DURATION
from chat.event import send_refills
from chat.event.booking import send_cancel_bookings
from chat.event.phone_auth import send_phone_auth_response
from main.models.booking import Booking, BookingStatus
from main.models.parking_space import SPACE_MODES, SPACE_STATUSES, ParkingSpace
from payments.models.operation import Operation, OperationAction, OperationType


PAID_TIME = timedelta(minutes=15)
logger = structlog.get_logger(__name__)


def _set_booking_cost(booking: Booking, parking_space: ParkingSpace):
    # Говорим, что с этого момента бронирование платное
    booking.cost = parking_space.price_hour
    booking.save(update_fields=["cost"])
    # В день можно бронировать один раз, поэтому сразу выставляем флаг
    # Этот флаг обратно поднимает cron задача,
    # которая выдает бесплатное время
    profile: Profile = booking.user.profile
    profile.can_book = False

    if parking_space.mode == SPACE_MODES.TEST:
        profile.free_seconds -= int(BOOKING_DURATION.total_seconds())
    elif parking_space.mode == SPACE_MODES.PRODUCTION:

        Operation.objects.create(
            kind=OperationType.CREDIT,
            action=OperationAction.BOOKING,
            amount=parking_space.price_hour,
            created_at=booking.created_at,
            user=booking.user,
            booking=booking,
        )

    profile.save(update_fields=["can_book", "free_seconds"])


@transaction.atomic
def update_and_notify_booking_status():
    any_changed = False
    spaces = ParkingSpace.objects.filter(
        status=SPACE_STATUSES.BOOKED,
    )
    for space in spaces:
        overdue_bookings = space.bookings.filter(
            _status=BookingStatus.OVERDUE,
        )
        for overdue_booking in overdue_bookings:
            overdue_booking.cancel()
            any_changed = True
            send_cancel_bookings(overdue_booking.user)
            send_phone_auth_response(overdue_booking.user, overdue_booking.user)
            logger.info(
                'Autoclose booking',
                space=space.uid,
                booking=overdue_booking.uuid,
                user=overdue_booking.user.username,
            )

        active_bookings = space.bookings.filter(
            _status=BookingStatus.ACTIVE_FREE,
        )
        for active_booking in active_bookings:
            current_time = datetime.now(timezone.utc)
            if current_time >= active_booking.created_at + PAID_TIME:
                _set_booking_cost(active_booking, space)
                logger.info(
                    "Booking became paid",
                    space=space.uid,
                    booking=active_booking.uuid,
                    user=active_booking.user.username,
                )

    if any_changed:
        send_refills('all')
