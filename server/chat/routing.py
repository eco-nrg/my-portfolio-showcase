from django.urls import re_path

from chat.consumers import ChatConsumer

websocket_urlpatterns = [
    re_path('ws/socket-server/', ChatConsumer.as_asgi()),
]
