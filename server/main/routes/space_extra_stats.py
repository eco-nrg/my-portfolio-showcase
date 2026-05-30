import structlog
from django.db import transaction
from django.http import HttpRequest
from django.utils import timezone
from ninja import Router, Schema

from account.auth.bearer_token import AuthBearerDevice
from chat.event.refill import send_refills
from main.models import ParkingSpace
from main.models.parking_space import SPACE_STATUSES

logger = structlog.get_logger(__name__)
router = Router(tags=['devices'])


class SpaceExtraStat(Schema):
    is_occupied: bool
    is_reed_installed: bool


class SpaceExtraStatRes(Schema):
    detail: str


@router.post(
    path='/space_extra_stat',
    response=SpaceExtraStatRes,
    auth=AuthBearerDevice(),
)
@transaction.atomic
def space_extra_stats(request: HttpRequest, data: SpaceExtraStat):
    space: ParkingSpace = request.auth.space  # type: ignore
    should_notify = False

    if space.status == SPACE_STATUSES.AVAILABLE and data.is_occupied:
        space.status = SPACE_STATUSES.BUSY
        space.save(update_fields=["status"])
        should_notify = True

    if space.is_occupied != data.is_occupied:
        logger.info(
            'Change is_occupied',
            cur_is_occupied=space.is_occupied,
            new_is_occupied=data.is_occupied,
            space=space.uid,
            device=request.auth.name,  # type: ignore
            api='space_extra_stat',
        )
        should_notify = True

    if data.is_reed_installed and not space.is_reed_installed:
        space.reed_install_time = timezone.now()

    space.is_occupied = data.is_occupied
    space.is_reed_installed = data.is_reed_installed
    space.save(update_fields=[
        'is_occupied',
        'is_reed_installed',
        'reed_install_time',
    ])

    if should_notify:
        send_refills('all')

    return SpaceExtraStatRes(
        detail='Successfully updated extra stats',
    )
