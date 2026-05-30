from typing import Optional
from py_scripts.constants import (
    PROPERTY_SPACE_PRICE_IDLE,
    PROPERTY_SPACE_PRICE_KWH,
    PROPERTY_SPACE_MODE,
    SPACE_MODES
)
from pyqt.handlers.Handler import Handler
from pyqt.config import color_qr_code, generate_qr, is_generate_qr, path_qr_code
from pyqt.config import connector_image_mapping, connector_name_mapping

from kv.redis_kv import models


class QrCodeActivateHandler(Handler):
    def __init__(self, parent_self):
        self.parent_self = parent_self
        self.connector_type: Optional[str] = None

    def handle(self):
        state_manager = self.parent_self.state_manager
        status = self.parent_self.status

        new_state = status.response
        if is_generate_qr(new_state, status.url):
            generate_qr(color=color_qr_code.get(new_state),
                        url=status.url,
                        path=path_qr_code.get(new_state))

        if (self.connector_type != status.chargingStation):
            self.connector_type = status.chargingStation
            state_manager.chargingStation = connector_image_mapping.get(
                status.chargingStation, state_manager.chargingStation
            )
            state_manager.nameConnector = connector_name_mapping.get(
                status.chargingStation, state_manager.nameConnector
            )

        space_mode = models.get_prop_value(PROPERTY_SPACE_MODE,
                                           SPACE_MODES.TEST)

        if space_mode == SPACE_MODES.TEST:
            state_manager.price_kwh = '0'
            state_manager.price_idle = '0'
        elif space_mode == SPACE_MODES.PRODUCTION:
            price_kwh = models.get_prop_value(PROPERTY_SPACE_PRICE_KWH, '0')
            if state_manager.price_kwh != price_kwh:
                state_manager.price_kwh = price_kwh

            price_idle = models.get_prop_value(PROPERTY_SPACE_PRICE_IDLE, '0')
            if state_manager.price_idle != price_idle:
                state_manager.price_idle = price_idle
        else:
            state_manager.price_kwh = '0'
            state_manager.price_idle = '0'
