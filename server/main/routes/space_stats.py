from decimal import Decimal
from http import HTTPStatus
from typing import Optional

import structlog
from django.db import transaction
from django.utils import timezone
from ninja import Router, Schema
from ninja.errors import HttpError

from account.auth.bearer_token import AuthBearerDevice, AuthBearerUser
from chat.event.session import send_session_charging
from main.models import SPACE_STATUSES, Order, ParkingSpace

logger = structlog.getLogger(__name__)
router = Router(tags=["devices"])


class SpaceStat(Schema):
    space_uid: str
    total_kw: float
    current_w: float
    current_v: float
    current_a: float


class ConnectorTypeRes(Schema):
    connector_type: str
    relay_pin_number: Optional[int]


class SpaceStatRes(Schema):
    status: str  # SPACE_STATUSES enum
    mode: str  # SPACE_MODES enum
    price_kwh: str
    price_idle: str
    start_kw: Optional[float]
    start_time: Optional[str]
    payed_time: Optional[str]
    free_seconds: Optional[float]
    is_on: bool
    is_disabled: bool
    connector_type: Optional[ConnectorTypeRes]
    booked_until: Optional[int]


def notify_users(order: Order):
    if not order.user:
        return

    send_session_charging(order.user, order.user)


def get_space_or_404(
    space_id: Optional[int],
    space_uid: Optional[str],
) -> ParkingSpace:
    try:
        if space_id == 0:
            return ParkingSpace.objects.get(uid=space_uid)
        return ParkingSpace.objects.get(id=space_id)
    except ParkingSpace.DoesNotExist as not_found_err:
        raise HttpError(
            HTTPStatus.NOT_FOUND,
            "Парковочное место не найдено",
        ) from not_found_err


@router.post(
    "/space_stat/{space_id}/",
    response=SpaceStatRes,
    auth=[AuthBearerDevice(), AuthBearerUser()],
)
@transaction.atomic
def space_stat(request, space_id: int, data: SpaceStat) -> SpaceStatRes:
    space = get_space_or_404(space_id, data.space_uid)

    space.total_kw = Decimal(data.total_kw)
    space.current_w = Decimal(data.current_w)
    space.current_v = Decimal(data.current_v)
    space.current_a = Decimal(data.current_a)
    space.last_data_update = timezone.now()
    space.save(
        update_fields=[
            "total_kw",
            "current_w",
            "current_v",
            "current_a",
            "last_data_update",
        ],
    )

    order = space.order
    if space.is_disabled and not space.is_manually_disabled:
        if not order:
            space.status = SPACE_STATUSES.AVAILABLE
            space.save(update_fields=["status"])
        elif space.is_booked:
            space.status = SPACE_STATUSES.BOOKED
            space.save(update_fields=["status"])
        else:
            space.enable()

    connector_type = None
    if order is not None:
        try:
            notify_users(order)
        except Exception:
            logger.exception("Failed to notify users about space stats")
        connector_type = ConnectorTypeRes(
            connector_type=order.connector_type.connector_type,
            relay_pin_number=order.connector_type.relay_pin_number,
        )

    payed_time = None
    if order and order.start_payed:
        payed_time = order.start_payed.isoformat()

    return SpaceStatRes(
        status=space.status,
        mode=space.mode,
        price_kwh=str(space.get_price_kw),
        price_idle=str(space.get_price_hour),
        start_kw=order.start_kw if order else None,
        start_time=order.created_at.isoformat() if order else None,
        payed_time=payed_time,
        free_seconds=order.user.profile.free_seconds if order else None,
        is_on=space.is_on,
        is_disabled=space.is_manually_disabled,
        connector_type=connector_type,
        booked_until=int(
            space.booked_until.timestamp(),
        ) if space.booked_until else None,
    )
