# TODO: rename module and move this functions to a utilities modules
import time
from datetime import datetime
from typing import Optional

from django.conf import settings


def datetime_as_ms(dt: datetime) -> Optional[int]:
    return int(time.mktime(dt.timetuple()) * 1000) if dt else None


def resolve_media_url(media: Optional[str]):
    return '/'.join(
        part.strip('/')
        for part in (
            settings.HOST,
            settings.MEDIA_URL,
            str(media),
        )
    )
