from datetime import datetime
from multiprocessing import Queue
from multiprocessing.connection import Connection
from RPi.GPIO import input, setup, setmode, BOARD, IN
from typing import List
import libscrc  # type: ignore
import requests
import time

from kv.redis_kv import models
from py_scripts.config import get_settings
from py_scripts.constants import (
    PROPERTY_SPACE_MODE,
    PROPERTY_SPACE_PRICE_IDLE,
    PROPERTY_SPACE_PRICE_KWH,
    update_property_if_present,
)
from py_scripts.custom_logger import logger
from py_scripts.serial_worker.serial_message import SerialMessage
from py_scripts.space_status import SpaceStatus

settings = get_settings()
reed_switch_pin = settings.reed_switch_pin if settings else 29
serial_number = settings.serial_number if settings else -1
active_charge_amp = settings.active_amp if settings else 12
base_url = settings.api_url if settings else ""
space_uid = settings.space_uid if settings else ""
api_token = settings.api_token if settings else ""

is_on = models.get_prop_value("METER__HAS_POWER") == "1"
last_has_power = models.get_prop_value("REAL_HAS_POWER") == "1"
last_internet_on = models.get_prop_value("NO_INTERNET_ITER") == "0"
no_internet = models.get_prop_value("NO_INTERNET") == "1"

connected = False

url = f"{base_url}/main/api/v1/space_stat/0/"

val_codes = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
             48, 49, 50, 51, 17, 18, 19, 33, 34, 35, 64]
val_divs = [100, 100, 100, 100, -100, -100, -100, -100, 100, 100, 100,
            100, 1000, 1000, 1000, 1000, 100, 100, 100, 1000, 1000, 1000, 100]
val_names = [
    "Мощность P (Вт) - сумма",  # 0
    "Мощность P (Вт) - 1",  # 1
    "Мощность P (Вт) - 2",  # 2
    "Мощность P (Вт) - 3",  # 3
    "Мощность Q (Вар) - сумма",  # 4
    "Мощность Q (Вар) - 1",  # 5
    "Мощность Q (Вар) - 2",  # 6
    "Мощность Q (Вар) - 3",  # 7
    "Мощность S (ВА) - сумма",  # 8
    "Мощность S (ВА) - 1",  # 9
    "Мощность S (ВА) - 2",  # 10
    "Мощность S (ВА) - 3",  # 11
    "Коэф. мощн. - сумма",  # 12
    "Коэф. мощн. - 1",  # 13
    "Коэф. мощн. - 2",  # 14
    "Коэф. мощн. - 3",  # 15
    "Напряж U (В) - 1",  # 16
    "Напряж U (В) - 2",  # 17
    "Напряж U (В) - 3",  # 18
    "Ток I (А) - 1",  # 19
    "Ток I (А) - 2",  # 20
    "Ток I (А) - 3",  # 21
    "Частота F (Гц)",  # 22
]


setmode(BOARD)
setup(reed_switch_pin, IN)


def convert_message(bytes_raw: List[int]):
    crc16 = libscrc.modbus(bytearray(bytes_raw))  # type: ignore

    new_list = bytes_raw + [0, 0]
    new_list[-2] = crc16 & 0xff
    new_list[-1] = crc16 >> 8

    return new_list


def convert_four_bytes(blist: List[int]) -> int:
    return (blist[1] << 24) + (blist[0] << 16) + (blist[3] << 8) + blist[2]


def convert_three_bytes(blist: List[int]) -> int:
    val = int(((blist[0] << 2) & 0xFF) >> 2)
    return ((val << 16) + (int(blist[2]) << 8) + int(blist[1]))


