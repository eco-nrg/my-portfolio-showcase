import time
from typing import Optional

from pydantic import BaseModel

from chat.presenters.helpers import datetime_as_ms, resolve_media_url
from main.models import Camera, Order


class OrderInfoView(BaseModel):
    id: int
    connector_type: str
    created_at: int
    start_payed: Optional[int]
    cash: float
    total_kwh: float
    am: float
    current_kwh: float
    current_v: float
    selected_camera: int
    cam_1: Optional[str]
    cam_2: Optional[str]
    status: str
    idle_amperage_threshold: float


def present_order(order: Order):
    space = order.space

    space_cam = Camera.objects.filter(space=space).first()
    lot_cam = Camera.objects.filter(lot=space.lot, space=None).first()

    camera_url_tmpl = '{img!s}?t={t!s}'

    cam1 = (
        resolve_media_url(
            camera_url_tmpl.format(
                img=lot_cam.image,
                t=time.mktime(lot_cam.last_image_update.timetuple()),
            ),
        )
        if lot_cam
        else None
    )

    cam2 = (
        resolve_media_url(
            camera_url_tmpl.format(
                img=space_cam.image,
                t=time.mktime(space_cam.last_image_update.timetuple()),
            ),
        )
        if space_cam
        else None
    )

    total_kw = order.last_kw - order.start_kw if order.last_kw else 0

    return OrderInfoView(
        id=space.id,
        connector_type=order.connector_type.connector_type,
        created_at=datetime_as_ms(order.created_at),
        start_payed=datetime_as_ms(order.start_payed),
        cash=order.cost_total,
        total_kwh=total_kw,
        am=order.space.current_a,
        current_kwh=order.space.current_w / 1000,
        current_v=order.space.current_v,
        selected_camera=1,
        cam_1=cam1,
        cam_2=cam2,
        status=order.status,
        idle_amperage_threshold=space.idle_amperage_threshold,
    )
