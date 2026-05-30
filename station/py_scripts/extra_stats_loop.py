import os
import time

import requests
from pydantic import BaseModel

from kv.redis_kv import models
from py_scripts.config import get_settings
from py_scripts.custom_logger import logger
from py_scripts.schedule import Interval


class ExtraStats(BaseModel):
    is_occupied: bool
    is_reed_installed: bool


class ExtraStatsLoop:
    def __init__(self) -> None:
        self.update_settings()
        self.interval = Interval(10)
        self.prev_is_occupied = True
        self.prev_is_reed_installed = False

    def update_settings(self):
        self.token_key = os.environ['TOKEN_KEY']
        self.settings = get_settings()
        self.url = f"{self.settings.api_url}/main/api/v1/space_extra_stat"
        self.threshold_distance = self.settings.sonic_car_distance

    def update(self):
        self.update_settings()
        reed_value = models.get_prop_value('REED_VALUE', '1')
        is_reed_installed = reed_value == '1'
        distance_avg = float(models.get_prop_value('DISTANCE__AVG', '0') or 0)
        park_lock_status = models.get_prop_value("PARKLOCK__LAST_STATUS")
        is_occupied = (
            distance_avg < self.threshold_distance and
            (not park_lock_status or park_lock_status == "UNLOCKED")
        )
        # как только что-то поменялось, то отправляем уведомление на сервер
        # иначе, все равно отправляем статус, но реже, раз в N секунд
        # как задано в Interval. Это сделано, чтобы данные все таки приходили
        # и поддерживали систему в актуальном состоянии
        changed = (
            is_occupied != self.prev_is_occupied or
            is_reed_installed != self.prev_is_reed_installed
        )
        self.prev_is_occupied = is_occupied
        self.prev_is_reed_installed = is_reed_installed

        if changed or self.interval.check():
            data = ExtraStats(
                is_occupied=is_occupied,
                is_reed_installed=is_reed_installed,
            )
            self.send_extra_stats(data)

    def send_extra_stats(self, data: ExtraStats):
        try:
            logger.info("Send extra stats", data=data.json())
            req = requests.post(
                self.url,
                headers={'Authorization': 'Bearer ' + self.token_key},
                json=data.dict(),
                timeout=30,
            )
            req.raise_for_status()
        except Exception:
            logger.exception('Failed to send extra stats')


def main():
    logger.info('extra stats loop started')
    loop = ExtraStatsLoop()
    try:
        while True:
            loop.update()
            time.sleep(1)
    except Exception:
        logger.exception('Unhandled exception')


if __name__ == '__main__':
    main()
