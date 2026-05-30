from decimal import Decimal

from django.utils import timezone

from chat.event.session import send_session_charging
from main.models.camera import Camera
from main.models.order import ORDER_STATUSES, Order
from main.models.parking_space import SPACE_MODES, SPACE_STATUSES, ParkingSpace


def _create_parking_order(old_order: Order, space: ParkingSpace):
    order = Order()
    order.user = old_order.user
    order.space = space
    order.start_kw = Decimal(0)
    order.last_kw = Decimal(0)
    order.end_kw = Decimal(0)
    order.status = ORDER_STATUSES.PARKING

    order.connector_type = old_order.connector_type
    order.created_at = timezone.now()
    order.last_process_time = order.created_at

    if space.mode == SPACE_MODES.PRODUCTION:
        order.start_payed = order.created_at
    space_cam = Camera.objects.filter(space=space).first()
    if space_cam is not None:
        order.selected_camera = space_cam
    else:
        lot_cam = Camera.objects.filter(lot=space.lot, space=None).first()
        if lot_cam is not None:
            order.selected_camera = lot_cam
    order.save()
    send_session_charging(order.user, order.user)


def start_charging_parking():
    occupied_spaces = ParkingSpace.objects.filter(status=SPACE_STATUSES.BUSY)

    for occupied_space in occupied_spaces:
        last_order: Order = occupied_space.orders.order_by(
            "-created_at",
        ).first()

        if last_order.status == ORDER_STATUSES.FINISHED:
            _create_parking_order(last_order, occupied_space)
