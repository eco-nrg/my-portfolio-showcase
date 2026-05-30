"""
ASGI config for mywebsite project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from mywebsite.ws_middleware import WSMetricsMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mywebsite.settings')
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# must be called after get_asgi_application() because it setups django ORM
import chat.routing  # NOQA

application = ProtocolTypeRouter(
    {
        'http': django_asgi_app,
        'websocket': AuthMiddlewareStack(
            WSMetricsMiddleware(
                URLRouter(chat.routing.websocket_urlpatterns),
            ),
        ),
    },
)
