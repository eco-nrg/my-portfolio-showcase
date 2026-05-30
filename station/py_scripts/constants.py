from enum import Enum
from typing import Dict
from kv.redis_kv import Redis


# Ключи для Redis
PROPERTY_SPACE_PRICE_KWH = 'SPACE__PRICE_KWH'
PROPERTY_SPACE_PRICE_IDLE = 'SPACE__PRICE_IDLE'
PROPERTY_SPACE_MODE = 'SPACE__MODE'


def update_property_if_present(
    data: Dict[str, str],
    property_response: str,
    property_redis_name: str,
    models: Redis,
) -> None:
    value = data.get(property_response)

    if value is not None:
        models.set_prop_value(property_redis_name, value)


# SPACE_MODE
class SPACE_MODES(str, Enum):
    PRODUCTION = 'PROD'
    TEST = 'TEST'
