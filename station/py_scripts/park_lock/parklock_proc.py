import os
import sys
import math
import datetime
import time
from bluepy import btle
from bluepy.btle import BTLEDisconnectError
from Crypto.Cipher import AES
from py_scripts.config import settings_loader, get_settings
from py_scripts.custom_logger import logger

from py_scripts.park_lock.parklock_logic import ParkLock
from kv.redis_kv import models
import RPi.GPIO as GPIO

settings = get_settings()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


device_mac = settings.parklock_mac
parklock_pin = settings.parklock_pin
sonic_led_pin = settings.sonic_led_pin
sonic_trigger_pin = settings.sonic_trigger_pin
sonic_echo_pin = settings.sonic_echo_pin

TRIG = 10 # 15                                  # Associate pin 15 to TRIG
ECHO = 8 # 14                                   # Associate pin 14 to Echo
DISTANCE = 250


adminPassword = "0970456745"
unlockKey = "0344382141"
aes_key = bytes([0x98,0x76,0x23,0xe8,0xa9,0x23,0xa1,0xbb,0x3d,0x9e,0x7d,0x03,0x78,0x12,0x45,0x88])
uid_key = bytes([0x00,0x42,0xcb,0x6e])
session_key = None

requests = list()
buffer = list()

TTL_WRITE = None
# TTL_READ = None


dscrc_table = [0, 0x5E, 0xBC, 0xE2, 0x61, 0x3F, 0xDD, 0x83, 0xC2,
    0x9C, 0x7E, 0x20, 0xA3, 0xFD, 0x1F, 0x41, 0x9D, 0xC3,
    0x21, 0x7F, 0xFC, 0xA2, 0x40, 0x1E, 0x5F, 1, 0xE3,
    0xBD, 0x3E, 0x60, 0x82, 0xDC, 0x23, 7, 0x9F, 0xC1,
    0x42, 0x1C, 0xFE, 0xA0, 0xE1, 0xBF, 0x5D, 3, 0x80,
    0xDE, 0x3C, 0x62, 0xBE, 0xE0, 2, 0x5C, 0xDF, 0x81,
    0x63, 0x3D, 0x7C, 0x22, 0xC0, 0x9E, 0x1D, 0x43, 0xA1,
    0xFF, 0x46, 0x18, 0xFA, 0xA4, 0x27, 0x79, 0x9B, 0xC5,
    0x84, 0xDA, 0x38, 0x66, 0xE5, 0xBB, 0x59, 7, 0xDB,
    0x85, 0x67, 0x39, 0xBA, 0xE4, 6, 0x58, 0x19, 0x47,
    0xA5, 0xFB, 0x78, 0x26, 0xC4, 0x9A, 0x65, 0x3B, 0xD9,
    0x87, 4, 0x5A, 0xB8, 0xE6, 0xA7, 0xF9, 0x1B, 0x45,
    0xC6, 0x98, 0x7A, 0x24, 0xF8, 0xA6, 0x44, 0x1A, 0x99,
    0xC7, 0x25, 0x7B, 0x3A, 0x64, 0x86, 0xD8, 0x5B, 5,
    0xE7, 0xB9, 0x8C, 0xD2, 0x30, 0x6E, 0xED, 0xB3, 0x51,
    0xF, 0x4E, 0x10, 0xF2, 0xAC, 0x2F, 0x71, 0x93, 0xCD,
    0x11, 0x4F, 0xAD, 0xF3, 0x70, 0x2E, 0xCC, 0x92, 0xD3,
    0x8D, 0x6F, 0x31, 0xB2, 0xEC, 0xE, 0x50, 0xAF, 0xF1,
    0x13, 0x4D, 0xCE, 0x90, 0x72, 0x2C, 0x6D, 0x33, 0xD1,
    0x8F, 0xC, 0x52, 0xB0, 0xEE, 0x32, 0x6C, 0x8E, 0xD0,
    0x53, 0xD, 0xEF, 0xB1, 0xF0, 0xAE, 0x4C, 0x12, 0x91,
    0xCF, 0x2D, 0x73, 0xCA, 0x94, 0x76, 0x28, 0xAB, 0xF5,
    0x17, 0x49, 8, 0x56, 0xB4, 0xEA, 0x69, 0x37, 0xD5,
    0x8B, 0x57, 9, 0xEB, 0xB5, 0x36, 0x68, 0x8A, 0xD4,
    0x95, 0xCB, 0x29, 0x77, 0xF4, 0xAA, 0x48, 0x16, 0xE9,
    0xB7, 0x55, 0xB, 0x88, 0xD6, 0x34, 0x6A, 0x2B, 0x75,
    0x97, 0xC9, 0x4A, 0x14, 0xF6, 0xA8, 0x74, 0x2A, 0xC8,
    0x96, 0x15, 0x4B, 0xA9, 0xF7, 0xB6, 0xE8, 0xA, 0x54,
    0xD7, 0x89, 0x6B, 0x35
]



