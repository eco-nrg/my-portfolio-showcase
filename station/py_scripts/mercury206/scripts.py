# coding=utf8
"Console scripts entries"

import sys
import logging
logging.basicConfig(level=logging.DEBUG, format="%(message)s")

from py_scripts.mercury206 import config, commands
from py_scripts.mercury206.communications import open_serial


def sample_config():
    "Create sample INI file"
    config.create_sample_config()
    return 0


def display_readings():
    "Display meter readings"
    settings = config.get_settings()
    port = open_serial(settings['device'])
    readings = commands.display_readings(port, settings['address'])
    print("{} kWh;{} kWh;{} kWh".format(*readings))
    return 0


def instant_vcp():
    "Display instant voltage, current and power consumption"
    settings = config.get_settings()
    port = open_serial(settings['device'])
    voltage, current, power = commands.instant_vcp(port, settings['address'])
    print("{0} V;{1} A;{2} kW".format(voltage, current, power))
    return 0


def turn_on():
    settings = config.get_settings()
    port = open_serial(settings['device'])
    commands.turn_relay(port, settings['address'], True)


def turn_off():
    settings = config.get_settings()
    port = open_serial(settings['device'])
    commands.turn_relay(port, settings['address'], False)

    
def get_relay():
    settings = config.get_settings()
    port = open_serial(settings['device'])
    commands.get_relay(port, settings['address'])


if __name__ == "__main__":
    display_readings()
    instant_vcp()
    
    args = sys.argv
    if args[-1] == '-on':
        turn_on()
        get_relay()
    elif args[-1] == '-off':
        turn_off()
        get_relay()
