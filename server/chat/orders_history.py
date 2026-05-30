import time
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

import structlog
from django.contrib.auth.models import User
from django.db import models
from django.db.models.functions import Coalesce, Now
from pydantic import BaseModel

from chat.influx_client import get_client
from main.models import Order

BUCKET = 'rasp-pi'

logger = structlog.stdlib.get_logger(__name__)
influx_client = get_client()
query_api = influx_client.query_api()


def _format_db_time(db_time: Optional[datetime]):
    if db_time is not None:
        return int(time.mktime(db_time.timetuple()))
    return None


def _format_influx_time(db_time: datetime):
    return db_time.strftime('%Y-%m-%dT%H:%M:%SZ')


def present_chart(user: User, order_uuid: str, limit: int = 18000):
    order = (
        user.orders.annotate(
            last_time=Coalesce('finished_at', Now()),
        )
        .filter(uuid=order_uuid)
        .first()
    )
    if order is None:
        # order is not found or this orders is not user's
        return None
    rows = (
        order.space.stats.filter(
            models.Q(created_at__gte=order.created_at)
            & models.Q(created_at__lte=order.last_time),
        )
        .order_by('-created_at')
        .only('created_at', 'current_a')
    )
    dataset = {
        'order_uuid': order_uuid,
        'labels': [],
        'current_a': [],
    }
    for row in rows[:limit]:
        dataset['labels'].append(_format_db_time(row.created_at))
        dataset['current_a'].append(row.current_a)

    return dataset


def _query_curent_a(start: str, stop: str, host: str, bucket: str = BUCKET):
    query_text = f"""from(bucket: "{bucket}")
      |> range(start: {start}, stop: {stop})
      |> filter(fn: (r) => r["_measurement"] == "station_state")
      |> filter(fn: (r) => r["_field"] == "current_a")
      |> filter(fn: (r) => r["host"] == "{host}")
      |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
      |> yield(name: "mean")"""

    dataset = {
        'labels': [],
        'current_a': [],
    }
    try:
        tables = query_api.query(query_text)
    except Exception:
        logger.exception('Failed to get data from influx')
        return dataset

    if len(tables) != 1:
        return dataset

    for row in tables[0]:
        dataset['labels'].append(_format_db_time(row.values['_time']))
        dataset['current_a'].append(row.values['_value'])

    return dataset


def present_chart_influx(user: User, order_uuid: str):
    order = (
        user.orders.annotate(
            last_time=Coalesce('finished_at', Now()),
        )
        .filter(uuid=order_uuid)
        .first()
    )
    if order is None:
        # order is not found or this orders is not user's
        return None
    start = _format_influx_time(order.created_at)
    stop = _format_influx_time(order.last_time)
    # TODO: put device id to the influx tags in the stations telegraph.conf?
    host = f'rasp4{order.space.name}'

    dataset = _query_curent_a(start, stop, host)
    dataset['order_uuid'] = order_uuid
    return dataset


class SpaceView(BaseModel):
    id: int
    name: str


class LotView(BaseModel):
    id: int
    name: str
    city: str


# TODO: use chat.presenters.order.OrderView instead???
class OrderHistoryView(BaseModel):
    uuid: str
    space: SpaceView
    lot: LotView
    connector_type: str
    created_at: int
    finished_at: Optional[int]
    cost_total: str  # Общая стоимость сессии. decimal XXX.YY
    cost_kw: str  # decimal XXX.YY
    cost_idle: str  # decimal XXX.YY
    cost_booking: str  # decimal XXX.YY
    kw: str  # Потреблено кВт за время сессии
    duration: int  # длителность в секундах с начала эпохи
    payed_seconds: int  # длительность платного время за простой
    status: str


class OrdersHistory(BaseModel):
    data: List[OrderHistoryView]


def present_order_history(order: Order) -> OrderHistoryView:
    delta_kw = Decimal(0)
    if order.end_kw is not None:
        delta_kw = order.end_kw - order.start_kw

    return OrderHistoryView(
        uuid=str(order.uuid),
        space=SpaceView(
            id=order.space.id,
            name=order.space.name,
        ),
        lot=LotView(
            id=order.space.lot.id,
            name=order.space.lot.name,
            city=order.space.lot.city.name,
        ),
        connector_type=order.connector_type.connector_type,
        created_at=_format_db_time(order.created_at),
        finished_at=_format_db_time(order.finished_at),
        cost_total=str(order.cost_total_with_booking),
        cost_kw=str(order.cost_kw),
        cost_idle=str(order.cost_without_kw),
        cost_booking=str(order.cost_booking),
        kw=str(delta_kw),
        duration=order.duration,
        payed_seconds=int(order.payed_seconds),
        status=order.status,
    )


def present_history(user: User):
    query = user.orders.order_by('-created_at')
    orders = query.all()
    return OrdersHistory(data=[present_order_history(order) for order in orders])
