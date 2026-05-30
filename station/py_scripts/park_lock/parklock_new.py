import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, Optional

import RPi.GPIO as GPIO
from bluepy import btle
from bluepy.btle import BTLEDisconnectError
from Crypto.Cipher import AES

from kv.redis_kv import models
from py_scripts.config import get_settings
from py_scripts.custom_logger import logger

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

settings = get_settings()

GPIO.setmode(GPIO.BOARD)

parklock_status: Dict[int, str] = {
    0: "UNLOCKED",
    1: "LOCKED",
}

device_mac = settings.parklock_mac

adminPassword = bytes([1, 2, 3, 4, 5, 6])
unlockKey = bytes([1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4, 5, 6])
aes_key = bytes([0xD0, 0xF9, 0x58, 0x8C, 0x59, 0xA2, 0x69, 0x26, 0x18, 0x53,
                 0xCB, 0xDA, 0x80, 0x82, 0x83, 0x39])
uid_key = bytes([0x00, 0x42, 0xcb, 0x6e])
requests = list()
buffer = list()


def get_key_path(mac_addr):
    file_path = os.path.join(BASE_DIR, '{}.key'.
                             format(mac_addr.replace(':', '-')))
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(bytearray())
    return file_path


def read_key(device_mac):
    with open(get_key_path(device_mac), 'rb') as f:
        return f.read()


def write_key(device_mac, new_key):
    with open(get_key_path(device_mac), 'wb') as f:
        f.write(new_key)


def aesEncrypt(data, key):
    obj = AES.new(key, AES.MODE_CBC, key)
    ciphertext = obj.encrypt(data)
    return ciphertext


def print_hex_array(arr, need_extended=False):
    logger.debug('[', end='')
    for idx, val in enumerate(arr):
        if idx > 0:
            logger.debug(',', end='')
        logger.debug(hex(val), end='')
    logger.debug(']')
    if need_extended:
        for idx, val in enumerate(arr):
            logger.debug(idx=idx, val=hex(val))


def aesDecrypt(ciphertext, key):
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.decrypt(ciphertext)


class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        global buffer
        global requests
        global access_key
        buffer += list(data)

        request_type, request = requests[0]
        del requests[0]
        response = bytes(buffer)
        buffer = list()
        # print("request", request_type, len(request))
        # print_hex_array(request)
        # print("response", len(response), [int(xh) for xh in response])
        # print_hex_array(response)

        if request_type == SET_AES_REQUEST:
            # обработка ключа
            logger.debug("SET_AES_REQUEST", response=response)
            if response[0] != 0xF9:
                raise ValueError("response[0] != 0xF9: " + str(
                    int(response[0])))
            data2 = response[1:17]
            access_key = aesDecrypt(data2, aes_key)
            write_key(device_mac, access_key)

            time.sleep(0.1)
            obj.checkPWD()

        elif request_type == CHECK_PWD_REQUEST:
            logger.debug("CHECK_PWD_REQUEST", response=response)

        elif request_type == SETUP_REQUEST:
            logger.debug("SETUP_REQUEST", response=response)

        elif request_type == BATTERY_REQUEST:
            logger.debug("BATTERY_REQUEST", response=response)

        else:
            raise ValueError('request_type:' + str(request_type))


access_key = read_key(device_mac)
obj = None

SERVICE_DATA = "0000fff0-0000-1000-8000-00805f9b34fb"
SERVICE_PWD1 = "0000ffe0-0000-1000-8000-00805f9b34fb"
SERVICE_BATTERY = "0000180f-0000-1000-8000-00805f9b34fb"
CHARACTERISTICS_PWD2 = "0000fff1-0000-1000-8000-00805f9b34fb"
CHARACTERISTICS_PWD = "0000fff6-0000-1000-8000-00805f9b34fb"
CHARACTERISTICS_PWDE1 = "0000ffe1-0000-1000-8000-00805f9b34fb"
CHARACTERISTICS_PWD1 = "0000ffe2-0000-1000-8000-00805f9b34fb"
CHARACTERISTICS_WRGB = "0000fff8-0000-1000-8000-00805f9b34fb"
CHARACTERISTICS_BATTERY = "00002a19-0000-1000-8000-00805f9b34fb"


SETUP_REQUEST = "SETUP_REQUEST"
CHECK_PWD_REQUEST = "CHECK_PWD_REQUEST"
BATTERY_REQUEST = "BATTERY_REQUEST"
SET_AES_REQUEST = "SET_AES_REQUEST"

