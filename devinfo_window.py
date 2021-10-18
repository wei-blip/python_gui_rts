import devinfo

from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread


class DevInfoWindow(QtWidgets.QMainWindow, devinfo.Ui_DevInfo, QtWidgets.QMessageBox):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

        # Callback begin
        self.getDevInfo.clicked.connect(self.get_dev_info)
        # Callback end

    def get_dev_info(self):
        # Send devinfo message
        return 0
