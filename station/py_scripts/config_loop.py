import os
import time
from typing import Any, Dict, NoReturn, Optional

import requests
from config_model import Camera, Settings
from custom_logger import logger

from kv.redis_kv import models
from py_scripts.hash import get_hash_value

DEVICE_KEY = os.environ["DEVICE_KEY"]
API_URL = os.environ["API_URL"]
API_INFO_URL = "/main/api/v1/space_get_info/"

config = None
last_update = None


def get_space_info() -> Optional[Dict[Any, Any]]:
    try:
        res = requests.post(
            f"{API_URL}{API_INFO_URL}",
            {"token": DEVICE_KEY},
            headers={"Authorization": f"Bearer {DEVICE_KEY}"},
        )
        res.raise_for_status()
        return res.json()
    except Exception:
        logger.exception("Failed to get config at /main/api/v1/space_get_info/")
    return None


def update_config() -> None:
    config = get_space_info()
    if config is None:
        return
    settings = Settings(
        api_url=API_URL,
        api_token=DEVICE_KEY,
        space_id=config["lot"]["spaces"][0]["id"],
        space_uid=config["lot"]["spaces"][0]["uid"],
        red_pin=config["lot"]["spaces"][0]["red_pin_number"],
        green_pin=config["lot"]["spaces"][0]["green_pin_number"],
        blue_pin=config["lot"]["spaces"][0]["blue_pin_number"],
        parklock_mac=config["lot"]["spaces"][0].get("parklock_mac"),
        parklock_com_port=config["lot"]["spaces"][0].get("parklock_com_port"),
        park_lock_serial_number=config["lot"]["spaces"][0].get(
            "park_lock_serial_number",
        ),
        park_lock_open_pin=config["lot"]["spaces"][0].get(
            "park_lock_open_pin_number",
        ),
        park_lock_close_pin=config["lot"]["spaces"][0].get(
            "park_lock_close_pin_number",
        ),
        parklock_pin=config["lot"]["spaces"][0].get(
            "parklock_led_pin_number",
        ),
        parklock_status_pin=config["lot"]["spaces"][0].get(
            "parklock_status_pin_number",
            16,
        ),
        sonic_led_pin=config["lot"]["spaces"][0].get(
            "sonic_led_pin_number",
        ),
        sonic_trigger_pin=config["lot"]["spaces"][0].get(
            "sonic_trigger_pin_number",
        ),
        sonic_echo_pin=config["lot"]["spaces"][0].get(
            "sonic_echo_pin_number",
        ),
        reed_switch_pin=config["lot"]["spaces"][0].get(
            "reed_switch_pin_number",
        ),
        sonic_floor_distance=config["lot"]["spaces"][0].get(
            "sonic_floor_distance",
        ),
        sonic_car_distance=config["lot"]["spaces"][0].get(
            "sonic_car_distance",
        ),
        com_port=config["lot"]["spaces"][0]["meter_com_port"],
        serial_number=config["lot"]["spaces"][0]["meter_code"],
        meter_model=config["lot"]["spaces"][0]["meter_model"],
        connector_type=config["lot"]["spaces"][0]["connectors"][0].get(
            "connector_type",
        ),
        cameras=[
            Camera(id=camera["id"], rtsp_url=camera["rtsp_url"])
            for camera in config["lot"].get("cameras", [])
        ],
    )
    settings_value = settings.json()
    logger.info("Settings: ", settings=settings_value)
    models.create("settings", settings_value)
    models.create("settings_cache", get_hash_value(settings_value))


def main() -> NoReturn:
    while True:
        update_config()
        time.sleep(10)


if __name__ == "__main__":
    main()
