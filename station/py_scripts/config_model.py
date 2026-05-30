from typing import List, Optional

from pydantic import BaseModel, BaseSettings


class Camera(BaseModel):
    id: Optional[str]
    rtsp_url: Optional[str]


class Settings(BaseSettings):
    # TODO: убрать значения после
    api_url: Optional[str]
    api_token: Optional[str]

    space_id: Optional[int]
    space_uid: Optional[str]

    com_port: Optional[str]
    serial_number: Optional[int]

    parklock_mac: Optional["str"] = None
    parklock_com_port: Optional["str"] = None
    park_lock_serial_number: Optional["str"] = None
    park_lock_open_pin: Optional["int"] = None
    park_lock_close_pin: Optional["int"] = None

    red_pin: Optional["int"] = None
    green_pin: Optional["int"] = None
    blue_pin: Optional["int"] = None

    turn_one_pin: Optional["int"] = None
    turn_two_pin: Optional["int"] = None

    active_amp: Optional[float] = 12
    reed_switch_pin: Optional[int] = 29
    parklock_status_pin: Optional[int]
    parklock_pin: Optional[int] = 37
    sonic_led_pin: Optional[int] = 35
    sonic_trigger_pin: Optional[int] = 10
    sonic_echo_pin: Optional[int] = 8
    sonic_floor_distance: Optional["int"] = None
    sonic_car_distance: Optional["int"] = None
    meter_model: Optional[str]
    connector_type: Optional[str]

    cameras: List[Camera] = []
