import structlog
from django.utils import timezone

from chat.event.helpers import send_to_all
from chat.presenters.helpers import datetime_as_ms

logger = structlog.getLogger(__name__)


def ping_ws_client():
    now = datetime_as_ms(timezone.now())
    logger.debug('PING clients', now=now)
    send_to_all(
        {
            'type': 'ping_response',
            'data': now,
        },
    )
