from datetime import datetime
import os
import time
from typing import Any, Dict

from kv.redis_kv import models
from py_scripts.space_status import SpaceStatus
from py_scripts.status_model import Status
from py_scripts.config import get_settings


# We check that all info about order contains in models.
# We update info about order in meter_loop.
# So for be sure that info has in model we check before work with it.
def has_order_info() -> bool:
    if (
        models.read("METER__KWT_VALUE") is None or
        models.read("ORDER_START_KW") is None or
        models.read("ORDER_START_TIME") is None
    ):
        return False
    return True


def get_status():
    settings = get_settings()
    data: Dict[str, Any] = dict(
        response=models.STATE_WARNING,
    )
    if settings is not None:
        APP_URL = os.environ["APP_URL"]
        QR_URL_TMPL = APP_URL + "/spaces?id={}"
        state = models.get_prop_value("STATE", models.STATE_IDLE)
        space_status = models.get_prop_value(
            "SPACE_STATUS",
            SpaceStatus.DISABLED,
        )
        has_real_power = models.get_prop_value("REAL_HAS_POWER", "0")
        has_meter_power = models.get_prop_value("METER__HAS_POWER", "0")
        no_internet = models.get_prop_value("NO_INTERNET", "0") == "1"
        station_color_led = models.get_prop_value(
            "LIGHT_COLOR_STATION",
            "WHITE",
        )
        connector_type = settings.connector_type

        if (
            has_real_power == "0" or
            no_internet or
            state == models.STATE_WARNING or
            station_color_led == "RED"
        ):
            res = models.STATE_WARNING
        elif has_meter_power == "0":
            if space_status == SpaceStatus.BOOKED:
                res = models.STATE_BOOKED
            elif space_status == SpaceStatus.AVAILABLE:
                res = models.STATE_IDLE
            elif space_status == SpaceStatus.BUSY:
                res = state
            elif space_status == SpaceStatus.CHARGING:
                res = state
            else:
                res = models.STATE_WARNING
        elif state in [
            models.STATE_IDLE,
            models.STATE_CHARGING,
            models.STATE_CHARGING_START,
            models.STATE_CHARGING_DOWN,
            models.STATE_CHARGING_END,
        ]:
            res = state
        else:
            res = models.STATE_WARNING

        updated_values = {
            "state": state,
            "response": res,
            "am": float(models.get_prop_value("METER__AM_VALUE", "0") or 0),
            "current_kwh": float(
                models.get_prop_value("METER__WT_VALUE", "0") or 0
            ) / 1000,
            "chargingStation": connector_type,
            "sliderCounts": 1,
            "timerSlideChange": 2000,
            "url": QR_URL_TMPL.format(settings.space_id),
        }

        data.update(updated_values)

        if state == models.STATE_CHARGING_DOWN:
            data["sliderCounts"] = 7
        if state == models.STATE_BOOKED:
            booked_until = models.get_prop_value("BOOKED_UNTIL")
            data["booked_until"] = int(booked_until) if booked_until else None
        elif has_meter_power == "1" and has_order_info():
            current_kwt = float(
                models.get_prop_value("METER__KWT_VALUE", "0") or 0,
            )
            start_kwt = float(models.get_prop_value("ORDER_START_KW", "0") or 0)
            data["total_kwh"] = current_kwt - start_kwt
            created = datetime.fromisoformat(
                models.get_prop_value(
                    "ORDER_START_TIME",
                    "1970-01-01",
                ) or "1970-01-01"
            )
            data["created_at"] = int(time.mktime(created.timetuple()) * 1000)

            payed = models.get_prop_value("ORDER_PAYED_TIME", "0") or "0"
            if payed == "0":
                data["start_payed"] = None
            else:
                data["start_payed"] = int(time.mktime(
                    datetime.fromisoformat(payed).timetuple()) * 1000)
            data["freeTime"] = int(float(
                models.get_prop_value("ORDER_USER_FREE_SECONDS", "0") or 0
            ))
    return Status(**data)
