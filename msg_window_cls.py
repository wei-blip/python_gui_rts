import msg_window

from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread


class MsgWindow(QtWidgets.QMainWindow, msg_window.Ui_MsgWindow, QtWidgets.QMessageBox):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

        # Callback begin
        self.getDevInfo.clicked.connect(self.get_dev_info)
        self.getMcuTelemetry.cliced.connect(self.get_mcu_telemetry)
        self.getJoinKey.clicked.connect(self.get_join_key)
        # Callback end

    def get_dev_info(self):
        # Send devinfo message
        return 0

    def get_mcu_telemetry(self):
        return 0

    def  get_join_key(self):
        return 0