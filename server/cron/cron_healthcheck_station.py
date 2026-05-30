import datetime

import structlog
from django.db import transaction
from django.utils import timezone

from chat.event.refill import send_refills
from main.models import ParkingSpace, Order, ORDER_STATUSES
from main.models.parking_space import SPACE_STATUSES
from main.utils.datetime_constants import (
    START_TIMEOUT,
    STOP_SESSION_TIME,
)

_logger = structlog.getLogger(__name__)


@transaction.atomic
def _change_space_status(space: ParkingSpace) -> None:
    if space.status == SPACE_STATUSES.AVAILABLE and space.is_occupied:
        space.status = SPACE_STATUSES.BUSY
        space.save(update_fields=["status"])

    if space.status == SPACE_STATUSES.BUSY and not space.is_occupied:
        space.status = SPACE_STATUSES.AVAILABLE
        space.save(update_fields=["status"])


@transaction.atomic
def _stop_session(space: ParkingSpace) -> None:
    now = timezone.now()
    delta_reed_install_time = now - space.reed_install_time

    order: Order = space.orders.filter(
        status=ORDER_STATUSES.ACTIVE,
    ).order_by(
        "-created_at",
    ).first()
    if order:
        delta_start_order = now - order.created_at

        if (
            space.is_reed_installed and
            not space.is_occupied and
            space.current_a < 1.0 and
            delta_start_order >= START_TIMEOUT and
            delta_reed_install_time >= STOP_SESSION_TIME
        ):
            order.finish(ORDER_STATUSES.FINISHED)


@transaction.atomic
def _check_and_disable_space(space: ParkingSpace) -> bool:
    now = timezone.now()
    dt = now - space.last_data_update
    msg = {
        'dt': int(dt.total_seconds()),
        'space_uid': space.uid,
        'status': space.status,
        'is_on': space.is_on,
        'a': float(space.current_a),
        'v': float(space.current_v),
        'w': float(space.current_w),
        'kw': float(space.total_kw),
    }

    if space.is_disabled:
        _logger.debug('station_disabled', **msg)
    else:
        if dt >= datetime.timedelta(minutes=2):
            _logger.info('deactivate station', **msg)
            space.disable()
            return True
        else:
            _logger.debug('station_ok', **msg)
            _stop_session(space)
            _change_space_status(space)

    return False


def health_check_stations():
    spaces = ParkingSpace.objects.all()
    _logger.debug('health_check_stations', n_spaces=spaces.count())
    any_change = False
    for space in spaces:
        any_change = _check_and_disable_space(space) or any_change

    if any_change:
        send_refills('all')
