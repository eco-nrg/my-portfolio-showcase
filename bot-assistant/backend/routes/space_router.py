from typing import List

from config import Config
from backend.models.views import SpaceView, ConnectorView

import structlog
import requests

config = Config()
_logger = structlog.get_logger(__name__)
api_token = config.API_TOKEN
api_url = config.API_SERVER_URL
api_path = config.API_BASE_PATH
api_version = config.API_VERSION
api_full_url = f'{api_url}{api_path}{api_version}'
api_all_spaces_path = f'{config.API_SPACES_PATH}{config.API_ALL_SPACES_PATH}'

def get_all_spaces() -> List[SpaceView]:
    """
    Send GET request to api.eco-nrg to get info about all parking spaces.
    :return: List[SpaceView]
    """
    response = requests.get(
        url=f'{api_full_url}{api_all_spaces_path}',
        headers={
            'Authorization': f'Bearer {api_token}',
        },
    )
    request_result = response.json()

    _logger.debug(
        'request was handled',
        response=request_result
    )

    all_spaces: List[SpaceView] = list([
        to_space_view(space) for space in request_result
    ])
    return all_spaces


def to_connector_view(connector: dict) -> ConnectorView:
    current_a = int(connector['current_a']) if 'current_a' in connector else -1
    phases_count = int(connector['phases_count']) if 'phases_count' in connector else -1
    power_kw = int(connector['power_kw']) if 'power_kw' in connector else -1
    type = connector['type'] if 'type' in connector else 'Undefined'

    _logger.debug(
        'getting and converting connectors data',
        current_a=current_a,
        phases_count=phases_count,
        power_kw=power_kw,
        type=type
    )

    return ConnectorView(
        current_a=current_a,
        phases_count=phases_count,
        power_kw=power_kw,
        type=type,
    )


def to_space_view(space: dict) -> SpaceView:
    id = space['id'] if 'id' in space else -1
    lot = space['lot'] if 'lot' in space else 'Undefined'
    name = space['name'] if 'name' in space else 'Undefined'
    position = space['position'] if 'position' in space else -1
    price_kwh = space['price'] if 'price' in space else -1
    price_booking = space['price_booking'] if 'price_booking' in space else -1
    status = space['status'] if 'status' in space else 'Undefined'
    booked_until = space['booked_until'] if 'booked_until' in space else -1
    connectors = list([
        to_connector_view(connector) for connector in space['connectors']
    ]) if 'connectors' in space else []

    _logger.debug(
        'getting and converting space data',
        id=id,
        lot=lot,
        name=name,
        position=position,
        price_kwh=price_kwh,
        price_booking=price_booking,
        status=status,
        booked_until=booked_until,
        connectors=connectors,
    )

    return SpaceView(
        id=id,
        lot=lot,
        name=name,
        position=position,
        price_kwh=price_kwh,
        price_parking=price_booking,
        status=status,
        booked_until=booked_until,
        connectors=connectors,
    )
