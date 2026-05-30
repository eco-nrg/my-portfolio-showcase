import sys
from PyQt5.QtCore import Qt, QTimer, QObject, pyqtProperty, pyqtSignal, pyqtSlot
from PyQt5.QtQml import QQmlApplicationEngine, QQmlProperty
from PyQt5.QtGui import QGuiApplication, QPixmap
from kv.redis_kv import models
from pyqt.config import human_delta
from datetime import datetime


class StateManager(QObject):
    # main.qml
    stateChanged = pyqtSignal()

    # BookedPage.qml
    bookedRemainingTimeChanged = pyqtSignal()

    # CustomValueBox.qml
    leftTimeChange = pyqtSignal()
    totalKwhChange = pyqtSignal()
    currentAmChange = pyqtSignal()
    currentKwhChange = pyqtSignal()
    prefixNumberChange = pyqtSignal()

    # ActivationPage.qml
    # ChargingInstructionPage.qml
    chargingStationChange = pyqtSignal()
    nameConnectorChange = pyqtSignal()
    price_kwh_change = pyqtSignal()
    price_idle_change = pyqtSignal()

    # ChargingDownPage.qml
    chargingDownImgPrefixChange = pyqtSignal()

    # ChargingEndPage.qml
    chargingEndImgPrefixChange = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._currentState = models.STATE_SYSTEM_START

        self._bookedRemainingTime = ""

        self._leftTime: int = 0
        self._currentAm: float = 0
        self._totalKwh: float = 0
        self._currentKwh: float = 0
        self._prefixNumber = "0-10"

        self._chargingStation = ""
        self._nameConnector = ""
        self._price_kwh: str = ""
        self._price_idle: str = ""

        self._chargingDownImgPrefix = "1"

        self._chargingEndImgPrefix = "1"

    @pyqtProperty(str, notify=stateChanged)
    def currentState(self):
        return self._currentState

    @currentState.setter
    def currentState(self, state):
        if self._currentState != state:
            self._currentState = state
            self.stateChanged.emit()

    @pyqtProperty(str, notify=bookedRemainingTimeChanged)
    def bookedRemainingTime(self):
        return self._bookedRemainingTime

    @bookedRemainingTime.setter
    def bookedRemainingTime(self, newTime):
        self._bookedRemainingTime = newTime
        self.bookedRemainingTimeChanged.emit()

    @pyqtProperty(str, notify=leftTimeChange)
    def leftTime(self):
        return human_delta(self._leftTime or 0)

    @leftTime.setter
    def leftTime(self, value):
        self._leftTime = value
        self.leftTimeChange.emit()

    @pyqtProperty(str, notify=totalKwhChange)
    def totalKwh(self):
        return '{0:.2f}'.format(self._totalKwh or 0)

    @totalKwh.setter
    def totalKwh(self, value):
        self._totalKwh = value
        self.totalKwhChange.emit()

    @pyqtProperty(str, notify=currentAmChange)
    def currentAm(self):
        return '{0:.2f}'.format(self._currentAm or 0)

    @currentAm.setter
    def currentAm(self, value):
        self._currentAm = value
        self.currentAmChange.emit()

    @pyqtProperty(str, notify=currentKwhChange)
    def currentKwh(self):
        return '{0:.2f}'.format(self._currentKwh or 0)

    @currentKwh.setter
    def currentKwh(self, value):
        self._currentKwh = value
        self.currentKwhChange.emit()

    @pyqtProperty(str, notify=prefixNumberChange)
    def prefixNumber(self):
        return self._prefixNumber

    @prefixNumber.setter
    def prefixNumber(self, value):
        self._prefixNumber = value
        self.prefixNumberChange.emit()

    @pyqtProperty(str, notify=chargingStationChange)
    def chargingStation(self):
        return self._chargingStation

    @chargingStation.setter
    def chargingStation(self, value):
        self._chargingStation = value
        self.chargingStationChange.emit()

    @pyqtProperty(str, notify=nameConnectorChange)
    def nameConnector(self):
        return self._nameConnector

    @nameConnector.setter
    def nameConnector(self, value):
        self._nameConnector = value
        self.nameConnectorChange.emit()

    @pyqtProperty(str, notify=price_kwh_change)
    def price_kwh(self):
        return self._price_kwh

    @price_kwh.setter
    def price_kwh(self, value):
        self._price_kwh = value
        self.price_kwh_change.emit()

    @pyqtProperty(str, notify=price_idle_change)
    def price_idle(self):
        return self._price_idle

    @price_idle.setter
    def price_idle(self, value):
        self._price_idle = value
        self.price_idle_change.emit()

    @pyqtProperty(str, notify=chargingDownImgPrefixChange)
    def chargingDownImgPrefix(self):
        return self._chargingDownImgPrefix

    @chargingDownImgPrefix.setter
    def chargingDownImgPrefix(self, value):
        self._chargingDownImgPrefix = value
        self.chargingDownImgPrefixChange.emit()

    @pyqtProperty(str, notify=chargingEndImgPrefixChange)
    def chargingEndImgPrefix(self):
        return self._chargingEndImgPrefix

    @chargingEndImgPrefix.setter
    def chargingEndImgPrefix(self, value):
        self._chargingEndImgPrefix = value
        self.chargingEndImgPrefixChange.emit()