def increment_no_internet():
    global last_internet_on
    global no_internet
    last_internet_on = False
    value = int(models.get_prop_value("NO_INTERNET_ITER", "0") or "0")
    if value == 0:
        models.set_prop_value(
            "NO_INTERNET_TIME",
            str(datetime.now().isoformat()),
        )
    value += 1
    models.set_prop_value("NO_INTERNET_ITER", str(value))

    if value > 1:
        stamp = models.get_prop_value(
            "NO_INTERNET_TIME",
            str(datetime.now().isoformat()),
        ) or ""
        val = datetime.fromisoformat(stamp)
        now = datetime.now()
        difference = (now - val).total_seconds()
        if difference > 60 and not no_internet:
            models.set_prop_value("NO_INTERNET", "1")
            logger.warning("internet was lost")
            no_internet = True
            turn_red()


def reset_internet():
    global last_internet_on
    global no_internet
    last_internet_on = True
    no_internet = False
    models.set_prop_value("NO_INTERNET_ITER", "0")
    models.set_prop_value("NO_INTERNET", "0")

    if is_on:
        logger.warning("internet was restored and now power is on")
        turn_blue()
    else:
        logger.warning("internet was restored and now power is off")

        if last_has_power:
            turn_green()
        else:
            turn_red()


def turn_red() -> None:
    models.set_prop_value("LIGHT_COLOR_STATION", "RED")
    models.set_prop_value("STATE", models.STATE_WARNING)


def turn_green() -> None:
    models.set_prop_value("LIGHT_COLOR_STATION", "GREEN")
    models.set_prop_value("STATE", models.STATE_IDLE)


def turn_blue() -> None:
    models.set_prop_value("LIGHT_COLOR_STATION", "BLUE")


def turn_white() -> None:
    models.set_prop_value("LIGHT_COLOR_STATION", "WHITE")


def turn_orange() -> None:
    models.set_prop_value("LIGHT_COLOR_STATION", "ORANGE")
    models.set_prop_value("STATE", models.STATE_BOOKED)


def send_message(bytes: List[int], size: int) -> List[int]:
    message = SerialMessage(
        message=bytes,
        destination=str(serial_number),
        size=size,
    )
    input_queue.put(message, True, None)
    answer = output_connection.recv()
    return list(answer)


def get_net_address():
    # 4.4.7 Сетевой адрес
    buf = send_message(
        bytes=convert_message([0x00, 0x08, 0x05]),
        size=5,
    )
    logger.info("net_address", buf=buf)


def test_request():
    buf = send_message(
        bytes=convert_message([serial_number, 0x00]),
        size=4,
    )
    logger.debug(f"test {buf}")

    if len(buf) != 4:
        logger.warning("len(TEST_RESPONSE) != 4")
        return False

    if buf[0] != serial_number:
        logger.warning("TEST_RESPONSE.serial_number != serial_number")
        return False

    return True


def authorize():
    buf = send_message(
        bytes=convert_message(
            [serial_number, 0x01, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02]
        ),
        size=4,
    )
    logger.debug(f"authorize {buf}")
    if len(buf) != 4:
        logger.warning("len(AUTHORIZE_RESPONSE) != 4")
        return False
    if buf[0] != serial_number:
        logger.warning("AUTHORIZE_RESPONSE.serial_number != serial_number")
        return False
    return True


def read_total_kw() -> List[int]:
    return send_message(
        bytes=convert_message([serial_number, 0x05, 0x00, 0x00]),
        size=19,
    )


def read_current_w() -> List[int]:
    return send_message(
        bytes=convert_message([serial_number, 0x08, 0x11, val_codes[0]]),
        size=6,
    )


def read_current_v() -> List[int]:
    return send_message(
        bytes=convert_message([serial_number, 0x08, 0x11, val_codes[18]]),
        size=6,
    )


def read_current_a_one() -> List[int]:
    return send_message(
        bytes=convert_message([serial_number, 0x08, 0x11, val_codes[19]]),
        size=6,
    )


def read_current_a_two() -> List[int]:
    return send_message(
        bytes=convert_message([serial_number, 0x08, 0x11, val_codes[20]]),
        size=6,
    )


def read_current_a_three() -> List[int]:
    return send_message(
        bytes=convert_message([serial_number, 0x08, 0x11, val_codes[21]]),
        size=6,
    )


def turn_on_meter() -> List[int]:
    return send_message(
        bytes=convert_message([serial_number, 0x03, 0x31, 0x00]),
        size=4,
    )


