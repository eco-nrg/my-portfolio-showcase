from typing import Union

import structlog
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.models import User

logger = structlog.get_logger(__name__)


def send_to(target: Union[str, User], msg):
    if target == 'all':
        send_to_all(msg)
    elif isinstance(target, str):
        send_to_channel(target, msg)
    elif isinstance(target, User):
        send_to_user(target, msg)
    else:
        logger.warn('Unknown send target', target=target)


def send_to_channel(channel_name: str, msg):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.send)(channel_name, msg)


def send_to_user(user: User, msg):
    channel_layer = get_channel_layer()
    for connection in user.connections.all():
        async_to_sync(channel_layer.send)(connection.channel_name, msg)


def send_to_all(msg):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)('all', msg)
