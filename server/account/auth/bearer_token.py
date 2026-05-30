from contextlib import suppress

import structlog
from ninja.security import HttpBearer

from account.models import Token
from main.models.device import Device

logger = structlog.get_logger(__name__)


class AuthBearerUser(HttpBearer):
    def authenticate(self, request, token: str):
        with suppress(Token.DoesNotExist):
            token_obj = Token.objects.select_related(
                'user',
            ).get(key=token, is_active=True)
            if token_obj.user.is_active:
                return token_obj.user
            return None


class AuthBearerDevice(HttpBearer):
    def authenticate(self, request, token: str):
        with suppress(Device.DoesNotExist):
            return Device.objects.get(key=token)