TTL_SERVICE_PWD = None
TTL_SERVICE_PWD1 = None
TTL_SERVICE_PWD2 = None
TTL_SERVICE_PWDE1 = None
TTL_SERVICE_WRGB = None
TTL_SERVICE_BATT = None


class ParklockConnection:

    def __init__(self, mac_addr):
        global TTL_SERVICE_PWD
        global TTL_SERVICE_PWD1
        global TTL_SERVICE_PWD2
        global TTL_SERVICE_PWDE1
        global TTL_SERVICE_WRGB
        global TTL_SERVICE_BATT

        self.dev = None
        for i in range(100):
            try:
                self.dev = btle.Peripheral(mac_addr, btle.ADDR_TYPE_PUBLIC)
                logger.info(f'Connected to {mac_addr}')
                break
            except BTLEDisconnectError as err:
                logger.info('Try reconnect', i=i, err=err)
                time.sleep(0.1)
                pass

        if self.dev:
            self.dev.setDelegate(MyDelegate())

            service = self.dev.getServiceByUUID(btle.UUID(SERVICE_DATA))
            for ch in service.getCharacteristics():
                if ch.uuid == CHARACTERISTICS_PWD:
                    TTL_SERVICE_PWD = ch
                elif ch.uuid == CHARACTERISTICS_WRGB:
                    TTL_SERVICE_WRGB = ch
                elif ch.uuid == CHARACTERISTICS_PWD2:
                    TTL_SERVICE_PWD2 = ch

            service = self.dev.getServiceByUUID(btle.UUID(SERVICE_PWD1))
            for ch in service.getCharacteristics():
                if ch.uuid == CHARACTERISTICS_PWD1:
                    TTL_SERVICE_PWD1 = ch
                elif ch.uuid == CHARACTERISTICS_PWDE1:
                    TTL_SERVICE_PWDE1 = ch

            service = self.dev.getServiceByUUID(btle.UUID(SERVICE_BATTERY))
            for ch in service.getCharacteristics():
                if ch.uuid == CHARACTERISTICS_BATTERY:
                    TTL_SERVICE_BATT = ch

            logger.debug("TTL_SERVICE_PWD", TTL_SERVICE_PWD=TTL_SERVICE_PWD)
            logger.debug("TTL_SERVICE_PWD1", TTL_SERVICE_PWD1=TTL_SERVICE_PWD1)
            logger.debug("TTL_SERVICE_PWDE1",
                         TTL_SERVICE_PWDE1=TTL_SERVICE_PWDE1)
            logger.debug("TTL_SERVICE_WRGB", TTL_SERVICE_WRGB=TTL_SERVICE_WRGB)
            logger.debug("TTL_SERVICE_PWD2", TTL_SERVICE_PWD2=TTL_SERVICE_PWD2)
            logger.debug("TTL_SERVICE_BATT", TTL_SERVICE_BATT=TTL_SERVICE_BATT)

            models.set_prop_value("PARKLOCK__LAST_CONNECTION_TIME",
                                  str(int(time.time())))
        else:
            logger.error("Unable to init Peripheral")

    def setAES(self):
        global requests
        mess = bytes([0xF0]) + unlockKey + bytes([0xF1])
        mess = bytes([int(xh) for xh in mess])
        logger.debug("mess", mess=mess)
        requests.append((SET_AES_REQUEST, mess))
        TTL_SERVICE_WRGB.write(mess, True)

    def setup(self, is_up: bool):
        global requests
        mess = bytes([0x0A if is_up else 0x0B])
        mess = bytes([int(xh) for xh in mess])
        logger.debug("mess", mess=mess)
        requests.append((SETUP_REQUEST, mess))
        TTL_SERVICE_PWD2.write(mess, True)

    def checkPWD(self):
        global requests
        mess = bytes([0xA0]) + adminPassword + bytes([0x0A])
        mess = bytes([int(xh) for xh in mess])
        logger.debug("mess", mess=mess)
        requests.append((CHECK_PWD_REQUEST, mess))
        TTL_SERVICE_PWD.write(mess, True)

    def readDeviceBattry(self):
        global requests
        requests.append((BATTERY_REQUEST, []))
        val = TTL_SERVICE_BATT.read()
        logger.debug(ord(val))


def connect():
    logger.info('Try to connect')
    global obj
    obj = ParklockConnection(device_mac)
    obj.setAES()
    time.sleep(0.1)


