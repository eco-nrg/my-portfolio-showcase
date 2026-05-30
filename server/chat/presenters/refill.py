import time
from typing import Any, Dict, List, Optional, Tuple

import structlog
from pydantic import BaseModel

from chat.presenters.helpers import datetime_as_ms, resolve_media_url
from main.models import (
    Camera,
    City,
    ParkingLot,
    ParkingSpace,
    ParkingSpaceConnector,
    Provider,
    ProviderParkingLot,
    ProviderType,
)

logger = structlog.get_logger(__name__)


class ConnectorView(BaseModel):
    current_a: int
    phases_count: int
    power_kw: int
    type: str


class SpaceView(BaseModel):
    id: int
    name: str
    position: int
    price_kwh: float
    price_parking: float
    status: str  # see SPACE_STATUSES
    booked_until: Optional[int]
    connectors: List[ConnectorView]


provider_type = {
    'PROVIDING': 'Организация предоставляющая услуги',
    'SERVICE': 'Обслуживающая организация',
}


class ProviderView(BaseModel):
    name: str
    address: str
    ogrn: str
    inn: str
    kpp: str
    payment_account: str
    branch_office: str
    pao: str
    bik: str
    correspondent_account: str
    extra_information: Dict[str, Any]


class StationView(BaseModel):
    id: int
    name: str
    address: str
    img_map: str
    img_cam: str
    loc: Optional[Tuple[float, float]]
    img: str
    show: bool
    spaces: List[SpaceView]
    providers: Dict[str, ProviderView]


class CityView(BaseModel):
    name: str  # city name
    station: List[StationView]


class RefillsView(BaseModel):
    data: List[CityView]


def present_connector(connector: ParkingSpaceConnector) -> ConnectorView:
    return ConnectorView(
        type=connector.connector_type,
        phases_count=connector.phases_count,
        current_a=float(connector.max_a),
        power_kw=float(connector.max_kw),
    )


def present_space(space: ParkingSpace) -> SpaceView:
    status = space.status
    return SpaceView(
        id=space.id,
        name=space.name,
        position=space.position,
        status=status,
        booked_until=datetime_as_ms(space.booked_until),
        price_kwh=space.get_price_kw,
        price_parking=space.get_price_hour,
        connectors=[
            present_connector(connector) for connector in space.connectors.all()
        ],
    )


def present_location(lot: ParkingLot) -> Optional[Tuple[float, float]]:
    if lot.latitude is not None and lot.longitude is not None:
        return float(lot.latitude), float(lot.longitude)
    return None


def present_provider(provider: Provider) -> ProviderView:
    return ProviderView(
        name=provider.name,
        address=provider.address,
        ogrn=provider.ogrn,
        inn=provider.inn,
        kpp=provider.kpp,
        payment_account=provider.payment_account,
        branch_office=provider.branch_office,
        pao=provider.pao,
        bik=provider.bik,
        correspondent_account=provider.correspondent_account,
        extra_information=provider.extra_information or {},
    )


def first(arr: Optional[List[ProviderView]]):
    if arr is None or len(arr) == 0:
        return None
    return arr[0]


def get_first_provider(
    entries: Dict[ProviderType, List[ProviderView]],
) -> Dict[ProviderType, ProviderView]:
    res: Dict[ProviderType, ProviderView] = {}
    for provider_type, providers in entries.items():
        provider = first(providers)
        if provider is not None:
            res[provider_type] = provider
    return res


def present_providers(lot_id: int) -> Dict[ProviderType, ProviderView]:
    # TODO: many-to-many relation configured wrong. Change models and this code
    try:
        parking_lots = ProviderParkingLot.objects.filter(parking_lot=lot_id)
    except ProviderParkingLot.DoesNotExist:
        return {}

    providers_by_types = {}

    for parking_lot in parking_lots:
        provider_type = parking_lot.provider_type
        providers = parking_lot.providers.all()

        providers_by_types[provider_type] = [
            present_provider(provider) for provider in providers
        ]

    return get_first_provider(providers_by_types)


def present_station(lot: ParkingLot) -> StationView:
    lot_camera = Camera.objects.filter(lot=lot, space=None).first()
    lot_img = (
        resolve_media_url(
            '{!s}?t={}'.format(
                lot_camera.image,
                time.mktime(lot_camera.last_image_update.timetuple()),
            ),
        )
        if lot_camera
        else ''
    )
    return StationView(
        id=lot.id,
        name=lot.name,
        img=lot_img,
        img_map=resolve_media_url(lot.map_image),
        img_cam=lot_img,
        loc=present_location(lot),
        address=lot.address,
        show=False,
        spaces=[present_space(space) for space in lot.spaces.all()],
        providers=present_providers(lot.id),
    )


def present_city(city: City) -> CityView:
    return CityView(
        name=city.name,
        station=[present_station(lot) for lot in city.lots.all()],
    )


def present_refills_typed() -> RefillsView:
    return RefillsView(data=[present_city(city) for city in City.objects.all()])


def present_refills():
    return present_refills_typed().dict()['data']
