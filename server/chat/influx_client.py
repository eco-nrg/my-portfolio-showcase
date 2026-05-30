from django.conf import settings
from influxdb_client import InfluxDBClient


def get_client():
    return InfluxDBClient(
        url=settings.INFLUXDB_V2_URL,
        token=settings.INFLUXDB_V2_TOKEN,
        org=settings.INFLUXDB_V2_ORG,
    )
