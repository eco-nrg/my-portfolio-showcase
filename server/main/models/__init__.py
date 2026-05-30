from typing import Any, Dict
from .booking import Booking, BookingStatus
from .camera import Camera, get_image_path
from .city import City
from .connector import ParkingSpaceConnector
from .device import Device
from .order import ORDER_STATUSES, Order
from .parking_lot import ParkingLot, get_map_path
from .parking_lot_provider import ProviderParkingLot, ProviderType
from .parking_space import SPACE_STATUSES, ParkingSpace
from .parking_space_stat import ParkingSpaceStat
from .provider import Provider
from .sms_send import SmsSend


def get_empty_dict() -> Dict[Any, Any]:
    return {}


__all__ = [
    'Booking',
    'BookingStatus',
    'Camera',
    'get_image_path',
    'City',
    'ParkingSpaceConnector',
    'Provider',
    'ProviderParkingLot',
    'ProviderType',
    'Device',
    'ORDER_STATUSES',
    'Order',
    'get_empty_dict',
    'ParkingLot',
    'get_map_path',
    'SPACE_STATUSES',
    'ParkingSpace',
    'ParkingSpaceStat',
    'SmsSend',
]