GPIO.setmode(GPIO.BOARD)                   #Set GPIO pin numbering 

# print("Distance measurement in progress")

# GPIO.setup(sonic_trigger_pin ,GPIO.OUT)                  #Set pin as GPIO out
# GPIO.setup(sonic_echo_pin,GPIO.IN)                   #Set pin as GPIO in
# pulse_end = time.time()
# pulse_start = time.time()


def get_key_path(mac_addr):
    file_path = os.path.join(BASE_DIR, '{}.key'.format(mac_addr.replace(':', '-')))
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


def crccompute(to_compute):
    res = 0
    for el in to_compute:
        res = dscrc_table[(res ^ el) & 0xFF]

    return res


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
    cipher = AES.new(key, AES.MODE_CBC, key)
    return cipher.decrypt(ciphertext)


def generate_message(command_code, data_bytes=None, key=None):
    arr = [0x7F, 0x5A, 0x05, 0x03, 0x01, 0x00, 0x01, 0x00, 0x01, command_code, 0xAA, 0]
    if data_bytes is not None:
        if key is None:
            key = aes_key
        crypted = aesEncrypt(data_bytes, key)
        arr[-1] = len(crypted)
        arr += crypted

    arr += [crccompute(arr), 0x0D, 0x0A]
    return arr


def integerToByteArray(integer):
    res = [0, 0, 0, 0]
    bitShift = [24, 16, 8, 0]
    for byteIdx in range(4):
        res[byteIdx] = (integer >> bitShift[byteIdx]) & 0xff
    return bytes(res)


def fourBytesToLong(val):
    return (val[0] << 24) + (val[1] << 16 & 0xFF0000) + (val[2] << 8 & 0xFF00) + (val[3] & 0xFF)


def convertTimeToByteArray(timeStr):
    length = len(timeStr) // 2
    res = [0 for _ in range(length)]
    for i in range(length):
        _2i = i * 2
        res[i] = int(timeStr[_2i:_2i+2])

    return bytes(res)


