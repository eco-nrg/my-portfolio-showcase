from typing import Union

from django.contrib.auth.models import User

from chat.event.helpers import send_to
from chat.no_error import no_error
from chat.presenters.refill import present_refills
from main.models.city import City
from main.models.parking_lot import ParkingLot


@no_error
def send_refills(target: Union[str, User]):
    msg = {
        'type': 'refill_response',
        'data': present_refills(),
    }
    send_to(target, msg)


@no_error
def send_map(target: Union[str, User]):
    # берем первый город в БД. Этот город считается default-city
    # его координа считаются координатами карты по-умолчанию
    # если города нет, то вообще и карта не может работать
    city = City.objects.order_by('pk').first()
    if city is not None:
        coords = city.location if city.location is not None else [0, 0]
        zoom = city.map_zoom if city.map_zoom is not None else 15
    else:
        coords = (0, 0)
        zoom = 15

    resp = {
        'config': {
            'coords': coords,
            'zoom': zoom,
            'iconImageSize': [30, 50],
        },
    }

    items = []
    for lot in ParkingLot.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False,
    ):
        if lot.latitude and lot.longitude:
            coord = [
                float(lot.latitude),
                float(lot.longitude),
            ]
        else:
            coord = []

        spaces = []

        for space in lot.spaces.all():
            connectors = []

            for connector in space.connectors.all():
                connectors.append(
                    {
                        'type': connector.connector_type,
                        'phases_count': connector.phases_count,
                        'current_a': float(connector.max_a),
                        'power_kw': float(connector.max_kw),
                    },
                )
            spaces.append(
                {
                    'id': space.id,
                    'status': space.status,
                    'connectors': connectors,
                },
            )

        items.append(
            {
                'index': lot.id,
                'name': lot.name,
                'address': lot.address,
                'coord': coord,
                'zoom': lot.zoom,
                'spaces': spaces,
            },
        )

        resp['markers'] = items

    msg = {
        'type': 'map_response',
        'data': resp,
    }
    send_to(target, msg)
