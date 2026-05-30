from pyqt.handlers.Handler import Handler
from pyqt.config import color_qr_code, generate_qr, human_delta, is_generate_qr, path_qr_code
from datetime import datetime, timezone
from py_scripts.custom_logger import logger


class BookedHander(Handler):
    def __init__(self, parent_self):
        self.parent_self = parent_self

    def handle(self):
        status = self.parent_self.status
        state_manager = self.parent_self.state_manager

        new_state = status.response
        if is_generate_qr(new_state, status.url):
            generate_qr(color=color_qr_code.get(new_state),
                        url=status.url, path=path_qr_code.get(new_state))

        if status.booked_until is not None:
            bookedRemainingTime = int(
                status.booked_until - int(datetime.now(timezone.utc).timestamp())
            )
            state_manager.bookedRemainingTime = human_delta(bookedRemainingTime or 0)
        else:
            state_manager.bookedRemainingTime = ""
