from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from main.utils.datetime_constants import NIGHT_END_AT, NIGHT_START_AT
from main.utils.number_utils import clamp0Int


def is_not_night(time: time) -> bool:
    return NIGHT_END_AT <= time <= NIGHT_START_AT


def is_night(time: time) -> bool:
    return time < NIGHT_END_AT or time > NIGHT_START_AT


def now_time_tz(zone_info: ZoneInfo) -> time:
    return datetime.now(tz=zone_info).time()


def time_between(v: time, start: time, end: time) -> bool:
    if start > end:
        return v >= start or v <= end
    return start <= v <= end


def to_seconds(timedelta: timedelta) -> int:
    return clamp0Int(round(timedelta.total_seconds()))
