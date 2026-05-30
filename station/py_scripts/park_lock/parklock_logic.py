from datetime import datetime
from typing import Callable, Optional, Union

from py_scripts.custom_logger import logger

from kv.redis_kv import Redis
from py_scripts.config import SettingsLoader
from py_scripts.config_model import Settings


def parse_float(value: str, default_value: float):
    try:
        return float(value)
    except ValueError:
        return default_value


class ParkLock:
    def __init__(
            self,
            lock_fn: Callable[[], None],
            unlock_fn: Callable[[], None],
            init_fn: Callable[[], None],
            db: Redis,
            settings_loader: SettingsLoader,
    ):
        self.FORCE_SYNC_DT_SECONDS = 60
        self.WAIT_TIME = 15
        # DEPRECATION_TIME фиксирует максимальное время актуальности проерок
        # если включилась система и видит, что парковка не занята машинами
        # больше чем DEPRECATION_TIME, то значит, что-то зависло и надо
        # заново ждать WAIT_TIME свободности парковки
        self.DEPRECATION_TIME = self.WAIT_TIME + 15

        self.db = db  # see redis_kv.py
        self.lock_fn = lock_fn
        self.unlock_fn = unlock_fn
        self.init_fn = init_fn
        self.last_time_sync = datetime.min
        self.settings_loader = settings_loader  # see config.py

    @property
    def settings(self) -> Union[Settings, None]:
        return self.settings_loader.settings

    def status_changed(self) -> bool:
        last_status = self.db.get_prop_value("PARKLOCK__LAST_STATUS")
        logger.info(f"Last status: {last_status}")
        need_status = self.db.get_prop_value("PARKLOCK__NEED_STATUS")
        logger.info(f"Need status: {need_status}")
        return last_status != need_status

    def force_sync_required(self) -> bool:
        now = datetime.now()
        dt = now - self.last_time_sync
        return dt.total_seconds() > self.FORCE_SYNC_DT_SECONDS

    def distance(self) -> float:
        distance_avg = self.db.get_prop_value("DISTANCE__AVG", "0") or "0"
        return parse_float(distance_avg, 0)

    def locked_by_car(self) -> bool:
        # distance - это расстояние от ультрасоника до земли
        # если distance=0 то значит под ультрасоником что-то стоит
        # Пусть лидар на высоте 300см.
        # Обычно distance будет 290..310 см с учетом погрешности и ветра.
        # Когда приедет машина, тогда distance будет сильно меньше 290.
        # Поэтому в базе данных задаем порог срабатывания меньше на 20 см,
        #  чем высота крепления. И машины, высотой от 20 см будут определяться.
        if self.settings and self.settings.sonic_car_distance:
            return self.distance() < self.settings.sonic_car_distance
        return True

    def parse_and_update_wait_time(self) -> Optional[datetime]:
        now = datetime.now()

        wait_time_str = self.db.get_prop_value("PARKLOCK__WAIT_TIME")
        if not wait_time_str:
            self.db.set_prop_value("PARKLOCK__WAIT_TIME", now.isoformat())
            logger.info("Reset PARKLOCK__WAIT_TIME: not set", elapsed_time=0)
            return None

        try:
            wait_time = datetime.fromisoformat(wait_time_str)
        except Exception:
            self.db.set_prop_value("PARKLOCK__WAIT_TIME", now.isoformat())
            logger.info(
                "Reset PARKLOCK__WAIT_TIME: datetime parse error",
                wait_time_str=wait_time_str,
                elapsed_time=0,
            )
            return None

        return wait_time

    def no_car_last_seconds(self) -> bool:
        wait_time = self.parse_and_update_wait_time()
        if wait_time is None:
            return False

        now = datetime.now()
        elapsed_time = (now - wait_time).total_seconds()
        if elapsed_time > self.DEPRECATION_TIME:
            # подозрительная ситуация, что ждем СЛИШКОМ долго,
            # хотя проверка запускатеся каждую секунду.
            # эта проверка для надежности, если система была перезапущена
            # и теперь считает, что она уже все проверила и можно закрывать.
            self.db.set_prop_value("PARKLOCK__WAIT_TIME", now.isoformat())
            logger.info(
                'Reset PARKLOCK__WAIT_TIME: deprecated',
                elapsed_time=elapsed_time,
            )
            return False

        if elapsed_time > self.WAIT_TIME:
            logger.info("Timeout: allow to lock", elapsed_time=elapsed_time)
            return True

        # ждем до WAIT_TIME...
        logger.info("Car was resently: waiting.", elapsed_time=elapsed_time)
        return False

    def do_lock(self) -> None:
        self.db.set_prop_value("PARKLOCK__WAIT_TIME", "-")
        self.last_time_sync = datetime.now()
        self.lock_fn()

    def do_unlock(self) -> None:
        self.db.set_prop_value("PARKLOCK__WAIT_TIME", "-")
        self.last_time_sync = datetime.now()
        self.unlock_fn()

    def do_init(self) -> None:
        self.db.set_prop_value("PARKLOCK__WAIT_TIME", "-")
        self.last_time_sync = datetime.now()
        self.init_fn()

    def check(self) -> None:
        # либо поменялся статус, либо мы давно не проверяли состояние парклоков
        #
        # могло быть так, что систему перезагрузили.
        # По прошлым данным парклок поднят, а на самом деле парклок лежит.
        # Лучше изредка явно отправить команду закройся даже закрытому парклоку.
        if not self.status_changed() and not self.force_sync_required():
            logger.info(
                "Park lock do nothing",
                last_sync=self.last_time_sync.isoformat(),
            )
            return

        if self.force_sync_required():
            logger.info('Force sync', last_sync=self.last_time_sync.isoformat())

        status = self.db.get_prop_value("PARKLOCK__NEED_STATUS")
        logger.info(f"Status: {status}")
        if status == "LOCKED":
            if self.locked_by_car():
                # машина под парклоком.
                # НИ В КОЕМ случае нельзя поднимать парклок
                # Обнуляем таймер. Когда машина уедет, то будет проверка
                # времени. Так как оно не задано, выставят now и отложат
                # проверку на еще один такт.
                # Это гарантирует, что если система
                # перезагрузилась вот прямо сейчас, то в следующий раз, придестя
                # время заново вычислять и выставлять в now,
                # а не использовать старые данные.
                self.db.set_prop_value("PARKLOCK__WAIT_TIME", "-")
                logger.info(
                    'Reset PARKLOCK__WAIT_TIME: locked by a car',
                    dst=self.distance,
                )
            elif self.no_car_last_seconds():
                # никого не было под парклоком последние N секунд
                self.do_lock()
            # else: waiting
        elif status == "UNLOCKED":
            self.do_unlock()
        elif status == "INIT":
            self.do_init()
        else:
            logger.warning('Unknown status', PARKLOCK__NEED_STATUS=status)
