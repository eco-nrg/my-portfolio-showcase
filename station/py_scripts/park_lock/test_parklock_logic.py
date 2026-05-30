from py_scripts.park_lock.parklock_logic import ParkLock
from kv.redis_kv import models
import time


def lock_mock():
    print('LOCK FN')
    models.set_prop_value("PARKLOCK__LAST_STATUS", "LOCKED")


def unlock_mock():
    print('UNLOCK FN')
    models.set_prop_value("PARKLOCK__LAST_STATUS", "UNLOCKED")


def init_mock():
    print('INIT FN')
    models.set_prop_value("PARKLOCK__LAST_STATUS", "INIT")


class MockSettings:
    def __init__(self):
        self.sonic_car_distance = 270


class MockSettingsLoader:
    def __init__(self) -> None:
        self._settings = MockSettings()

    @property
    def settings(self):
        return self._settings


def main():
    settings_loader = MockSettingsLoader()
    park_lock = ParkLock(
        lock_mock,
        unlock_mock,
        init_mock,
        models,
        settings_loader,
    )

    while True:
        park_lock.check()
        time.sleep(1)


if __name__ == '__main__':
    main()
