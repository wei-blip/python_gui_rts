import mcu_telemetry

from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread


class McuTelemetryWindow(QtWidgets.QMainWindow, mcu_telemetry.Ui_McuTelemetry, QtWidgets.QMessageBox):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

        # Callback begin
        self.getMcuTelemetry.clicked.connect(self.get_mcu_telemetry)
        # Callback end

    def get_mcu_telemetry(self):
        # Send mcu_telemetry_req message
        return 0
