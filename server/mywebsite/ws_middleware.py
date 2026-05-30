from threading import Thread
from typing import List, Optional, Tuple

import structlog
from django.conf import settings
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

logger = structlog.get_logger(__name__)


def get_client():
    return InfluxDBClient(
        url=settings.INFLUXDB_V2_URL,
        token=settings.INFLUXDB_V2_TOKEN,
        org=settings.INFLUXDB_V2_ORG,
    )


def headers_as_dict(raw_headers: Optional[List[Tuple[str, str]]]):
    res = {}
    for key, value in raw_headers:
        res[key.decode('latin1')] = value.decode('latin1')
    return res


def process_points(client: InfluxDBClient, points):
    bucket = settings.INFLUXDB_MIDDLEWARE_BUCKET
    try:
        logger.debug('Send metrics to influxdb', data=points)
        api = client.write_api(write_options=SYNCHRONOUS)
        points = [Point.from_dict(point) for point in points]
        api.write(
            bucket=bucket,
            record=points,
        )
    except Exception:
        logger.exception(
            'Failed to write influxdb points',
            influx_url=client.url,
            bucket=bucket,
            org=client.org,
            data=points,
        )


def write_points(points):
    client = get_client()
    thread = Thread(target=process_points, args=(client, points))
    thread.start()


def send_metrics(headers):
    if getattr(settings, 'INFLUXDB_MIDDLEWARE_DISABLED', True):
        logger.debug('STATS disabled')
        return

    points = [
        {
            'measurement': 'ws_connection',
            'tags': {
                'req_host': headers.get('host'),
                'user_agent': headers.get('user-agent'),
                'client_ip': headers.get('x-forwarded-for'),
                'host': settings.HOST,
            },
            'fields': {
                'value': 1,
            },
        },
    ]

    try:
        write_points(points)
    except Exception:
        logger.exception('Failed to write websocket metrics')


class WSMetricsMiddleware:
    def __init__(self, inner) -> None:
        self.inner = inner

    async def __call__(self, scope, receive, send):
        headers = headers_as_dict(scope.get('headers'))
        logger.info(
            'WS_CONNECT',
            headers=headers,
            client=scope.get('client'),
        )

        send_metrics(headers)

        return await self.inner(scope, receive, send)
