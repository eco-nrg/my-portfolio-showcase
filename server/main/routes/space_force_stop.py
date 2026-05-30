from typing import Optional

import structlog
from ninja import Router

from account.auth.bearer_token import AuthBearerDevice
from chat.event.phone_auth import send_phone_auth_response
from chat.event.refill import send_refills
from chat.event.session import send_session_stop, send_sessions_history
from main.models import ORDER_STATUSES, ParkingSpace

logger = structlog.get_logger(__name__)
router = Router(tags=['devices'])


def notify_users(order):
    try:
        send_refills('all')
        send_session_stop(order.user, order.space.id)
        send_phone_auth_response(order.user, order.user)
        send_sessions_history(order.user, order.user)
    except Exception:
        logger.exception('Failed to notify users about force_stop')


def force_stop(space: Optional[ParkingSpace]):
    if space is None:
        return None
    order = space.order
    if order is None:
        return None

    order.finish(ORDER_STATUSES.FINISHED)
    notify_users(order)
    return order


@router.post(
    path='/space_force_stop',
    auth=AuthBearerDevice(),
)
def force_stop_handler(request):
    with structlog.contextvars.bound_contextvars(
        api='space_force_stop',
        device=request.auth.name,
    ):
        space = request.auth.space
        order = force_stop(space)

    if order is None:
        return {
            'space_id': None,
            'order_id': None,
            'status': None,
        }

    return {
        'space_id': space.id,
        'order_id': order.uuid,
        'status': order.status,
    }
