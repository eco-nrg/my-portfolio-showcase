import datetime
import time

import libscrc
import requests
import RPi.GPIO as GPIO
import serial
from config import get_settings
from custom_logger import logger
from mercury206 import commands

from kv.redis_kv import models
from py_scripts.constants import (
    PROPERTY_SPACE_MODE,
    PROPERTY_SPACE_PRICE_IDLE,
    PROPERTY_SPACE_PRICE_KWH,
    update_property_if_present,
)
from py_scripts.space_status import SpaceStatus

MERCURY_206_PRNO_MODEL = "M_206_PRNO"

settings = get_settings()
logger.info("meter loop started")
GPIO.setmode(GPIO.BOARD)

meter_model = settings.meter_model
serial_number = settings.serial_number
port = settings.com_port
stream = serial.Serial()

redPin = settings.red_pin
greenPin = settings.green_pin
bluePin = settings.blue_pin
ACTIVE_CHARGE_AMP = settings.active_amp
reedSwitchPin = settings.reed_switch_pin
is_on = models.get_prop_value("METER__HAS_POWER") == "1"
last_has_power = models.get_prop_value("REAL_HAS_POWER") == "1"
last_internet_on = models.get_prop_value("NO_INTERNET_ITER") == "0"
no_internet = models.get_prop_value("NO_INTERNET") == "1"

GPIO.setup(reedSwitchPin, GPIO.IN)


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


def increment_no_internet():
    global last_internet_on
    global no_internet
    last_internet_on = False
    value = int(models.get_prop_value("NO_INTERNET_ITER", "0"))
    if value == 0:
        models.set_prop_value("NO_INTERNET_TIME", str(
            datetime.datetime.now().isoformat()))
    value += 1
    models.set_prop_value("NO_INTERNET_ITER", str(value))

    if value > 1:
        stamp = models.get_prop_value("NO_INTERNET_TIME", str(
            datetime.datetime.now().isoformat()))
        val = datetime.datetime.fromisoformat(stamp)
        now = datetime.datetime.now()
        difference = (now - val).total_seconds()
        if difference > 60 and not no_internet:
            models.set_prop_value("NO_INTERNET", "1")
            logger.warning("internet was lost")
            no_internet = True
            turn_red()


def turn_red():
    models.set_prop_value('LIGHT_COLOR_STATION', 'RED')
    models.set_prop_value('STATE', models.STATE_WARNING)


def turn_green():
    models.set_prop_value('LIGHT_COLOR_STATION', 'GREEN')
    models.set_prop_value('STATE', models.STATE_IDLE)


def turn_blue():
    models.set_prop_value('LIGHT_COLOR_STATION', 'BLUE')


def turn_white():
    models.set_prop_value('LIGHT_COLOR_STATION', 'WHITE')


def turn_orange():
    models.set_prop_value('LIGHT_COLOR_STATION', 'ORANGE')
    models.set_prop_value("STATE", models.STATE_BOOKED)


def convert_bytes(bytes_raw):
    crc16 = libscrc.modbus(bytearray(bytes_raw))

    new_list = bytes_raw + [0, 0]
    new_list[-2] = crc16 & 0xff
    new_list[-1] = crc16 >> 8

    return new_list


def convert4byte(blist):
    '''
    see page 58 at https://www.incotexcom.ru/files/em/docs/merkuriy-sistema-komand-ver-1-2023-01-23.pdf
    Здесь и в дальнейшем под нумерацией байт понимается уменьшение
    «веса» каждого байта с возрастанием его номера, т. е. 1-й байт – старший, 2-й байт –
    старший младшего слова, 3-й – младший младшего слова. 
    Also see: https://github.com/wirenboard/wb-mqtt-serial
    '''
    return (blist[1] << 24) + (blist[0] << 16) + (blist[3] << 8) + blist[2]


def convert3byte(blist):
    val = int(((blist[0] << 2) & 0xFF) >> 2)
    return ((val << 16) + (int(blist[2]) << 8) + int(blist[1]))


def get_net_address():
    # 4.4.7 Сетевой адрес
    stream.write(convert_bytes([0x00, 0x08, 0x05]))
    time.sleep(0.2)
    buf = list(stream.read(32))
    logger.info("net_address", buf=buf)


def test_request():
    # Тест
    if meter_model == MERCURY_206_PRNO_MODEL:
        try:
            readings = commands.display_readings(stream, serial_number)
        except Exception as e:
            readings = []
            logger.error(e)
        return len(readings) > 0

    stream.write(convert_bytes([serial_number, 0x00]))
    time.sleep(0.2)
    buf = list(stream.read(32))
    logger.debug(f"test {buf}")

    if len(buf) != 4:
        logger.warning("len(TEST_RESPONSE) != 4")
        return False

    if buf[0] != serial_number:
        logger.warning("TEST_RESPONSE.serial_number != serial_number")
        return False

    return True


