import msg_window

from PyQt5 import QtWidgets
from enum import IntEnum
import cobs_proto_terminal
from PyQt5.QtCore import QThread


class TabIndex(IntEnum):
    DEV_INFO = 0
    MCU_TELEMETRY = 1
    JOIN_KEY = 2
    DS18B20 = 3
    ADXL345 = 4
    REBOOT = 5
    CW_MODE = 6


class MsgWindow(QtWidgets.QMainWindow, msg_window.Ui_MsgWindow, QtWidgets.QMessageBox):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.ser_port = 0
        self.isOpen = False
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

        # Settings begin
        enum_arr = ["CW command enumeration", "CW_ON", "CW_OFF", "CW_FORM_START", "CW_FORM_FINISH"]
        self.fill_combo_box(enum_arr)  # fill cw_cmd
        self.disable_all_tabs()
        # Settings end

        # Callback begin
        self.getDevInfo.clicked.connect(self.get_dev_info)
        self.getMcuTelemetry.clicked.connect(self.get_mcu_telemetry)
        self.getJoinKey.clicked.connect(self.get_join_key)
        self.getAdxl345.clicked.connect(self.get_adxl345)
        self.getDs18b20.clicked.connect(self.get_ds18b20)
        self.rebootDevice.clicked.connect(self.reboot_dev)
        self.setCwMode.clicked.connect(self.set_cw_mode)
        # Callback end

    def get_dev_info(self):
        print("My message")
        cobs_proto_terminal.something(self.ser_port)
        # Send devinfo message
        return 0

    def get_mcu_telemetry(self):
        # Send mcu_telemetry message
        return 0

    def get_join_key(self):
        # Send join_key message
        return 0

    def get_adxl345(self):
        # Send adxl345 message
        return 0

    def get_ds18b20(self):
        # Send ds18b20 message
        return 0

    def set_cw_mode(self):
        # Set device in cw mode message
        return 0

    def reboot_dev(self):
        # Reboot device
        return 0

    def fill_combo_box(self, arr):
        for i in arr:
            self.cw_cmd.addItem(str(i))
            print(i)

    def disable_all_tabs(self):
        self.tabMessage.setTabEnabled(int(TabIndex.DEV_INFO), False)
        self.tabMessage.setTabEnabled(int(TabIndex.MCU_TELEMETRY), False)
        self.tabMessage.setTabEnabled(int(TabIndex.JOIN_KEY), False)
        self.tabMessage.setTabEnabled(int(TabIndex.DS18B20), False)
        self.tabMessage.setTabEnabled(int(TabIndex.ADXL345), False)
        self.tabMessage.setTabEnabled(int(TabIndex.REBOOT), False)
        self.tabMessage.setTabEnabled(int(TabIndex.CW_MODE), False)

    def closeEvent(self, event):
        self.isOpen = False
        self.disable_all_tabs()
        event.accept()

    def enable_tab(self, index):
        self.tabMessage.setTabEnabled(int(index), True)
