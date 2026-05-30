from datetime import datetime
import time

import RPi.GPIO as GPIO
from py_scripts.custom_logger import logger
from py_scripts.smoothing_window import MedianWindow, clamp
from config import get_settings
from kv.redis_kv import models


class UltrasonicLoop:
    def __init__(self) -> None:
        # при старте системы положим прошлое значение ультрасоника
        self.window = MedianWindow(
            size=5,
            init_value=float(models.get_prop_value('SONIC__RANGE_AVG', '0')),
        )
        # при старте системы положим прошлое значение ультрасоника
        # self.window = SmoothingWindow(
        #     size=5,
        #     init_value=float(models.get_prop_value('SONIC__RANGE_AVG', '0')),
        #     kernell_func=gauss_kernel,
        # )

    def _update_settings(self):
        settings = get_settings()
        if settings is not None:
            self.settings = settings
        if self.settings is None:
            return False
        self.TRIG = self.settings.sonic_trigger_pin
        self.ECHO = self.settings.sonic_echo_pin
        GPIO.setup(self.TRIG, GPIO.OUT)
        GPIO.setup(self.ECHO, GPIO.IN)

        return True

    def update(self):
        if self._update_settings() is False:
            logger.warning('Settings is None. Skipping')
            return

        GPIO.output(self.TRIG, False)            # Set TRIG as LOW
        time.sleep(1)                            # Delay of 1 seconds

        GPIO.output(self.TRIG, True)             # Set TRIG as HIGH
        time.sleep(0.00001)                      # Delay of 0.00001 seconds
        GPIO.output(self.TRIG, False)            # Set TRIG as LOW

        counter = 0
        pulse_start = time.time()
        while GPIO.input(self.ECHO) == 0:        # Check if Echo is LOW
            pulse_start = time.time()            # Time of the last  LOW pulse
            counter += 1
            if counter > 40000:
                logger.debug('Ultrasonic stuck to get ECHO=0')
                return

        counter = 0
        pulse_end = time.time()
        while GPIO.input(self.ECHO) == 1:        # Check whether Echo is HIGH
            pulse_end = time.time()              # Time of the last HIGH pulse
            counter += 1
            if counter > 40000:
                logger.debug('Ultrasonic stuck to get ECHO=1')
                return

        pulse_duration = pulse_end - pulse_start  # pulse duration to a variable

        distance = pulse_duration * 17150        # Calculate distance
        distance = round(distance, 2)            # Round to two decimal points

        if distance > 1000:  # 10 meters is impossible
            # this is GC problem,
            # but once we get large number it's not a good value
            # we cannot even smooth this out because it's an extrem outlier
            logger.debug('LARGE range=%.2f', distance)
            return

        range = int(clamp(distance, 20, 400))
        self.window.append(range)

        avg_range = int(self.window.smoothed_value())
        logger.info('range=%.2f avg=%.2f', range, avg_range)

        last_time = str(datetime.now().isoformat())

        models.set_prop_value("SONIC__RANGE", str(range))
        models.set_prop_value("SONIC__RANGE_AVG", str(avg_range))
        models.set_prop_value("SONIC__LAST_TIME", last_time)

        models.set_prop_value("DISTANCE", str(range))
        models.set_prop_value("DISTANCE__AVG", str(avg_range))
        models.set_prop_value("DISTANCE__LAST_TIME", last_time)


def main():
    GPIO.setmode(GPIO.BOARD)
    looper = UltrasonicLoop()
    while True:
        try:
            looper.update()
        except Exception:
            logger.exception('Failed to update ultrasonic')
            time.sleep(5)


if __name__ == '__main__':
    main()
