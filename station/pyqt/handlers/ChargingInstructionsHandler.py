from typing import Optional
from pyqt.handlers.Handler import Handler
from pyqt.config import connector_image_mapping


class ChargingInstructionsHandler(Handler):
    def __init__(self, parent_self):
        self.parent_self = parent_self
        self.connector_type: Optional[str] = None

    def handle(self):
        state_manager = self.parent_self.state_manager
        status = self.parent_self.status
        if (self.connector_type != status.chargingStation):
            self.connector_type = status.chargingStation
            state_manager.chargingStation = connector_image_mapping.get(
                status.chargingStation, state_manager.chargingStation
            )
