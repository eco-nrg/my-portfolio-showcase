from decimal import Decimal
from main.utils.datetime_constants import MINUTES_IN_HOUR, SECONDS_IN_MINUTE


def get_per_minute_cost(
    payed_seconds: Decimal,
    price_hour: Decimal,
) -> Decimal:
    return (
        round(payed_seconds / SECONDS_IN_MINUTE) *
        (price_hour / MINUTES_IN_HOUR)
    )