class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        global buffer
        global requests
        global access_key
        global session_key
        buffer += list(data)

        if buffer[-2] == 0xD and buffer[-1] == 0xA:
            request_type, request = requests[0]
            del requests[0]
            response = bytes(buffer)
            buffer = list()
            logger.debug("request", request_type=request_type, len=len(request))
            # print_hex_array(request)
            logger.debug("response", len=len(response))
            # print_hex_array(response)

            if request_type == "COMM_INITIALIZATION":
                # COMM_GET_AES_KEY
                data_raw = b'SCIENER\t\t\t\t\t\t\t\t\t'
                mess = bytes(generate_message(0x19, data_raw))
                for idx in range(int(math.ceil(len(mess) / 20))):
                    TTL_WRITE.write(mess[20 * idx: 20 * idx + 20], True)
                requests.append(("COMM_GET_AES_KEY", mess))

            elif request_type == "COMM_GET_AES_KEY":
                data_length = response[11]
                if data_length != 32:
                    raise ValueError("data_length != 32: " + str(int(data_length)))
                data2 = response[12:12+data_length]
                decoded = aesDecrypt(data2, aes_key)
                # print("decoded")
                # print_hex_array(decoded)

                if decoded[0] != 0x19:
                    raise ValueError("decoded[0] != 0x19: " + str(hex(decoded[0])))
                if decoded[1] != 0x1:
                    raise ValueError("decoded[1] != 0x1: " + str(hex(decoded[1])))

                access_key = bytes(decoded[2:18])
                write_key(device_mac, access_key)

                # print("access_key:")
                # print_hex_array(access_key)

                # start command
                # COMM_ADD_ADMIN
                adminPasswd = integerToByteArray(int(adminPassword))
                unlockCode = integerToByteArray(int(unlockKey))
                data_raw = adminPasswd + unlockCode + bytes([0x53,0x43,0x49,0x45,0x4e,0x45,0x52]) + bytes([0x1])
                mess = bytes(generate_message(0x56, data_raw, access_key))
                for idx in range(int(math.ceil(len(mess) / 20))):
                    TTL_WRITE.write(mess[20 * idx: 20 * idx + 20], True)
                requests.append(("COMM_ADD_ADMIN", mess))
                # end command

            elif request_type == "COMM_ADD_ADMIN":
                data_length = response[11]
                if data_length % 16 != 0 or data_length == 0:
                    raise ValueError("data_length % 16 != 0: " + str(int(data_length)))
                data2 = response[12:12+data_length]
                decoded = aesDecrypt(data2, access_key)
                # print("decoded")
                # print_hex_array(decoded)

                if decoded[0] != 0x56:
                    raise ValueError("decoded[0] != 0x56: " + str(hex(decoded[0])))
                if decoded[1] != 0x1:
                    raise ValueError("decoded[1] != 0x1: " + str(hex(decoded[1])))

                # start command
                # COMM_TIME_CALIBRATE
                daytime = datetime.datetime.now().strftime("%y%m%d%H%M%S")
                # print(daytime)
                data_raw = convertTimeToByteArray(daytime)
                if len(data_raw) % 16 != 0:
                    count = 16 - (len(data_raw) % 16)
                    data_raw += bytes([count] * count)
                mess = bytes(generate_message(0x43, data_raw, access_key))
                for idx in range(int(math.ceil(len(mess) / 20))):
                    TTL_WRITE.write(mess[20 * idx: 20 * idx + 20], True)
                requests.append(("COMM_TIME_CALIBRATE", mess))
                # end command

            elif request_type == "COMM_TIME_CALIBRATE":
                data_length = response[11]
                if data_length % 16 != 0 or data_length == 0:
                    raise ValueError("data_length % 16 != 0: " + str(int(data_length)))
                data2 = response[12:12+data_length]
                decoded = aesDecrypt(data2, access_key)
                # print("decoded")
                # print_hex_array(decoded)

                if decoded[0] != 0x43:
                    raise ValueError("decoded[0] != 0x43: " + str(hex(decoded[0])))
                if decoded[1] != 0x1:
                    raise ValueError("decoded[1] != 0x1: " + str(hex(decoded[1])))

                # start command
                # COMM_GET_ALARM_ERRCORD_OR_OPERATION_FINISHED
                data_raw = bytes()
                mess = bytes(generate_message(0x57, data_raw, access_key))
                for idx in range(int(math.ceil(len(mess) / 20))):
                    TTL_WRITE.write(mess[20 * idx: 20 * idx + 20], True)
                requests.append(("COMM_GET_ALARM_ERRCORD_OR_OPERATION_FINISHED", mess))
                # end command
                
            elif request_type == "COMM_GET_ALARM_ERRCORD_OR_OPERATION_FINISHED":
                data_length = response[11]
                if data_length % 16 != 0 or data_length == 0:
                    raise ValueError("data_length % 16 != 0: " + str(int(data_length)))
                data2 = response[12:12+data_length]
                decoded = aesDecrypt(data2, access_key)
                # print("decoded")
                # print_hex_array(decoded)

                if decoded[0] != 0x57:
                    raise ValueError("decoded[0] != 0x57: " + str(hex(decoded[0])))
                if decoded[1] != 0x1:
                    raise ValueError("decoded[1] != 0x1: " + str(hex(decoded[1])))

                # start command
                # COMM_CHECK_USER_TIME
                data_raw = bytes([0x00,0x01,0x1f,0x14,0x00] + [0x63,0x0b,0x1e,0x14,0x00] + [0x00,0x00,0x00]) + uid_key
                if len(data_raw) % 16 != 0:
                    count = 16 - (len(data_raw) % 16)
                    data_raw += bytes([count] * count)
                mess = bytes(generate_message(0x55, data_raw, access_key))
                for idx in range(int(math.ceil(len(mess) / 20))):
                    TTL_WRITE.write(mess[20 * idx: 20 * idx + 20], True)
                requests.append(("COMM_CHECK_USER_TIME", mess))
                # end command

            elif request_type == "COMM_CHECK_USER_TIME":
                data_length = response[11]
                if data_length % 16 != 0 or data_length == 0:
                    raise ValueError("data_length % 16 != 0: " + str(int(data_length)))
                data2 = response[12:12+data_length]
                decoded = aesDecrypt(data2, access_key)
                # print("decoded")
                # print_hex_array(decoded)

                if decoded[0] != 0x55:
                    raise ValueError("decoded[0] != 0x55: " + str(hex(decoded[0])))
                if decoded[1] != 0x1:
                    raise ValueError("decoded[1] != 0x1: " + str(hex(decoded[1])))

                session_key = decoded[2:6]
                # print("session_key")
                # print_hex_array(session_key)

                # start command
                # COMM_CHECK_RANDOM
                lockPwd = str(fourBytesToLong(session_key) + int(unlockKey))
                lockPwdArr = integerToByteArray(int(lockPwd))

                data_raw = bytes(lockPwdArr)
                if len(data_raw) % 16 != 0:
                    count = 16 - (len(data_raw) % 16)
                    data_raw += bytes([count] * count)
                mess = bytes(generate_message(0x30, data_raw, access_key))
                for idx in range(int(math.ceil(len(mess) / 20))):
                    TTL_WRITE.write(mess[20 * idx: 20 * idx + 20], True)
                requests.append(("COMM_CHECK_RANDOM", mess))
                # end command

            elif request_type == "COMM_CHECK_RANDOM":
                data_length = response[11]
                if data_length % 16 != 0 or data_length == 0:
                    raise ValueError("data_length % 16 != 0: " + str(int(data_length)))
                data2 = response[12:12+data_length]
                decoded = aesDecrypt(data2, access_key)
                # print("decoded")
                # print_hex_array(decoded)

                if decoded[0] != 0x30:
                    raise ValueError("decoded[0] != 0x30: " + str(hex(decoded[0])))
                if decoded[1] != 0x1:
                    raise ValueError("decoded[1] != 0x1: " + str(hex(decoded[1])))

                logger.debug("battery: %d", int(decoded[3]))

                # start command
                # COMM_TIME_CALIBRATE
                daytime = datetime.datetime.now().strftime("%y%m%d%H%M%S")
                # print(daytime)
                data_raw = convertTimeToByteArray(daytime)
                if len(data_raw) % 16 != 0:
                    count = 16 - (len(data_raw) % 16)
                    data_raw += bytes([count] * count)
                mess = bytes(generate_message(0x43, data_raw, access_key))
                for idx in range(int(math.ceil(len(mess) / 20))):
                    TTL_WRITE.write(mess[20 * idx: 20 * idx + 20], True)
                requests.append(("COMM_TIME_CALIBRATE2", mess))
                # end command

            elif request_type == "COMM_TIME_CALIBRATE2":
                data_length = response[11]
                if data_length % 16 != 0 or data_length == 0:
                    raise ValueError("data_length % 16 != 0: " + str(int(data_length)))
                data2 = response[12:12+data_length]
                decoded = aesDecrypt(data2, access_key)
                # print("decoded")
                # print_hex_array(decoded)

                if decoded[0] != 0x43:
                    raise ValueError("decoded[0] != 0x43: " + str(hex(decoded[0])))
                if decoded[1] != 0x1:
                    raise ValueError("decoded[1] != 0x1: " + str(hex(decoded[1])))

                models.set_prop_value("PARKLOCK__LAST_STATUS", "INIT")
                logger.info("initiated")

            elif request_type == "COMM_CHECK_ADMIN:LOCK":
                data_length = response[11]
                if data_length % 16 != 0 or data_length == 0:
                    raise ValueError("data_length % 16 != 0: " + str(int(data_length)))
                data2 = response[12:12+data_length]
                decoded = aesDecrypt(data2, access_key)
                # print("decoded")
                # print_hex_array(decoded)

                if decoded[0] != 0x41:
                    raise ValueError("decoded[0] != 0x41: " + str(hex(decoded[0])))
                if decoded[1] != 0x1:
                    raise ValueError("decoded[1] != 0x1: " + str(hex(decoded[1])))

                session_key = decoded[2:6]
                # print("session_key")
                # print_hex_array(session_key)

                # start command
                # COMM_FUNCTION_LOCK
                lockPwd = str(fourBytesToLong(session_key) + int(unlockKey))
                lockPwdArr = integerToByteArray(int(lockPwd))
                unlockDate = integerToByteArray(int(time.time()))

                data_raw = lockPwdArr + unlockDate
                if len(data_raw) % 16 != 0:
                    count = 16 - (len(data_raw) % 16)
                    data_raw += bytes([count] * count)
                mess = bytes(generate_message(0x58, data_raw, access_key))
                for idx in range(int(math.ceil(len(mess) / 20))):
                    TTL_WRITE.write(mess[20 * idx: 20 * idx + 20], True)
                requests.append(("COMM_FUNCTION_LOCK1", mess))
                requests.append(("COMM_FUNCTION_LOCK2", mess))
                # end command

            elif request_type == "COMM_FUNCTION_LOCK1":
                data_length = response[11]
                if data_length % 16 != 0 or data_length == 0:
                    raise ValueError("data_length % 16 != 0: " + str(int(data_length)))
                data2 = response[12:12+data_length]
                decoded = aesDecrypt(data2, access_key)
                logger.debug("decoded")
                print_hex_array(decoded)

            elif request_type == "COMM_FUNCTION_LOCK2":
                data_length = response[11]
                if data_length % 16 != 0 or data_length == 0:
                    raise ValueError("data_length % 16 != 0: " + str(int(data_length)))
                data2 = response[12:12+data_length]
                decoded = aesDecrypt(data2, access_key)
                logger.debug("decoded")
                print_hex_array(decoded)

                models.set_prop_value("PARKLOCK__LAST_STATUS", "LOCKED")
                logger.info("locked")


            elif request_type == "COMM_CHECK_ADMIN:UNLOCK":
                data_length = response[11]
                if data_length % 16 != 0 or data_length == 0:
                    raise ValueError("data_length % 16 != 0: " + str(int(data_length)))
                data2 = response[12:12+data_length]
                decoded = aesDecrypt(data2, access_key)
                # print("decoded")
                # print_hex_array(decoded)

                if decoded[0] != 0x41:
                    raise ValueError("decoded[0] != 0x41: " + str(hex(decoded[0])))
                if decoded[1] != 0x1:
                    raise ValueError("decoded[1] != 0x1: " + str(hex(decoded[1])))

                session_key = decoded[2:6]
                # print("session_key")
                # print_hex_array(session_key)

                # start command
                # COMM_UNLOCK
                lockPwd = str(fourBytesToLong(session_key) + int(unlockKey))
                lockPwdArr = integerToByteArray(int(lockPwd))
                
                timestamp = int(time.time())
                unlockDate = integerToByteArray(timestamp)
                date = datetime.datetime.fromtimestamp(timestamp)
                daytime = date.strftime("%y%m%d%H%M%S")

                data_raw = lockPwdArr + unlockDate + convertTimeToByteArray(daytime)
                if len(data_raw) % 16 != 0:
                    count = 16 - (len(data_raw) % 16)
                    data_raw += bytes([count] * count)
                mess = bytes(generate_message(0x47, data_raw, access_key))
                for idx in range(int(math.ceil(len(mess) / 20))):
                    TTL_WRITE.write(mess[20 * idx: 20 * idx + 20], True)
                requests.append(("COMM_UNLOCK1", mess))
                requests.append(("COMM_UNLOCK2", mess))
                # end command

            elif request_type == "COMM_UNLOCK1":
                data_length = response[11]
                if data_length % 16 != 0 or data_length == 0:
                    raise ValueError("data_length % 16 != 0: " + str(int(data_length)))
                data2 = response[12:12+data_length]
                decoded = aesDecrypt(data2, access_key)
                logger.debug("decoded")
                print_hex_array(decoded)

                models.set_prop_value("PARKLOCK__LAST_STATUS", "UNLOCKED")
                logger.info("unlocked")

            elif request_type == "COMM_UNLOCK2":
                data_length = response[11]
                if data_length % 16 != 0 or data_length == 0:
                    raise ValueError("data_length % 16 != 0: " + str(int(data_length)))
                data2 = response[12:12+data_length]
                decoded = aesDecrypt(data2, access_key)
                logger.debug("decoded")
                print_hex_array(decoded)

            else:
                raise ValueError('request_type:' + str(request_type))


