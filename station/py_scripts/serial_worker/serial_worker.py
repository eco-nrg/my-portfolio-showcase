import serial
import time
from multiprocessing import Pipe, Process, Queue
from multiprocessing.connection import Connection
from typing import Dict, List, Optional, Tuple, Union

from py_scripts.config import get_settings
from py_scripts.custom_logger import logger
from py_scripts.serial_worker.serial_message import SerialMessage
from py_scripts.serial_worker.simple_meter_serial import start_meter
from py_scripts.serial_worker.simple_park_lock_serial import start_park_lock


READ_TIMEOUT = 5
SKIP_TIMEOUT = 1


settings = get_settings()
port = settings.com_port if settings else ""
meter_serial_number = settings.serial_number if settings else -1
park_lock_serial_number = settings.park_lock_serial_number if settings else ""


input: "Queue[SerialMessage]" = Queue(500)
outputs: Dict[str, Tuple[Connection, Connection]] = {}


def connect() -> None:
    global serial_port
    serial_port = serial.Serial(port, 9600, timeout=READ_TIMEOUT)
    time.sleep(0.1)


def write(message: Union[bytes, List[int]]) -> None:
    global serial_port

    if not serial_port.is_open:
        connect()

    logger.info("Write", message=message)
    serial_port.write(message)  # type: ignore


def read(
    size: int,
    skip_bytes: Optional[int],
    destination: str,
) -> None:
    global serial_port

    if not serial_port.is_open:
        connect()

    response = serial_port.read(size)

    if skip_bytes:
        serial_port.timeout = SKIP_TIMEOUT
        serial_port.read(skip_bytes)
        serial_port.timeout = READ_TIMEOUT

    logger.info("Read", response=response, size=len(response))
    dest = outputs[destination]
    if dest:
        dest[1].send(response)


def loop() -> None:
    connect()
    while True:
        message = input.get()
        write(message=message.message)
        read(
            size=message.size,
            skip_bytes=message.skip_bytes,
            destination=message.destination,
        )


if __name__ == "__main__":
    park_lock_connection = Pipe(False)
    outputs[park_lock_serial_number] = park_lock_connection
    park_lock_process = Process(
        target=start_park_lock,
        args=(input, park_lock_connection[0]),
    )
    park_lock_process.start()

    meter_connection = Pipe(False)
    outputs[str(meter_serial_number)] = meter_connection
    meter_process = Process(
        target=start_meter,
        args=(input, meter_connection[0]),
    )
    meter_process.start()

    loop()
