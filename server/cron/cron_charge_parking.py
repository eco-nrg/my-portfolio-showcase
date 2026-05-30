from datetime import datetime, timezone

from structlog import get_logger

from chat.event.session import send_session_charging
from main.models.order import ORDER_STATUSES, Order
from main.models.parking_space import SPACE_MODES, ParkingSpace
from main.notifications import (
    once_notify_no_night_charge,
    once_notify_penalty_time,
    once_notify_reed_not_installed,
)
from main.order_snapshot import OrderSnapshot
from main.utils.datetime_constants import ZONE_INFO

_logger = get_logger(__name__)
TIME_TO_LEAVE_PARKING_SPACE = 60 * 10

def charge(order: Order):
    space: ParkingSpace = order.space
    space.refresh_from_db()

    if not space.is_occupied:
        order.finish(ORDER_STATUSES.FINISHED_PARKING)
        return

    order_snapshot = OrderSnapshot(
        tz=ZONE_INFO,
        start_kw=order.start_kw,
        start_time=order.created_at,
        last_kw=order.last_kw or order.start_kw,
        last_payed_seconds=order.payed_seconds,
        last_payed_penalty_seconds=order.penalty_seconds,
        last_updated_at=order.last_process_time,
        current_time=datetime.now(tz=timezone.utc),
        current_kw=space.total_kw,
        current_a=space.current_a,
        current_is_occupied=space.is_occupied,
        current_is_reed_installed=space.is_reed_installed,
        price_kw=space.price_kw,
        price_hour=space.price_hour,
        free_seconds=order.user.profile.free_seconds,
        balance=order.user.profile.balance,
        trial_time=order.user.profile.trial_time,
        idle_amperage_threshold=space.idle_amperage_threshold,
    )

    _logger.info(
        'balance at begin',
        order_balance=order.user.profile.balance,
        snapshot_balance=order_snapshot.get_updated_balance(),
    )

    order.last_process_time = order_snapshot.current_time
    order.save(update_fields=["last_process_time"])
    _logger.info(
        "parking order is processing for",
        order = order,
        processing_time = order.processing_time
    )

    if space.is_disabled:
        return

    if space.mode == SPACE_MODES.PRODUCTION and order.processing_time.seconds > TIME_TO_LEAVE_PARKING_SPACE:
        _logger.info(
            "parking order being accounted",
            order=order,
            processing_time=order.processing_time
        )
        cost_penalty = max(order_snapshot.cost_penalty, order_snapshot.cost_parking)
        penalty_seconds = max(
            order_snapshot.current_payed_penalty_seconds,
            order_snapshot.current_payed_parking_seconds,
        )
        need_send = cost_penalty > order.cost_penalty

        order.cost_penalty = cost_penalty
        order.penalty_seconds = penalty_seconds
        order.save(
            update_fields=[
                "cost_penalty",
                "penalty_seconds",
            ]
        )

        if order_snapshot.is_payed_parking_time:
            once_notify_penalty_time(order)

        if (
            order_snapshot.is_night
            and order_snapshot.is_idle_amperage
            and not order_snapshot.is_payed_penalty_time
        ):
            once_notify_no_night_charge(order)

        if order_snapshot.is_payed_penalty_time:
            once_notify_reed_not_installed(order, order_snapshot.penalty_price_hour)

        if need_send:
            send_session_charging(order.user, order.user)

        _logger.info(
            'balance at end',
            order_balance=order.user.profile.balance,
            snapshot_balance=order_snapshot.get_updated_balance(),
        )


def charge_parking():
    parking_orders = Order.objects.filter(
        status=ORDER_STATUSES.PARKING,
    )
    for parking_order in parking_orders:
        try:
            charge(parking_order)
        except Exception:
            _logger.exception(
                "Unable to charge parking order",
                parking_order=parking_order,
            )