access_key = read_key(device_mac)
dev = None


def connect():
    global dev
    global TTL_WRITE

    # cleanup and initialisation
    global session_key
    global requests
    global buffer
    session_key = None
    requests = list()
    buffer = list()

    dev = btle.Peripheral(device_mac, btle.ADDR_TYPE_PUBLIC)
    dev.setDelegate( MyDelegate() )

    TTL_SERVICE = dev.getServiceByUUID(btle.UUID("00001910-0000-1000-8000-00805f9b34fb"))
    for ch in TTL_SERVICE.getCharacteristics():
        if ch.uuid == "0000fff2-0000-1000-8000-00805f9b34fb":
            TTL_WRITE = ch
        # elif ch.uuid == "0000fff4-0000-1000-8000-00805f9b34fb":
        #     TTL_READ = ch

    ClientCharacteristicConfiguration = None
    descriptors = dev.getDescriptors(1,0x00F)
    for descriptor in descriptors:
        if str(descriptor.uuid) == "00002902-0000-1000-8000-00805f9b34fb":
            ClientCharacteristicConfiguration = descriptor

    ClientCharacteristicConfiguration.write(bytes([0x01, 0x00]))
    resp = ClientCharacteristicConfiguration.read()
    if len(resp) != 2:
        raise ValueError("ClientCharacteristicConfiguration response length != 2")
    if resp[0] != 0x01:
        raise ValueError("ClientCharacteristicConfiguration response[0] != 0x01")
    if resp[1] != 0x00:
        raise ValueError("ClientCharacteristicConfiguration response[1] != 0x00")


    models.set_prop_value("PARKLOCK__LAST_CONNECTION_TIME", str(int(time.time())))


