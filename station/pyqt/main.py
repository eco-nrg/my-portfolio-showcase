import sys
from PyQt5.QtCore import Qt, QTimer, QObject, pyqtProperty, pyqtSignal, pyqtSlot
from PyQt5.QtQml import QQmlApplicationEngine, QQmlProperty
from PyQt5.QtGui import QGuiApplication, QPixmap
import qrcode

from PIL import Image
from typing import Dict
from kv.redis_kv import models

from py_scripts.custom_logger import logger
from py_scripts.status import get_status
from py_scripts.status_model import Status
from py_scripts.custom_logger import logger
import time
from typing import Callable, Dict
from pyqt.handlers.BookedHander import BookedHander
from pyqt.handlers.ChargingDownHandler import ChargingDownHandler
from pyqt.handlers.ChargingEndHandler import ChargingEndHandler

from pyqt.handlers.ChargingHandler import ChargingHandler
from pyqt.handlers.ChargingInstructionsHandler import ChargingInstructionsHandler
from pyqt.handlers.Handler import Handler
from pyqt.config import color_qr_code, is_generate_qr, path_qr_code, MAX_RETRIES, url_qr_code, generate_qr
from pyqt.handlers.NoServiceHandler import NoServiceHandler
from pyqt.handlers.QrCodeActivateHandler import QrCodeActivateHandler
from pyqt.state_manager.StateManager import StateManager



def get_current_status() -> Status:
    retry_count = 0
    while retry_count < MAX_RETRIES:
        try:
            data = get_status()
            if data is not None:
                logger.debug('Status: ', data=data.json())
                return data
            else:
                retry_count += 1
        except KeyboardInterrupt:
            raise
        except Exception:
            logger.exception('Can not get values')
            time.sleep(1)
        retry_count += 1
        logger.info(
            "Retrying... (Attempt {%d}/{%d})",
            retry_count,
            MAX_RETRIES,
        )
    if retry_count == MAX_RETRIES:
        logger.error("Max retries exceeded. Could get value by key.")
        return None



class App:
    def __init__(self):
        self.app = QGuiApplication(sys.argv)
        self.app.setOverrideCursor(Qt.BlankCursor)
        self.engine = QQmlApplicationEngine()
        self.context = self.engine.rootContext()

        self.state_manager = StateManager()
        self.status = get_current_status()
        self.context.setContextProperty("stateManager", self.state_manager)

        self.handle_state_function_map: Dict[str, Handler] = {
            models.STATE_IDLE: QrCodeActivateHandler(parent_self=self),
            models.STATE_WARNING: NoServiceHandler(parent_self=self),
            models.STATE_BOOKED: BookedHander(parent_self=self),
            models.STATE_CHARGING: ChargingInstructionsHandler(parent_self=self),
            models.STATE_CHARGING_START: ChargingHandler(parent_self=self),
            models.STATE_CHARGING_DOWN: ChargingDownHandler(parent_self=self),
            models.STATE_CHARGING_END: ChargingEndHandler(parent_self=self),
        }
        

        qml_file = "pyqt/main.qml"
        self.engine.load(qml_file)

        if not self.engine.rootObjects():
            sys.exit(-1)

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_and_update_state)
        self.timer.start(2000)

    def check_and_update_state(self):
        self.status = get_current_status()
        self.new_state = self.status.response
        hander = self.handle_state_function_map.get(self.new_state)
        if hander:
            hander.handle()
            if self.state_manager.currentState != self.new_state:
                if self.new_state == models.STATE_CHARGING_DOWN:
                    self.state_manager._chargingDownImgPrefix = "1"
                self.state_manager.currentState = self.new_state

        else:
            logger.exception('No handler for state:', current_state = self.new_state)
            self.state_manager.currentState = models.STATE_WARNING

    def run(self):
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    app = App()
    app.run()
