import time
from datetime import datetime

from kv.redis_kv import models
from py_scripts.state_model import State


def __get_sonik_last_time():
    if models.get_prop_value("SONIC__LAST_TIME") is None:
        return 0
    else:
        last_time = models.get_prop_value("SONIC__LAST_TIME")
        dt = datetime.fromisoformat(last_time)
        return int(time.mktime(dt.timetuple()))


def __get_lidar_last_time():
    if models.get_prop_value("LIDAR__LAST_TIME") is None:
        return 0
    else:
        last_time = models.get_prop_value("LIDAR__LAST_TIME")
        dt = datetime.fromisoformat(last_time)
        return int(time.mktime(dt.timetuple()))


def get_state() -> State:
    parklock_last_status = models.get_prop_value("PARKLOCK__LAST_STATUS", 1)
    if parklock_last_status == "LOCKED":
        parklock_last_status = 1
    elif parklock_last_status == "UNLOCKED":
        parklock_last_status = 0

    parklock_need_status = models.get_prop_value("PARKLOCK__NEED_STATUS", 1)
    if parklock_need_status == "LOCKED":
        parklock_need_status = 1
    elif parklock_need_status == "UNLOCKED":
        parklock_need_status = 0

    state = models.get_prop_value("STATE", models.STATE_IDLE)

    return State(
        state=state,
        state_val=models.STATES_ARR.index(state),
        no_internet=int(models.get_prop_value("NO_INTERNET", "0")),
        no_internet_iter=int(models.get_prop_value("NO_INTERNET_ITER", "0")),
        no_internet_time=models.get_prop_value("NO_INTERNET_TIME"),
        has_power=int(models.get_prop_value("METER__HAS_POWER", "0")),
        real_has_power=int(models.get_prop_value("REAL_HAS_POWER", "0")),
        parklock_last_status=parklock_last_status,
        parklock_need_status=parklock_need_status,
        parklock_manual_mode=int(models.get_prop_value("PARKLOCK__MANUAL_MODE", 0)),
        wait_time=models.get_prop_value("PARKLOCK__WAIT_TIME", "-"),
        current_a=float(models.get_prop_value("METER__AM_VALUE", "0")),
        current_a_phase_1=float(
            models.get_prop_value("METER__AM_PHASE_1", "0")
        ),
        current_a_phase_2=float(
            models.get_prop_value("METER__AM_PHASE_2", "0")
        ),
        current_a_phase_3=float(
            models.get_prop_value("METER__AM_PHASE_3", "0")
        ),
        current_w=float(models.get_prop_value("METER__WT_VALUE", "0")),
        sonic_range=float(models.get_prop_value("SONIC__RANGE", "0")),
        sonic_range_avg=float(models.get_prop_value("SONIC__RANGE_AVG", "0")),
        sonic_last_time=__get_sonik_last_time(),
        lidar_distance=float(models.get_prop_value("LIDAR__DISTANCE", "0")),
        lidar_last_time=__get_lidar_last_time(),
        reed_value=int(models.get_prop_value("REED_VALUE", "0")),
        total_kw=float(models.get_prop_value("METER__KWT_VALUE", "0")),
        order_id=models.get_prop_value("ORDER_ID", "0"),
        user=models.get_prop_value("USER", "0"),
        space_status=models.get_prop_value("SPACE_STATUS", "0"),
    )
