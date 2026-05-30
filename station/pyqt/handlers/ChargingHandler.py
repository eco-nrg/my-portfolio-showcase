from py_scripts.status_model import Status
from pyqt.handlers.Handler import Handler
from pyqt.config import color_qr_code, generate_qr, is_generate_qr, path_qr_code
from pyqt.state_manager.StateManager import StateManager
from datetime import datetime

class ChargingHandler(Handler):
    def __init__(self, parent_self):
        self.parent_self = parent_self

    def handle(self):
        status = self.parent_self.status
        state_manager = self.parent_self.state_manager
        
        new_state = status.response

        if is_generate_qr(new_state, status.url):
            generate_qr(color=color_qr_code.get(new_state),
                        url=status.url, path=path_qr_code.get(new_state))
        
        state_manager.leftTime = self.calc_time(status=status)
        state_manager.currentAm = status.am
        state_manager.totalKwh = status.total_kwh
        state_manager.currentKwh = status.current_kwh
        
        if (state_manager.prefixNumber != self.get_prefix_number(status.am)):
            state_manager.prefixNumber = self.get_prefix_number(status.am)
    
    def calc_time(self, status: Status):
        start_payed = status.start_payed
        current_time_milliseconds = int(datetime.utcnow().timestamp() * 1000)
        if start_payed is None:
            if (
                status.created_at is None or
                status.freeTime is None
            ):
                return 0
            created_at = int(status.created_at)
            free_time = int(status.freeTime)
            duration = current_time_milliseconds - created_at
            result = int(free_time - duration / 1000)
            return result
        else:
            result = int((current_time_milliseconds - int(start_payed)) / 1000)
            return result

    def get_prefix_number(self, am):
        value = int(float(am))
        if 0 <= value <= 10:
            return "0-10"
        elif 10 < value <= 25:
            return "10-25"
        elif 25 < value <= 30:
            return "25-30"
        elif 30 < value <= 35:
            return "30-35"
        else:
            return "35-40"