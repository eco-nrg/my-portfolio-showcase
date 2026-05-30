import sys
import time
from typing import Dict

import RPi.GPIO

from kv.redis_kv import models
from py_scripts.config import get_settings, settings_loader
from py_scripts.custom_logger import logger
from py_scripts.park_lock.parklock_logic import ParkLock

SETTINGS = get_settings()

PARK_LOCK_STATUS_PIN = SETTINGS.parklock_status_pin if SETTINGS else -1
PARK_LOCK_OPEN_PIN = SETTINGS.park_lock_open_pin if SETTINGS else -1
PARK_LOCK_CLOSE_PIN = SETTINGS.park_lock_close_pin if SETTINGS else -1

PARK_LOCK_PIN_STATUS: Dict["bool", "str"] = {
    False: "UNLOCKED",
    True: "LOCKED",
}

RPi.GPIO.setmode(RPi.GPIO.BOARD)

RPi.GPIO.setup(PARK_LOCK_STATUS_PIN or -1, RPi.GPIO.IN)
RPi.GPIO.setup(PARK_LOCK_OPEN_PIN or -1, RPi.GPIO.OUT)
RPi.GPIO.setup(PARK_LOCK_CLOSE_PIN or -1, RPi.GPIO.OUT)


def check_status() -> None:
    logger.info("Checking status")
    status_pin = RPi.GPIO.input(PARK_LOCK_STATUS_PIN or -1)
    status = PARK_LOCK_PIN_STATUS.get(status_pin)
    logger.info(f"Status: {status}")
    models.set_prop_value("PARKLOCK__LAST_STATUS", status)


def initialize() -> None:
    check_status()
    RPi.GPIO.output(PARK_LOCK_CLOSE_PIN or -1, RPi.GPIO.HIGH)
    RPi.GPIO.output(PARK_LOCK_OPEN_PIN or -1, RPi.GPIO.HIGH)


def lock() -> None:
    logger.info("Trying to lock")
    RPi.GPIO.output(PARK_LOCK_CLOSE_PIN or -1, RPi.GPIO.LOW)
    time.sleep(0.1)
    RPi.GPIO.output(PARK_LOCK_CLOSE_PIN or -1, RPi.GPIO.HIGH)
    time.sleep(10)
    check_status()


def unlock() -> None:
    logger.info("Trying to unlock")
    RPi.GPIO.output(PARK_LOCK_OPEN_PIN or -1, RPi.GPIO.LOW)
    time.sleep(0.1)
    RPi.GPIO.output(PARK_LOCK_OPEN_PIN or -1, RPi.GPIO.HIGH)
    time.sleep(10)
    check_status()


def run_loop() -> None:
    park_lock = ParkLock(
        lock_fn=lock,
        unlock_fn=unlock,
        init_fn=initialize,
        db=models,
        settings_loader=settings_loader,
    )

    while True:
        time.sleep(1)
        park_lock.check()


if __name__ == "__main__":
    args = sys.argv

    if len(args) <= 1:
        raise Exception("No arguments")

    if args[-1] == '-init':
        initialize()
    elif args[-1] == '-lock':
        # Будьте осторожны,
        # не будет проверки с лидара, ультрасоника на расстояние
        initialize()
        lock()
    elif args[-1] == '-unlock':
        # Будьте осторожны,
        # не будет проверки с лидара, ультрасоника на расстояние
        initialize()
        unlock()
    elif args[-1] == '-loop':
        run_loop()
    else:
        raise Exception("Invalid key" + str(args[-1]))
