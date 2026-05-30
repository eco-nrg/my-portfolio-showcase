from datetime import time, timedelta
from zoneinfo import ZoneInfo

SECONDS_IN_MINUTE = 60
MINUTES_IN_HOUR = 60

# Двойной простой начинаем после 15 минут обычного простоя
PARKING_CHARGE_TIME = timedelta(minutes=1)
STOP_SESSION_TIME = timedelta(minutes=2)
START_TIMEOUT = timedelta(minutes=5)
NIGHT_START_AT = time(23, 0, 0)
NIGHT_END_AT = time(9, 0, 0)

ZONE_INFO = ZoneInfo("Europe/Moscow")
