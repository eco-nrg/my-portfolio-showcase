"""
Fake Loop.

Этот скрипт эмулирует поведение реального meter loop
для того, чтобы можно было тестировать работу системы.
"""

import time
from random import random

import requests
from config import get_settings
from custom_logger import logger

from kv.redis_kv import models
from py_scripts.constants import (
    PROPERTY_SPACE_PRICE_IDLE,
    PROPERTY_SPACE_MODE,
    PROPERTY_SPACE_PRICE_KWH,
    update_property_if_present
)
from py_scripts.space_status import SpaceStatus


def sync_state(data, settings):
    url = f"{settings.api_url}/main/api/v1/space_stat/0/"
    try:
        req = requests.post(
            url,
            json=data,
            headers={"Authorization": f"Bearer {settings.api_token}"},
            timeout=10,
        )
        req.raise_for_status()
        return req.json()
    except requests.exceptions.ConnectionError as e:
        logger.exception("SyncState: No response:", exception=e, exc_info=True)
    except Exception:
        logger.exception("Unhandled error: ")

    return None


# За основу эмуляции брал зарядку https://api.eco-nrg.store/my_admin/main/order/7b8b11b4-cbb7-4ef4-a8f1-abf51afadc54/change/
class FakeMeter:
    total_kw: float
    current_w: float
    current_v: float
    current_a: float
    ticks: int
    timer: int  # количество шагов
    step_time: int  # шаг таймера в секундах

    def __init__(self,
                 duration=18000,  # время всей зарядки в секундах
                 duration_of_end_charging=3600,  # время в секундах, за которое амперы уменшились до 0
                 max_am=32.1,  # амперы во время зарядки
                 v=233,  # напряжение
                 ticks_before_start=5,
                 step_time=600) -> None:
        self.reset()
        self.ticks_before_start = ticks_before_start
        self.initialized = False
        self.timer = 1
        self.step_time = step_time
        self.duration = duration
        self.duration_of_end_charging = duration_of_end_charging
        self.v = v
        self.max_am = max_am
        self.step_am = max_am / duration_of_end_charging

    def update(self):
        # Эмуляция зарядки закончена
        if (self.timer * self.step_time >= self.duration):
            self.current_a = 0
            self.current_w = 0
            return

        # Эмуляция сценария, когда пользователь активировал станцию,
        # но еще не поставил машину на место и не включил зарядку машины
        self.ticks += 1
        if (self.ticks < self.ticks_before_start):
            return

        if not self.initialized:
            self.current_a = 40
            self.initialized = True

        self.timer += 1

        self.current_v = self.v + random()
        if self.timer * self.step_time <= (
            self.duration - self.duration_of_end_charging
        ):
            self.current_a = self.max_am + random()
        # Сила тока уменьшаться, батарея маишны почти зарядилась
        else:
            self.current_a -= (self.step_am * self.step_time)

        # P = U * I (КилоВатт)
        self.current_w = (self.current_v * self.current_a)
        # E = P * t (КилоВатты в час)
        self.total_kw += (self.current_w / 1000) * (self.step_time / 3600)

    def reset(self):
        self.total_kw = 0
        self.current_w = 0
        self.current_v = 0
        self.current_a = 0
        self.ticks = 0
        self.timer = 0
        self.initialized = False