def initialize():
    logger.info("trying to initialize")
    connect()


def lock():
    connect()
    logger.info("trying to lock")
    obj.setup(True)


def unlock():
    connect()
    logger.info("trying to unlock")
    obj.setup(False)


def get_battery():
    connect()
    logger.info("trying to get battery")
    obj.readDeviceBattry()


def status_parklock_by_pin() -> Optional[int]:
    pin_number = settings.parklock_status_pin
    GPIO.setup(pin_number, GPIO.IN)
    pin_value = GPIO.input(pin_number)
    if pin_value is None:
        logger.error("Value read from GPIO",
                     pin_number=pin_number, pin_value=pin_value)
    logger.info(f"Parklock pin value: {pin_value}")
    return pin_value


def is_timedelta_gone() -> bool:
    now = datetime.now()

    wt = models.get_prop_value("PARKLOCK__WAIT_TIME")
    if wt is None or wt == 'None':
        models.set_prop_value("PARKLOCK__WAIT_TIME", now.isoformat())
        return False

    last_update = datetime.fromisoformat(wt)

    time_difference = now - last_update

    if time_difference >= timedelta(seconds=15):
        models.set_prop_value("PARKLOCK__WAIT_TIME", None)
        return True
    return False


def try_lock():
    sonic_car_distance = settings.sonic_car_distance
    lidar_range_avg = float(models.get_prop_value("LIDAR__RANGE_AVG", "0"))
    if lidar_range_avg > sonic_car_distance:
        # We want wait delta time when we firstly know
        # that lidar distance is acceptable before lock parklock
        if is_timedelta_gone():
            lock()
            return True
        else:
            logger.debug('Wait time after lidar approve')
    else:
        logger.debug(
            'Lidar forbid locking. waiting... range=%.2f limit=%.2f',
            lidar_range_avg,
            sonic_car_distance,
        )
        models.set_prop_value("PARKLOCK__WAIT_TIME", datetime.now().isoformat())


def check():
    parklock__last_status = parklock_status.get(status_parklock_by_pin())
    models.set_prop_value('PARKLOCK__LAST_STATUS', parklock__last_status)
    parklock__need_status = models.get_prop_value("PARKLOCK__NEED_STATUS")

    logger.debug(
        'parklock_status=%s need_status=%s',
        parklock__last_status,
        parklock__need_status,
    )

    any_lock = False
    if parklock__last_status != parklock__need_status:
        if parklock__need_status == "LOCKED":
            any_lock = try_lock()
        elif parklock__need_status == "UNLOCKED":
            models.set_prop_value("PARKLOCK__WAIT_TIME", None)
            unlock()
        elif parklock__need_status == "INIT":
            models.set_prop_value("PARKLOCK__WAIT_TIME", None)
            initialize()

        parklock__last_status = parklock_status.get(status_parklock_by_pin())

        if (
            any_lock is True and
            parklock__last_status != parklock__need_status
        ):
            logger.warning(
                f'Status of parklock by pin {parklock__last_status}.'
                f'Need parklock status {parklock__need_status}',
            )


def run_loop():
    # systemd должен перезапустить систему, если она упадет с исключением
    # поэтому здесь нет смысла отлавливать исключения
    logger.info("parklock loop started")
    parklock__last_status = parklock_status.get(status_parklock_by_pin())
    if parklock__last_status is not None:
        models.set_prop_value('PARKLOCK__LAST_STATUS', parklock__last_status)
    while True:
        global settings
        settings = get_settings()
        check()
        time.sleep(1)


if __name__ == "__main__":
    args = sys.argv

    if len(args) <= 1:
        raise Exception("No arguments")

    if args[-1] == '-init':
        initialize()
    elif args[-1] == '-lock':
        lock()
    elif args[-1] == '-unlock':
        unlock()
    elif args[-1] == '-battery':
        get_battery()
    elif args[-1] == '-check':
        check()
    elif args[-1] == '-loop':
        run_loop()
    elif args[-1] == '-status':
        status_parklock_by_pin()
    else:
        raise Exception("Invalid key" + str(args[-1]))

    while True:
        try:
            if obj.dev.waitForNotifications(1.0):
                # handleNotification() was called
                continue
        except BTLEDisconnectError:
            logger.info("BLE disconnected")
            break
        except Exception:
            logger.exception('Unhandled error')
            break
