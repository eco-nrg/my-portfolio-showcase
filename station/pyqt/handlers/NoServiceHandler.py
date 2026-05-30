from py_scripts.status_model import Status
from pyqt.handlers.Handler import Handler
from pyqt.state_manager.StateManager import StateManager
from datetime import datetime

class NoServiceHandler(Handler):
    def __init__(self, parent_self):
        self.parent_self = parent_self

    def handle(self):
        pass