def initialize():
    logger.info("trying to initialize")

    connect()

    # COMM_INITIALIZATION
    mess = bytes(generate_message(0x45))
    TTL_WRITE.write(mess, True)
    requests.append(("COMM_INITIALIZATION", mess))


def lock():
    logger.info("trying to lock")
    connect()

    # # COMM_CHECK_ADMIN
    adminPasswd = integerToByteArray(int(adminPassword))
    data_raw = adminPasswd + bytes([0x00, 0x00, 0x00]) + uid_key
    if len(data_raw) % 16 != 0:
        count = 16 - (len(data_raw) % 16)
        data_raw += bytes([count] * count)
    mess = bytes(generate_message(0x41, data_raw, access_key))
    for idx in range(int(math.ceil(len(mess) / 20))):
        TTL_WRITE.write(mess[20 * idx: 20 * idx + 20], True)
    requests.append(("COMM_CHECK_ADMIN:LOCK", mess))


def unlock():
    logger.info("trying to unlock")
    connect()

    # # COMM_CHECK_ADMIN
    adminPasswd = integerToByteArray(int(adminPassword))
    data_raw = adminPasswd + bytes([0x00, 0x00, 0x00]) + uid_key
    if len(data_raw) % 16 != 0:
        count = 16 - (len(data_raw) % 16)
        data_raw += bytes([count] * count)
    mess = bytes(generate_message(0x41, data_raw, access_key))
    for idx in range(int(math.ceil(len(mess) / 20))):
        TTL_WRITE.write(mess[20 * idx: 20 * idx + 20], True)
    requests.append(("COMM_CHECK_ADMIN:UNLOCK", mess))


