from django.conf import settings
from django.db import transaction
from django.utils import timezone
from structlog import get_logger
from structlog.contextvars import bind_contextvars, clear_contextvars

from chat.event.phone_auth import send_phone_auth_response
from chat.event.refill import send_refills
from chat.event.session import send_session_stop, send_sessions_history
from main.models import Order
from main.models.order import ORDER_STATUSES
from main.models.parking_space import SPACE_MODES, SPACE_STATUSES
from main.notifications import (
    once_notify_end_session,
    once_notify_no_money,
    once_notify_less_balance,
    once_notify_no_night_charge,
    once_notify_penalty_time,
    once_notify_reed_not_installed,
)
from main.order_snapshot import OrderSnapshot
from main.utils.datetime_constants import ZONE_INFO

_logger = get_logger(__name__)


def finish_no_money(order: Order) -> None:
    order.finish_no_money()
    send_session_stop(order.user, order.space.id)
    send_phone_auth_response(order.user, order.user)
    send_sessions_history(order.user, order.user)
    send_refills("all")


def charge_prod_mode(order: Order, snapshot: OrderSnapshot) -> None:
    _logger.info(
        'balance at begin in cron_charge_orders',
        order_balance=order.user.profile.balance,
        snapshot_balance=snapshot.get_updated_balance(),
    )

    if snapshot.enough_trial_time:
        return

    order.cost_kw = snapshot.cost_kw
    order.cost_time = snapshot.cost_time
    order.cost_penalty = snapshot.cost_penalty

    order.penalty_seconds = snapshot.current_payed_penalty_seconds
    order.payed_seconds = snapshot.current_payed_seconds
    order.payed_kw = snapshot.current_kw
    order.save(
        update_fields=[
            "cost_kw",
            "cost_time",
            "cost_penalty",
            "payed_seconds",
            "payed_kw",
            "penalty_seconds",
        ]
    )

    if snapshot.is_payed_idle_time:
        once_notify_end_session(order)

    if (
        snapshot.is_night
        and snapshot.is_idle_amperage
        and not snapshot.is_payed_penalty_time
    ):
        once_notify_no_night_charge(order)

    if snapshot.is_payed_penalty_time:
        once_notify_reed_not_installed(order, snapshot.penalty_price_hour)

    if snapshot.is_payed_double_idle_time:
        once_notify_penalty_time(order)

    if snapshot.less_balance:
        once_notify_less_balance(order)

    if snapshot.get_updated_balance() > settings.LESS_BALANCE:
        once_notify_less_balance(order, has_deposited=True)

    if not snapshot.enough_money:
        once_notify_no_money(order)
        order.space.status = SPACE_STATUSES.BUSY
        order.space.save(update_fields=["status"])

    _logger.info(
        'balance at end',
        order_balance=order.user.profile.balance,
        snapshot_balance=snapshot.get_updated_balance()
    )


def charge_test_mode(order: Order, snapshot: OrderSnapshot) -> None:
    if not snapshot.enough_free_seconds:
        finish_no_money(order)


def create_order_snapshot(order: Order):
    space = order.space
    return OrderSnapshot(
        tz=ZONE_INFO,
        start_kw=order.start_kw,
        start_time=order.created_at,
        last_kw=order.last_kw or order.start_kw,
        last_payed_seconds=order.payed_seconds,
        last_payed_penalty_seconds=order.penalty_seconds,
        last_updated_at=order.last_process_time,
        current_time=timezone.now(),
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


@transaction.atomic
def charge(order: Order):
    snapshot = create_order_snapshot(order)

    order.last_kw = snapshot.current_kw
    order.last_process_time = snapshot.current_time
    order.save(update_fields=["last_kw", "last_process_time"])

    if order.space.is_disabled is True:
        return

    if order.space.mode == SPACE_MODES.TEST:
        charge_test_mode(order, snapshot)
    elif order.space.mode == SPACE_MODES.PRODUCTION:
        charge_prod_mode(order, snapshot)
    else:
        _logger.error(f"Unknown space mode {order.space.mode}")
        finish_no_money(order)


def charge_active_orders():
    orders = Order.objects.filter(
        status=ORDER_STATUSES.ACTIVE,
    )
    for order in orders:
        clear_contextvars()
        bind_contextvars(
            order_uuid=str(order.uuid),
            space_uid=str(order.space.uid),
            username=str(order.user.username),
        )
        try:
            charge(order)
        except Exception:
            _logger.exception("Failed to charge")
