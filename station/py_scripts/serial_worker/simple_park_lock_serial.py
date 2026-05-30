from multiprocessing import Queue
from multiprocessing.connection import Connection
import time


from kv.redis_kv import models
from py_scripts.config import get_settings, settings_loader
from py_scripts.custom_logger import logger
from py_scripts.park_lock.parklock_logic import ParkLock
from py_scripts.serial_worker.serial_message import SerialMessage


settings = get_settings()
serial_number = settings.park_lock_serial_number if settings else ""


def initialize() -> None:
    logger.info("Trying to get status")
    message = SerialMessage(
        message=f"{serial_number}status".encode(),
        destination=serial_number or "",
        size=12,
        skip_bytes=2,
    )
    input_queue.put(message, True, None)
    answer = output_connection.recv().decode('ascii')
    logger.info("Status answer", answer=answer)
    status = answer.split(" ")[0]
    if status == "lock":
        models.set_prop_value("PARKLOCK__LAST_STATUS", "LOCKED")
    if status == "unlock":
        models.set_prop_value("PARKLOCK__LAST_STATUS", "UNLOCKED")


def lock() -> None:
    logger.info("Trying to lock")
    message = SerialMessage(
        message=f"{serial_number}on".encode(),
        destination=serial_number or "",
        size=4,
        skip_bytes=2,
    )
    input_queue.put(message, True, None)
    answer = output_connection.recv().decode('ascii')
    logger.info("Lock answer", answer=answer)
    if answer == "lock":
        logger.info("Locked")
        models.set_prop_value("PARKLOCK__LAST_STATUS", "LOCKED")


def unlock() -> None:
    logger.info("Trying to unlock")
    message = SerialMessage(
        message=f"{serial_number}off".encode(),
        destination=serial_number or "",
        size=6,
        skip_bytes=2,
    )
    input_queue.put(message, True, None)
    answer = output_connection.recv().decode('ascii')
    logger.info("Unlock answer", answer=answer)
    if answer == "unlock":
        logger.info("Unlocked")
        models.set_prop_value("PARKLOCK__LAST_STATUS", "UNLOCKED")


def run_loop() -> None:
    logger.info("Park lock loop started")
    initialize()

    park_lock_wrapper = ParkLock(
        lock_fn=lock,
        unlock_fn=unlock,
        init_fn=initialize,
        db=models,
        settings_loader=settings_loader,
    )

    while True:
        try:
            time.sleep(1)
            park_lock_wrapper.check()
        except Exception as e:
            logger.exception(str(e))
            continue


def start_park_lock(input: "Queue[SerialMessage]", output: Connection) -> None:
    global input_queue
    input_queue = input

    global output_connection
    output_connection = output

    run_loop()