def turn_off_meter() -> List[int]:
    return send_message(
        bytes=convert_message([serial_number, 0x03, 0x31, 0x01]),
        size=4,
    )


def run_loop() -> None:
    logger.info("Meter loop started")

    global is_on
    global last_has_power
    global last_internet_on
    global no_internet
    global connected

    while True:
        try:
            # Add time.sleep if CPU is overloaded by serial worker
            if not connected:
                get_net_address()
                logger.info(
                    "test request",
                    serial_number=serial_number,
                )
                if not test_request():
                    turn_red()
                logger.info("authorize")
                if not authorize():
                    logger.info("not authorized")
                    turn_red()
                else:
                    logger.info("authorized")
                    if (no_internet or
                       models.get_prop_value("STATION__DISABLED", "0") == "1"):
                        turn_red()
                    else:
                        if is_on:
                            turn_blue()
                        elif last_has_power:
                            turn_green()
                        else:
                            turn_red()
                connected = True

            reed_value = int(input(reed_switch_pin))
            models.set_prop_value("REED_VALUE", str(reed_value))

            state = models.get_prop_value("STATE", models.STATE_IDLE)

            buf = read_total_kw()
            if len(buf) != 19:
                time.sleep(1)
                logger.info(f"Invalid buf length == {buf}")
                continue
            total_kw = convert_four_bytes(buf[1:5]) / 1000
            logger.debug("read total_kw", total_kw=total_kw)

            buf = read_current_w()
            current_w = convert_three_bytes(buf[1:4]) / val_divs[0]
            logger.debug("read current_w", current_w=current_w)

            buf = read_current_v()
            current_v = convert_three_bytes(buf[1:4]) / val_divs[18]
            logger.debug("read current_v", current_v=current_v)

            if current_v <= 150 and last_has_power:
                last_has_power = False
                models.set_prop_value("REAL_HAS_POWER", "0")
                logger.warning("power was lost")
                turn_red()
            elif current_v > 150 and not last_has_power:
                models.set_prop_value("REAL_HAS_POWER", "1")
                last_has_power = True
                if is_on:
                    logger.warning("power was restored and now its on")
                    if not no_internet:
                        turn_blue()
                else:
                    logger.warning("power was restored and now its off")
                    if not no_internet:
                        turn_green()

            buf = read_current_a_one()
            current_a_1 = convert_three_bytes(buf[1:4]) / val_divs[19]
            logger.debug("read current_a_1", current_a_1=current_a_1)
            models.set_prop_value("METER__AM_PHASE_1", str(current_a_1))

            buf = read_current_a_two()
            current_a_2 = convert_three_bytes(buf[1:4]) / val_divs[20]
            logger.debug("read current_a_2", current_a_2=current_a_2)
            models.set_prop_value("METER__AM_PHASE_2", str(current_a_2))

            buf = read_current_a_three()
            current_a_3 = convert_three_bytes(buf[1:4]) / val_divs[21]
            logger.debug("read current_a_3", current_a_3=current_a_3)
            models.set_prop_value("METER__AM_PHASE_3", str(current_a_3))

            current_a = max(current_a_1, current_a_2, current_a_3)

            overwrite_amp = float(
                models.get_prop_value("OVERWRITE_AMP", "0") or "0",
            )

            if overwrite_amp:
                current_a = overwrite_amp

            if (state in [models.STATE_CHARGING, models.STATE_CHARGING_DOWN] and
                    current_a > active_charge_amp):
                state = models.STATE_CHARGING_START
                models.set_prop_value("STATE", state)
            elif (state == models.STATE_CHARGING_START and
                    current_a < active_charge_amp):
                state = models.STATE_CHARGING_DOWN
                models.set_prop_value("STATE", state)
            elif state == models.STATE_CHARGING_DOWN and reed_value == 1:
                state = models.STATE_CHARGING_END
                models.set_prop_value("STATE", state)

            data = dict(
                space_uid=space_uid,
                total_kw=total_kw,
                current_w=current_w,
                current_v=current_v,
                current_a=current_a,
            )

            models.set_prop_value("METER__AM_VALUE", str(current_a))
            models.set_prop_value("METER__KWT_VALUE", str(total_kw))
            models.set_prop_value("METER__WT_VALUE", str(current_w))

            try:
                logger.info("Send data", data=data)
                req = requests.post(
                    url,
                    json=data,
                    headers={"Authorization": f"Bearer {api_token}"},
                    timeout=30,
                )
            except requests.exceptions.ConnectionError:
                logger.exception("No response")
                increment_no_internet()
                continue
            except Exception as e:
                logger.exception(str(e))
                continue

            if req.status_code != 200:
                logger.error("status code is %s", req.status_code)
                continue

            if not last_internet_on:
                reset_internet()

            data = req.json()
            logger.info("Receive data", data=data)
            is_station_force_disable = data.get("is_disabled") or "0"
            is_station_force_disable = str(int(is_station_force_disable))

            station_disable = models.get_prop_value("STATION__DISABLED", "0")
            if station_disable != is_station_force_disable:
                models.set_prop_value(
                    "STATION__DISABLED",
                    is_station_force_disable,
                )

                if is_station_force_disable == "1":
                    logger.info("The station is disabled by the admin")
                    turn_red()
                else:
                    turn_green()

            if "payed_time" in data:
                models.set_prop_value(
                    "ORDER_PAYED_TIME",
                    data["payed_time"] or "0",
                )

            space_status = data.get("status")

            if space_status:
                models.set_prop_value("SPACE_STATUS", space_status)

            if space_status == SpaceStatus.BOOKED:
                turn_orange()
                models.set_prop_value("BOOKED_UNTIL", data.get("booked_until"))

            price_kwh = data.get("price_kwh") or "0"
            models.set_prop_value(PROPERTY_SPACE_PRICE_KWH, price_kwh)

            price_idle = data.get("price_idle") or "0"
            models.set_prop_value(PROPERTY_SPACE_PRICE_IDLE, price_idle)

            update_property_if_present(
                data,
                "mode",
                PROPERTY_SPACE_MODE,
                models,
            )

            if data["is_on"] != is_on:
                if data["is_on"]:
                    # Включение
                    logger.info("up")

                    state = models.STATE_CHARGING
                    models.set_prop_value("STATE", state)
                    buf = turn_on_meter()
                    result = buf[0] == serial_number
                    if result:
                        if models.set_prop_value(
                                "PARKLOCK__MANUAL_MODE",
                                "0",
                        ) != "1":
                            models.set_prop_value(
                                "PARKLOCK__NEED_STATUS",
                                "UNLOCKED",
                            )
                        is_on = data['is_on']
                        models.set_prop_value(
                            "ORDER_START_TIME",
                            data['start_time'],
                        )
                        models.set_prop_value(
                            "ORDER_USER_FREE_SECONDS",
                            data['free_seconds'],
                        )
                        models.set_prop_value(
                            "ORDER_START_KW",
                            str(data['start_kw']),
                        )
                        models.set_prop_value("METER__HAS_POWER", "1")
                        logger.info("meter is on")

                        if last_has_power:
                            turn_blue()
                        else:
                            turn_red()
                else:
                    logger.info("down")

                    buf = turn_off_meter()
                    result = buf[0] == serial_number
                    if result:
                        if models.set_prop_value(
                            "PARKLOCK__MANUAL_MODE",
                            "0",
                        ) != "1":
                            models.set_prop_value(
                                "PARKLOCK__NEED_STATUS",
                                "LOCKED",
                            )

                        is_on = data['is_on']
                        models.set_prop_value("METER__HAS_POWER", "0")
                        logger.info("meter is off")

                        if last_has_power:
                            turn_green()
                        else:
                            turn_red()
        except Exception as e:
            logger.exception(str(e))
            continue

        time.sleep(1)


def start_meter(input: "Queue[SerialMessage]", output: Connection) -> None:
    global input_queue
    input_queue = input

    global output_connection
    output_connection = output

    run_loop()
