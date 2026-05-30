import serial
import sys
import time

from config import settings_loader, get_settings

from kv.redis_kv import models
from py_scripts.custom_logger import logger
from py_scripts.park_lock.parklock_logic import ParkLock

settings = get_settings()
park_lock_port = settings.parklock_com_port if settings else ''


def connect():
    global park_lock
    park_lock = serial.Serial(park_lock_port, 9600, timeout=3)
    time.sleep(0.1)


def initialize():
    logger.info("Trying to initialize")
    connect()
    logger.info("Trying to get status")
    park_lock.write("status".encode())
    time.sleep(0.2)
    answer = park_lock.readline().decode()
    status = answer.split(" ")[0]
    if status == "lock":
        models.set_prop_value("PARKLOCK__LAST_STATUS", "LOCKED")
    if status == "unlock":
        models.set_prop_value("PARKLOCK__LAST_STATUS", "UNLOCKED")


def lock():
    connect()
    logger.info("Trying to lock")
    park_lock.write("on".encode())
    time.sleep(0.2)
    answer = park_lock.readline().decode()
    if answer == "lock":
        logger.info("Unlocked")
        logger.info("Locked")
        models.set_prop_value("PARKLOCK__LAST_STATUS", "LOCKED")


def unlock():
    connect()
    logger.info("Trying to unlock")
    park_lock.write("off".encode())
    time.sleep(0.2)
    answer = park_lock.readline().decode()
    if answer == "unlock":
        logger.info("Unlocked")
        models.set_prop_value("PARKLOCK__LAST_STATUS", "UNLOCKED")


def run_loop():
    park_lock_wrapper = ParkLock(
        lock_fn=lock,
        unlock_fn=unlock,
        init_fn=initialize,
        db=models,
        settings_loader=settings_loader,
    )
    while True:
        time.sleep(1)
        park_lock_wrapper.check()


if __name__ == "__main__":
    args = sys.argv

    if len(args) <= 1:
        raise Exception("No arguments")

    if args[-1] == '-init':
        initialize()
    elif args[-1] == '-lock':
        # Будьте осторожны,
        # не будет проверки с лидара, ультрасоника на расстояние
        lock()
    elif args[-1] == '-unlock':
        # Будьте осторожны,
        # не будет проверки с лидара, ультрасоника на расстояние
        unlock()
    elif args[-1] == '-loop':
        run_loop()
    else:
        raise Exception("Invalid key" + str(args[-1]))