def main():
    logger.info("Started")
    is_on = False
    reed_value = 1
    space_status = models.get_prop_value("SPACE_STATUS", SpaceStatus.AVAILABLE)
    meter = FakeMeter(ticks_before_start=3, step_time=600)
    while True:
        settings = get_settings()
        if settings is None:
            logger.info("Failed to get_settings. Sleeping...")
            time.sleep(2)
            continue
        ACTIVE_CHARGE_AMP = settings.active_amp

        models.set_prop_value("REED_VALUE", 1)
        models.set_prop_value("REAL_HAS_POWER", "1")

        state = models.get_prop_value("STATE", models.STATE_IDLE)

        if (
            state in [models.STATE_CHARGING, models.STATE_CHARGING_DOWN] and
            meter.current_a > ACTIVE_CHARGE_AMP
        ):
            state = models.STATE_CHARGING_START
            models.set_prop_value("STATE", state)
        elif (
            state == models.STATE_CHARGING_START and
            meter.current_a < ACTIVE_CHARGE_AMP
        ):
            state = models.STATE_CHARGING_DOWN
            models.set_prop_value("STATE", state)
        elif (
            state == models.STATE_CHARGING_DOWN and
            reed_value == 1
        ):
            state = models.STATE_CHARGING_END
            models.set_prop_value("STATE", state)

        if is_on or space_status == SpaceStatus.BUSY:
            meter.update()
        else:
            meter.reset()

        data = {
            "space_uid": settings.space_uid,
            "total_kw": meter.total_kw,
            "current_w": meter.current_w,
            "current_v": meter.current_v,
            "current_a": meter.current_a,
        }
        models.set_prop_value("METER__AM_VALUE", str(meter.current_a))
        models.set_prop_value("METER__KWT_VALUE", str(meter.total_kw))
        models.set_prop_value("METER__WT_VALUE", str(meter.current_w))

        remote = sync_state(data, settings)
        if remote is None:
            continue

        logger.info("SyncState: receive data", data=remote)

        is_station_force_disable = data.get("is_disabled")
        is_station_force_disable = ("0"
                                    if is_station_force_disable is None
                                    else str(int(is_station_force_disable))
                                    )

        station_disable = models.get_prop_value("STATION__DISABLED", "0")
        if station_disable != is_station_force_disable:
            models.set_prop_value("STATION__DISABLED", is_station_force_disable)

            if is_station_force_disable == "1":
                logger.info("The station is disabled by the admin")
                models.set_prop_value("LIGHT_COLOR_STATION", "RED")
                models.set_prop_value("STATE", models.STATE_WARNING)
            else:
                models.set_prop_value("LIGHT_COLOR_STATION", "GREEN")
                models.set_prop_value("STATE", models.STATE_IDLE)

        if remote.get("payed_time") is not None:
            models.set_prop_value("ORDER_PAYED_TIME", remote["payed_time"])

        space_status = remote.get("status")

        if not is_on:
            if space_status == SpaceStatus.BOOKED:
                models.set_prop_value("STATE", models.STATE_BOOKED)
                models.set_prop_value("BOOKED_UNTIL", remote["booked_until"])
            if space_status == SpaceStatus.AVAILABLE:
                models.set_prop_value("STATE", models.STATE_IDLE)

        if space_status:
            models.set_prop_value("SPACE_STATUS", space_status)

        price_kwh = remote.get("price_kwh")
        price_kwh = price_kwh if price_kwh is not None else "0"
        models.set_prop_value(PROPERTY_SPACE_PRICE_KWH, price_kwh)

        price_idle = remote.get("price_idle")
        price_idle = price_idle if price_idle is not None else "0"
        models.set_prop_value(PROPERTY_SPACE_PRICE_IDLE, price_idle)

        update_property_if_present(remote,
                                   "mode",
                                   PROPERTY_SPACE_MODE,
                                   models)

        if remote["is_on"] != is_on:  # состояние изменилось
            if remote["is_on"] is True:
                logger.info("up")
                is_on = True
                models.set_prop_value("STATE", models.STATE_CHARGING)
                models.set_prop_value("PARKLOCK__NEED_STATUS", "UNLOCKED")
                models.set_prop_value("ORDER_START_TIME",
                                        remote["start_time"])
                models.set_prop_value(
                    "ORDER_USER_FREE_SECONDS", remote["free_seconds"])
                models.set_prop_value("ORDER_START_KW",
                                        str(remote["start_kw"]))
                models.set_prop_value("METER__HAS_POWER", "1")
            else:
                logger.info("down")
                is_on = False
                models.set_prop_value("STATE", models.STATE_IDLE)
                models.set_prop_value("PARKLOCK__NEED_STATUS", "LOCKED")
                models.set_prop_value("METER__HAS_POWER", "0")

        time.sleep(2)


if __name__ == "__main__":
    main()