def run_loop():
    park_lock = ParkLock(
        lock_fn=lock,
        unlock_fn=unlock,
        init_fn=initialize,
        db=models,
        settings_loader=settings_loader,
    )
    # systemd должен перезапустить систему, если она упадет с исключением
    # поэтому здесь нет смысла отлавливать исключения
    logger.info("parklock loop started")
    while True:
        time.sleep(1)
        park_lock.check()
        wait_bt()
        

def wait_bt():
    global dev
    # Этот код ждет когда по блютузу доставится сообщение на парклок
    if dev is None:
        return
    while True:
        try:
            if dev.waitForNotifications(1.0):
                # handleNotification() was called
                continue
        except BTLEDisconnectError as e:
            logger.info("BLE disconnected")
            break
        except Exception as e:
            logger.exception(e)
            break
    
    dev = None

if __name__ == "__main__":
    args = sys.argv

    if len(args) <= 1:
        raise Exception("No arguments")

    if args[-1] == '-init':
        initialize()
    elif args[-1] == '-lock':
        # Будьте осторожны, не будет проверки с лидара, ультрасоника на расстояние
        lock()
    elif args[-1] == '-unlock':
        # Будьте осторожны, не будет проверки с лидара, ультрасоника на расстояние
        unlock()
    elif args[-1] == '-loop':
        run_loop()
    else:
        raise Exception("Invalid key" + str(args[-1]))

    wait_bt()
