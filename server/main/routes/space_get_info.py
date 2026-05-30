from http import HTTPStatus

from django.db.models import Q
from ninja import Router
from ninja.errors import HttpError

from account.auth.bearer_token import AuthBearerDevice
from account.auth.body_token import AuthBodyTokenDevice
from main.models import Camera, Device, ParkingSpace

router = Router(tags=["devices"])


@router.api_operation(
    methods=["GET", "POST"],  # TODO: remove POST: it was for compatibility
    path="/space_get_info/",
    # TODO: удалить AuthBodyTokenDevice когда перейдем на AuthBearerDevice
    auth=[AuthBearerDevice(), AuthBodyTokenDevice()],
)
def space_get_info(request):
    device: Device = request.auth

    if device.space:
        spaces = ParkingSpace.objects.filter(id=device.space.id)
        lot = device.space.lot
        cameras = (
            Camera.objects.filter(
                Q(space=device.space) | Q(send_by_space=device.space),
            )
            .order_by("order_index")
            .all()
        )
    elif device.lot:
        lot = device.space.lot
        spaces = lot.spaces.all()
        cameras = (
            Camera.objects.filter(
                lot=lot,
                space=None,
            )
            .order_by("order_index")
            .all()
        )
    else:
        raise HttpError(
            HTTPStatus.BAD_REQUEST,
            "Устройство не привзяно к станции",
        )

    lot_cameras = [
        {
            "id": cam.id,
            "name": cam.name,
            "ip": cam.ip,
            "rtsp_url": cam.rtsp_url,
        }
        for cam in cameras
    ]

    spaces_list = []
    for space in spaces:
        connectors = [
            {
                "connector_type": connector.connector_type,
                "phases_count": connector.phases_count,
                "max_kw": connector.max_kw,
                "max_a": connector.max_a,
                "relay_pin_number": connector.relay_pin_number,
            }
            for connector in space.connectors.all()
        ]

        spaces_list.append(
            {
                "charge_type": space.charge_type,
                "name": space.name,
                "id": space.id,
                "uid": space.uid,
                "price_kw": space.get_price_kw,
                "price_hour": space.get_price_hour,
                "parklock_mac": space.parklock_mac,
                "parklock_com_port": space.parklock_com_port,
                "meter_com_port": space.meter_com_port,
                "meter_code": space.meter_code,
                "red_pin_number": space.red_pin_number,
                "green_pin_number": space.green_pin_number,
                "blue_pin_number": space.blue_pin_number,
                "parklock_led_pin_number": space.parklock_led_pin_number,
                "parklock_status_pin_number": space.parklock_status_pin_number,
                "park_lock_open_pin_number": space.park_lock_open_pin_number,
                "park_lock_close_pin_number": space.park_lock_close_pin_number,
                "park_lock_serial_number": space.park_lock_serial_number,
                "sonic_led_pin_number": space.sonic_led_pin_number,
                "sonic_trigger_pin_number": space.sonic_trigger_pin_number,
                "sonic_echo_pin_number": space.sonic_echo_pin_number,
                "reed_switch_pin_number": space.reed_switch_pin_number,
                "active_amp": space.active_amp,
                "sonic_floor_distance": space.sonic_floor_distance,
                "sonic_car_distance": space.sonic_car_distance,
                "meter_model": space.meter_model,
                "connectors": connectors,
            },
        )

    return {
        "lot": {
            "uid": lot.uid,
            "spaces": spaces_list,
            "cameras": lot_cameras,
        },
    }
