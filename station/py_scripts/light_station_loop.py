import sys
import time
from typing import Callable, Dict

import pigpio  # http://abyz.me.uk/rpi/pigpio/python.html
from config import get_settings
from custom_logger import logger

from kv.redis_kv import models
from py_scripts.pinout import BOARD_TO_BCM

pi = pigpio.pi()
if not pi.connected:
    logger.error("Failed to connect to pigpio")
    sys.exit(1)


settings = get_settings()

redPin = BOARD_TO_BCM[settings.red_pin]
greenPin = BOARD_TO_BCM[settings.green_pin]
bluePin = BOARD_TO_BCM[settings.blue_pin]

GREEN_COLOR = "GREEN"
RED_COLOR = "RED"
BLUE_COLOR = "BLUE"
WHITE_COLOR = "WHITE"
ORANGE_COLOR = "ORANGE"

pi.set_mode(redPin, pigpio.OUTPUT)
pi.set_mode(greenPin, pigpio.OUTPUT)
pi.set_mode(bluePin, pigpio.OUTPUT)


def turn_on_pin(pin):
    logger.debug(f"TURN ON {pin}")
    pi.set_mode(pin, pigpio.OUTPUT)
    pi.write(pin, 1)


def turn_off_pin(pin):
    logger.debug(f"TURN OFF {pin}")
    pi.set_mode(pin, pigpio.OUTPUT)
    pi.write(pin, 0)


def turn_red():
    logger.info('turn_red')
    turn_on_pin(redPin)
    turn_off_pin(greenPin)
    turn_off_pin(bluePin)


def turn_green():
    logger.info('turn_green')
    turn_off_pin(redPin)
    turn_on_pin(greenPin)
    turn_off_pin(bluePin)


def turn_blue():
    logger.info('turn_blue')
    turn_off_pin(redPin)
    turn_off_pin(greenPin)
    turn_on_pin(bluePin)


def turn_white():
    logger.info('turn_white')
    turn_on_pin(redPin)
    turn_on_pin(greenPin)
    turn_on_pin(bluePin)


def turn_off_all_pins():
    turn_off_pin(redPin)
    turn_off_pin(greenPin)
    turn_off_pin(bluePin)


def turn_orange():
    logger.info('turn orange')
    turn_red()
    pi.set_PWM_dutycycle(greenPin, 192)


def main():
    logger.info("light station loop started")

    prev_color = None

    colors: Dict[str, Callable] = {
        GREEN_COLOR: turn_green,
        RED_COLOR: turn_red,
        BLUE_COLOR: turn_blue,
        WHITE_COLOR: turn_white,
        ORANGE_COLOR: turn_orange,
    }

    while True:
        current_color = models.get_prop_value("LIGHT_COLOR_STATION")
        if current_color != prev_color:
            color_func = colors.get(current_color, turn_red)
            prev_color = current_color
            if color_func is not None:
                color_func()
            else:
                logger.error(f"Unknow color: {current_color}")
        time.sleep(1)


if __name__ == "__main__":
    main()
