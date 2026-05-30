from pyqt.handlers.Handler import Handler


class ChargingEndHandler(Handler):
    def __init__(self, parent_self):
        self.parent_self = parent_self

    def handle(self):
        state_manager = self.parent_self.state_manager
        chargingEndImgPrefix = int(state_manager.chargingEndImgPrefix)
        
        chargingEndImgPrefix = (chargingEndImgPrefix % 1) + 1
        state_manager.chargingEndImgPrefix = str(chargingEndImgPrefix)

