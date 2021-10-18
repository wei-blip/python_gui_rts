import join_key

from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread


class JoinKeyWindow(QtWidgets.QMainWindow, join_key.Ui_JoinKey, QtWidgets.QMessageBox):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

        # Callback begin
        self.getJoinKey.clicked.connect(self.get_join_key)
        # Callback end

        # Values begin
        self.values = 0;
        # Values end


    def get_join_key(self):
        # Send mcu_telemetry_req message
        return 0

    def get_fields_value(self):
        return 0
