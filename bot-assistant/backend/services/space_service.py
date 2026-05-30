from typing import Dict, List

from backend.routes.space_router import get_all_spaces
from backend.models.views import ConnectorView, SpaceView

import structlog

_logger = structlog.get_logger(__name__)


def connectors_from(space: SpaceView) -> List[str]:
    """
    Select all connector's types from given space
    :param space:
    :return:
    """
    return list([connector.type for connector in space.connectors])


def present_parking_places() -> Dict[str, List[str | List[str]]]:
    """
    Convert List[SpaceView] from /space/all API response
    to dictionary where key is a parking lot and value is a list of their connectors.
    :return: Dict[place, List[connectors]]
    """
    spaces_views: List[SpaceView] = get_all_spaces()

    _logger.debug(
        'space`s response is',
        space_views_response=spaces_views,
    )

    parking_places: Dict[str, List[str | List[str]]] = dict()
    for space in spaces_views:
        if space.lot in parking_places.keys():
            parking_places[space.lot] += connectors_from(space)
        else:
            parking_places[space.lot] = connectors_from(space)

    return parking_places


class ParkingPlaces:
    __parking_places: Dict[str, List[str | List[str]]]

    def __init__(self):
        self.__parking_places = present_parking_places()

    @property
    def parking_places(self):
        return self.__parking_places

    def update_parking_places(self):
        self.__parking_places = present_parking_places()
