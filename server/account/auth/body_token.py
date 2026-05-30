from contextlib import suppress
from typing import Optional

import simplejson
import structlog
from django.http import HttpRequest
from ninja.security.apikey import APIKeyBase

from main.models.device import Device

logger = structlog.get_logger(__name__)


class APIKeyBody(APIKeyBase):
    openapi_in: str = 'body'

    def _get_key(self, request: HttpRequest) -> Optional[str]:
        try:
            body = simplejson.loads(request.body)
        except simplejson.JSONDecodeError:
            logger.debug('Failed to parse json from request.body')
            return None
        return body.get(self.param_name)


class AuthBodyTokenDevice(APIKeyBody):
    param_name = 'token'

    def authenticate(self, request, token):
        if token is not None:
            return None
        with suppress(Device.DoesNotExist):
            return Device.objects.get(key=token)
