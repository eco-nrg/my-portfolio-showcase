import os
from typing import Optional, Union

import redis


class Redis:
    STATE_IDLE = "qr-code"
    STATE_CHARGING = "charging"
    STATE_CHARGING_START = "charging_start"
    STATE_CHARGING_DOWN = "charging_down"
    STATE_CHARGING_END = "charging_end"
    STATE_BOOKED = "booked"
    STATE_WARNING = "warning"
    STATE_SYSTEM_START = "system-start"
    STATES_ARR = [STATE_IDLE,
                  STATE_CHARGING,
                  STATE_CHARGING_START,
                  STATE_CHARGING_DOWN,
                  STATE_CHARGING_END,
                  STATE_BOOKED,
                  STATE_WARNING,
                  STATE_SYSTEM_START]

    def __init__(self, host='localhost', port=6379, db=0):
        self.redis_client = redis.Redis(host=host, port=port, db=db)

    def create(self, key: str, value: Optional[str]):
        if value is None:
            value = 'None'
        self.redis_client.set(key, value)

    def read(self, key: str):
        value = self.redis_client.get(key)
        return value.decode() if value else None

    def update(self, key, value):
        if value is None:
            value = 'None'
        if self.redis_client.exists(key):
            self.redis_client.set(key, value)
        else:
            raise KeyError(f"Key '{key}' does not exist.")

    def delete(self, key):
        if self.redis_client.exists(key):
            self.redis_client.delete(key)
        else:
            raise KeyError(f"Key '{key}' does not exist.")

    def get_all(self):
        keys = self.redis_client.keys('*')
        data = {}
        for key in keys:
            value = self.redis_client.get(key)
            data[key.decode()] = value.decode() if value else None
        return data

    def get_prop_value(
        self,
        key: str,
        default: Union[str, None] = None,
    ) -> Union[str, None]:
        value = self.redis_client.get(key)
        value = value.decode() if value else None
        if value is not None:
            return value
        return default

    def set_prop_value(self, key: str, value: Union[str, int, None]):
        if value is None:
            self.redis_client.delete(key)
            return None
        self.redis_client.set(key, value)
        new_value = self.redis_client.get(key)
        return new_value.decode() if new_value else None


redis_host = os.environ.get('REDIS_HOST', 'localhost')
models = Redis(host=redis_host)
