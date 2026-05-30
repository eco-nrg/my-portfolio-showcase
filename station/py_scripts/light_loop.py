import time

import RPi.GPIO as GPIO
from config import get_settings

from kv.redis_kv import models

settings = get_settings()

GPIO.setmode(GPIO.BOARD)
GPIO.setup(settings.parklock_pin, GPIO.OUT)
GPIO.setup(settings.sonic_led_pin, GPIO.OUT)

GPIO.output(settings.parklock_pin, GPIO.LOW)
GPIO.output(settings.sonic_led_pin, GPIO.LOW)


while True:
    last_status = models.get_prop_value("PARKLOCK__LAST_STATUS")
    if last_status == "LOCKED":
        if models.get_prop_value("METER__HAS_POWER") == "0":
            # если поднят и нет питания (свободен)
            GPIO.output(settings.parklock_pin, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(settings.parklock_pin, GPIO.LOW)

    elif last_status == "UNLOCKED":
        if models.get_prop_value("METER__HAS_POWER") == "1":
            # если поднят и нет питания (свободен)
            GPIO.output(settings.sonic_led_pin, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(settings.sonic_led_pin, GPIO.LOW)

    time.sleep(0.5)
