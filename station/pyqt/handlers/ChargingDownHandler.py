from pyqt.handlers.Handler import Handler


class ChargingDownHandler(Handler):
    def __init__(self, parent_self):
        self.parent_self = parent_self

    def handle(self):
        state_manager = self.parent_self.state_manager
        chargingDownImgPrefix = int(state_manager.chargingDownImgPrefix)
        
        chargingDownImgPrefix = (chargingDownImgPrefix % 6) + 1
        state_manager.chargingDownImgPrefix = str(chargingDownImgPrefix)

