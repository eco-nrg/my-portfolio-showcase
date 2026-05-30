from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from main.utils.datetime_constants import PARKING_CHARGE_TIME, START_TIMEOUT
from main.utils.datetime_utils import (
    is_night,
    is_not_night,
    now_time_tz,
    to_seconds,
)
from main.utils.number_utils import clamp0Decimal
from main.utils.payment_utils import get_per_minute_cost

from django.conf import settings

MAX_KW_PER_SECOND = 0.1


@dataclass
class OrderSnapshot:
    tz: ZoneInfo
    start_kw: Decimal
    start_time: datetime
    last_kw: Decimal
    last_payed_seconds: Decimal
    last_payed_penalty_seconds: Decimal
    last_updated_at: datetime
    current_a: Decimal
    current_kw: Decimal
    current_time: datetime
    current_is_reed_installed: bool
    current_is_occupied: bool
    price_kw: Decimal
    price_hour: Decimal

    free_seconds: Decimal
    balance: Decimal
    trial_time: Decimal
    idle_amperage_threshold: Decimal

    @property
    def penalty_price_hour(self) -> Decimal:
        return self.price_hour * 2

    @property
    def delta_time(self) -> int:
        dt = self.current_time - self.last_updated_at
        return to_seconds(dt)

    @property
    def total_kw(self) -> Decimal:
        return clamp0Decimal(self.current_kw - self.start_kw)

    @property
    def duration(self) -> timedelta:
        return self.current_time - self.start_time

    @property
    def duration_seconds(self) -> int:
        return to_seconds(self.duration)

    @property
    def cost_kw(self) -> Decimal:
        return (
            min(
                self.total_kw,
                Decimal(self.duration_seconds * MAX_KW_PER_SECOND),
            )
            * self.price_kw
        )

    @property
    def cost_time(self) -> Decimal:
        return get_per_minute_cost(
            max(
                self.current_payed_seconds - PARKING_CHARGE_TIME.seconds,
                Decimal(0),
            ),
            self.price_hour,
        )

    @property
    def cost_penalty(self) -> Decimal:
        return get_per_minute_cost(
            self.current_payed_penalty_seconds,
            self.penalty_price_hour,
        )

    @property
    def cost_parking(self) -> Decimal:
        return get_per_minute_cost(
            self.current_payed_parking_seconds,
            self.penalty_price_hour,
        )

    @property
    def cost_total(self) -> Decimal:
        return self.cost_kw + self.cost_time + self.cost_penalty

    @property
    def is_idle_amperage(self) -> bool:
        return self.current_a < self.idle_amperage_threshold

    @property
    def is_start_timeout_passed(self) -> bool:
        return self.duration > START_TIMEOUT

    @property
    def is_night(self) -> bool:
        now = now_time_tz(self.tz)
        return is_night(now)

    @property
    def is_not_night(self) -> bool:
        now = now_time_tz(self.tz)
        return is_not_night(now)

    @property
    def is_payed_idle_time(self) -> bool:
        return (
            self.is_start_timeout_passed and self.is_idle_amperage and self.is_not_night
        )

    @property
    def is_payed_penalty_time(self) -> bool:
        return not self.current_is_occupied and not self.current_is_reed_installed

    @property
    def is_payed_double_idle_time(self) -> bool:
        return (
            self.is_payed_idle_time
            and self.last_payed_seconds > 2 * PARKING_CHARGE_TIME.total_seconds()
        )

    @property
    def is_payed_parking_time(self) -> bool:
        return self.is_idle_amperage and self.is_not_night

    @property
    def current_payed_seconds(self) -> Decimal:
        if (
            self.is_payed_idle_time
            and not self.is_payed_penalty_time
            and not self.is_payed_double_idle_time
        ):
            return self.last_payed_seconds + self.delta_time
        return self.last_payed_seconds

    @property
    def current_payed_penalty_seconds(self) -> Decimal:
        if self.is_payed_penalty_time or self.is_payed_double_idle_time:
            return self.last_payed_penalty_seconds + self.delta_time
        return self.last_payed_penalty_seconds

    @property
    def current_payed_parking_seconds(self) -> Decimal:
        if self.is_payed_parking_time and not self.is_payed_penalty_time:
            return self.last_payed_penalty_seconds + self.delta_time
        return self.last_payed_penalty_seconds

    @property
    def enough_money(self) -> bool:
        return self.balance > self.cost_total

    @property
    def enough_free_seconds(self) -> bool:
        return self.free_seconds > self.duration_seconds

    @property
    def enough_trial_time(self) -> bool:
        return self.trial_time > self.duration_seconds

    @property
    def less_balance(self) -> bool:
        return self.get_updated_balance() < settings.LESS_BALANCE

    def get_updated_balance(self) -> Decimal:
        return self.balance - self.cost_total