def authorize():
    # Авторизация
    if meter_model == MERCURY_206_PRNO_MODEL:
        # TODO: check
        # try:
        #     data = commands.connect(stream, serial_number)
        #     print("connect data:")
        #     print(data)
        # except Exception as e:
        #     data = []
        #     logger.error(e)
        # return len(data)
        return True

    stream.write(convert_bytes(
        [serial_number, 0x01, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02]))
    time.sleep(0.2)
    buf = list(stream.read(32))
    logger.debug(f"authorize {buf}")
    if len(buf) != 4:
        logger.warning("len(AUTHORIZE_RESPONSE) != 4")
        return False
    if buf[0] != serial_number:
        logger.warning("AUTHORIZE_RESPONSE.serial_number != serial_number")
        return False
    return True


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


# white on
turn_white()


def main():
    logger.info("meter loop started")

    global is_on
    global last_has_power
    global last_internet_on
    global no_internet
    global stream

    # pin_number = int(models.get_prop_value("PIN_NUMBER", "0"))
    # logger.info(f"initial pin number {pin_number}")

    # for space_item in config.get("lot", dict()).get("spaces", list()):
    # for pin in space_item.get("connectors", list()):
    # pin = pin.get("relay_pin_number")
    # logger.info(f"relay_pin_number {pin}")
    # if pin:
    #     turn_off_pin(pin)

    while True:
        if not stream.isOpen():
            logger.info("opening stream")

            time.sleep(0.1)

            try:
                stream = serial.Serial(port, 9600, timeout=1)
            except Exception as e:
                logger.exception(e)

            get_net_address()
            time.sleep(0.2)

            logger.info(
                "test request",
                port=port,
                meter_model=meter_model,
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
                if (
                    no_internet or
                    models.get_prop_value("STATION__DISABLED", "0") == "1"
                ):
                    turn_red()
                else:
                    if is_on:
                        turn_blue()
                        # if pin_number > 0:
                        #     turn_on_pin(pin_number)
                    elif last_has_power:
                        turn_green()
                    else:
                        turn_red()

        logger.info("continue")

        reed_value = int(GPIO.input(reedSwitchPin))
        models.set_prop_value("REED_VALUE", str(reed_value))

        state = models.get_prop_value("STATE", models.STATE_IDLE)

        if meter_model == MERCURY_206_PRNO_MODEL:
            current_v, current_a, current_w = commands.instant_vcp(stream, serial_number)
            readings = commands.display_readings(stream, serial_number)
            total_kw = sum(readings)
        else:
            # Чтение накопленной мощности
            logger.debug('read total_kw')
            stream.write(convert_bytes([serial_number, 0x05, 0x00, 0x00]))
            time.sleep(0.1)
            buf = list(stream.read(32))

            # [95, 0, 0, 180, 6, 255, 255, 255, 255, 0, 0, 140, 1, 0, 0, 62, 1, 35, 137]
            # [95, 5, 248, 67]
            # [95, 5, 248, 67, 0]
            if len(buf) != 19:
                time.sleep(1)
                logger.info(f"close stream, buf == {buf}")
                stream.close()
                continue

            total_kw = convert4byte(buf[1:5]) / 1000

            # Мощность P (Вт) - сумма
            stream.write(convert_bytes([serial_number, 0x08, 0x11, val_codes[0]]))
            time.sleep(0.1)
            buf = list(stream.read(32))
            current_w = convert3byte(buf[1:4]) / val_divs[0]
            logger.debug('read current_w', current_w=current_w)

            # Напряж U (В) - 3
            stream.write(convert_bytes([serial_number, 0x08, 0x11, val_codes[18]]))
            time.sleep(0.1)
            buf = list(stream.read(32))
            current_v = convert3byte(buf[1:4]) / val_divs[18]
            logger.debug('read current_v', current_v=current_v)

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

        if meter_model != MERCURY_206_PRNO_MODEL:
            # Ток I (А) - 1
            stream.write(convert_bytes([serial_number, 0x08, 0x11, val_codes[19]]))
            time.sleep(0.1)
            buf = list(stream.read(32))
            current_a_1 = convert3byte(buf[1:4]) / val_divs[19]
            logger.debug('read current_a_1', current_a_1=current_a_1)
            models.set_prop_value("METER__AM_PHASE_1", str(current_a_1))

            # Ток I (А) - 2
            stream.write(convert_bytes([serial_number, 0x08, 0x11, val_codes[20]]))
            time.sleep(0.1)
            buf = list(stream.read(32))
            current_a_2 = convert3byte(buf[1:4]) / val_divs[20]
            logger.debug('read current_a_2', current_a_2=current_a_2)
            models.set_prop_value("METER__AM_PHASE_2", str(current_a_2))

            # Ток I (А) - 3
            stream.write(convert_bytes([serial_number, 0x08, 0x11, val_codes[21]]))
            time.sleep(0.1)
            buf = list(stream.read(32))
            current_a_3 = convert3byte(buf[1:4]) / val_divs[21]
            logger.debug('read current_a_3', current_a_3=current_a_3)
            models.set_prop_value("METER__AM_PHASE_3", str(current_a_3))

            current_a = max(current_a_1, current_a_2, current_a_3)

        overwrite_amp = float(models.get_prop_value("OVERWRITE_AMP", "0"))
        if overwrite_amp:
            current_a = overwrite_amp

        if state in [models.STATE_CHARGING, models.STATE_CHARGING_DOWN] and current_a > ACTIVE_CHARGE_AMP:
            state = models.STATE_CHARGING_START
            models.set_prop_value("STATE", state)
        elif state == models.STATE_CHARGING_START and current_a < ACTIVE_CHARGE_AMP:
            state = models.STATE_CHARGING_DOWN
            models.set_prop_value("STATE", state)
        elif state == models.STATE_CHARGING_DOWN and reed_value == 1:
            state = models.STATE_CHARGING_END
            models.set_prop_value("STATE", state)

        url = settings.api_url + "/main/api/v1/space_stat/0/"
        data = dict(
            space_uid=settings.space_uid,
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
                headers={'Authorization': 'Bearer ' + settings.api_token},
                timeout=30,
            )
        except requests.exceptions.ConnectionError:
            logger.exception("No response")
            increment_no_internet()
            continue
        except Exception as e:
            logger.exception(e)
            continue

        if req.status_code != 200:
            logger.error("status code is %s", req.status_code)
            continue

        if not last_internet_on:
            reset_internet()

        data = req.json()
        logger.info("Receive data", data=data)

        is_station_force_disable = data.get('is_disabled')
        is_station_force_disable = ("0"
                                    if is_station_force_disable is None
                                    else str(int(is_station_force_disable))
                                    )

        station_disable = models.get_prop_value("STATION__DISABLED", "0")
        if station_disable != is_station_force_disable:
            models.set_prop_value("STATION__DISABLED", is_station_force_disable)

            if is_station_force_disable == "1":
                logger.info("The station is disabled by the admin")
                turn_red()
            else:
                turn_green()

        if "payed_time" in data:
            models.set_prop_value("ORDER_PAYED_TIME", data['payed_time'] or "0")

        space_status = data.get('status')

        if space_status:
            models.set_prop_value("SPACE_STATUS", space_status)

        #TODO: add booking session end handling (set available after)
        if space_status == SpaceStatus.BOOKED:
            turn_orange()
            models.set_prop_value('BOOKED_UNTIL', data.get('booked_until'))

        price_kwh = data.get('price_kwh')
        price_kwh = price_kwh if price_kwh is not None else '0'
        models.set_prop_value(PROPERTY_SPACE_PRICE_KWH, price_kwh)

        price_idle = data.get('price_idle')
        price_idle = price_idle if price_idle is not None else '0'
        models.set_prop_value(PROPERTY_SPACE_PRICE_IDLE, price_idle)

        update_property_if_present(data,
                                   'mode',
                                   PROPERTY_SPACE_MODE,
                                   models)

        if data['is_on'] != is_on:
            if data['is_on']:
                # Включение
                logger.info("up")

                state = models.STATE_CHARGING
                models.set_prop_value("STATE", state)
                result = False
                if meter_model != MERCURY_206_PRNO_MODEL:
                    stream.write(convert_bytes([serial_number, 0x03, 0x31, 0x00]))
                    time.sleep(0.1)
                    buf = list(stream.read(32))
                    result = buf[0] == serial_number
                else:
                    commands.turn_relay(stream, serial_number, True)
                    try:
                        result = commands.get_relay(stream, serial_number)
                    except Exception as e:
                        logger.error(e)
                if result:
                    if models.set_prop_value("PARKLOCK__MANUAL_MODE", "0") != "1":
                        models.set_prop_value(
                            "PARKLOCK__NEED_STATUS", "UNLOCKED")
                    is_on = data['is_on']
                    models.set_prop_value(
                        "ORDER_START_TIME", data['start_time'])
                    models.set_prop_value(
                        "ORDER_USER_FREE_SECONDS", data['free_seconds'])
                    models.set_prop_value(
                        "ORDER_START_KW", str(data['start_kw']))
                    models.set_prop_value("METER__HAS_POWER", "1")
                    logger.info("meter is on")

                    if last_has_power:
                        turn_blue()
                    else:
                        turn_red()
            else:
                logger.info("down")

                result = False
                if meter_model != MERCURY_206_PRNO_MODEL:
                    stream.write(convert_bytes([serial_number, 0x03, 0x31, 0x01]))
                    time.sleep(0.1)
                    buf = list(stream.read(32))
                    logger.info('down')
                    result = buf[0] == serial_number
                else:
                    commands.turn_relay(stream, serial_number, False)
                    try:
                        result = not commands.get_relay(stream, serial_number)
                    except Exception as e:
                        logger.error(e)
                if result:
                    if models.set_prop_value("PARKLOCK__MANUAL_MODE", "0") != "1":
                        models.set_prop_value(
                            "PARKLOCK__NEED_STATUS", "LOCKED")

                    is_on = data['is_on']
                    models.set_prop_value("METER__HAS_POWER", "0")
                    logger.info("meter is off")

                    if last_has_power:
                        turn_green()
                    else:
                        turn_red()


if __name__ == "__main__":
    main()
