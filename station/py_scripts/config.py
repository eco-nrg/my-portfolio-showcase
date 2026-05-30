import json
from typing import Optional

from kv.redis_kv import models
from py_scripts.config_model import Settings
from py_scripts.custom_logger import logger
from py_scripts.hash import get_hash_value


class SettingsLoader:
    def __init__(self) -> None:
        self.__cached_value = None
        self.__cached_hash = None

    def __load_settings(self) -> Optional[Settings]:
        try:
            value_json = models.read('settings')
            if value_json is None:
                return None
            value_dict = json.loads(value_json)
            return Settings(**value_dict)
        except Exception:
            logger.exception('Failed to read settings')
        return None

    def is_settings_cache_update(self) -> bool:
        settings = self.__load_settings()
        if settings is None:
            return False
        settings_hash = get_hash_value(settings.json())
        if self.__cached_hash == settings_hash:
            return False
        return True

    @property
    def settings(self) -> Optional[Settings]:
        new_settings = self.__load_settings()
        if new_settings is None:
            return self.__cached_value
        self.__cached_value = new_settings
        self.__cached_hash = get_hash_value(new_settings.json())
        return self.__cached_value


settings_loader = SettingsLoader()


def get_settings() -> Optional[Settings]:
    return settings_loader.settings


def is_settings_cache_update():
    return settings_loader.is_settings_cache_update()
