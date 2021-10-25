import time
import queue

from json_protobuf_proto import JSONProtobufProto
from enum import IntEnum
from rs_0006_0_icp_pb2 import *
from cobs import cobs
from PyQt5 import QtWidgets
from msg_window import Ui_MsgWindow
from MyThreads import ReaderSocketThread

q = queue.Queue()


class TabIndex(IntEnum):
    DEV_INFO = 0
    MCU_TELEMETRY = 1
    JOIN_KEY = 2
    DS18B20 = 3
    ADXL345 = 4
    REBOOT = 5
    CW_MODE = 6


class MsgWindow(QtWidgets.QMainWindow, Ui_MsgWindow, QtWidgets.QMessageBox, JSONProtobufProto):
    def __init__(self, queue_time, sock):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

        # Attributes begin
        self.transport = sock
        self.in_msg = exch()
        self.current_msg = 0
        self.isOpen = False
        self.thread = 0
        self.queue_time = queue_time
        self.reader_thread = ReaderSocketThread(self)
        # self.recv_thread = ReceivingThread(self)
        # Attributes end

        # Settings begin
        # fill cw_cmd
        self.fill_combo_box(["CW command", "CW_ON", "CW_OFF", "CW_FORM_START", "CW_FORM_FINISH"])
        self.disable_all_tabs()
        self.reader_thread.start()
        # self.recv_thread.start()
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

    # Send devinfo message begin
    def get_dev_info(self):
        msg = '{"req":{"devinfo":{}}}'
        self.current_msg = 'devinfo'
        self.queue_time.put_nowait("Message devinfo is send " + self.get_time())
        self.send_msg(msg)
        # self.getDevInfo.setEnabled(False)
        return 0

    # Send devinfo message end

    def get_mcu_telemetry(self):
        pass
        # Send mcu_telemetry message
        return 0

    def get_join_key(self):
        pass
        # Send join_key message
        return 0

    def get_adxl345(self):
        pass
        # Send adxl345 message
        return 0

    def get_ds18b20(self):
        msg = '{"req":{"ds18b20":{}}}'
        self.current_msg = 'ds18b20'
        self.send_msg(msg)
        self.queue_time.put_nowait("Message ds18b20 is send " + self.get_time())
        self.getDs18b20.setEnabled(False)
        # Send ds18b20 message
        return 0

    def set_cw_mode(self):
        # Set device in cw mode message
        cmd = self.cw_cmd.currentText()  # get cw command
        freq = str(self.freq.value())  # get frequency value
        pwr = str(self.pwr_dbm.value())  # get power value
        dur = str(self.duration.value())  # get duration value
        msg = '{"req":{""}'
        return 0

    # Reboot device begin
    def reboot_dev(self):
        if self.swap.isChecked():
            msg = '{"req":{"reboot":{"swap": true}}}'
        else:
            msg = '{"req":{"reboot":{"swap": false}}}'
        self.current_msg = 'reboot_dev'
        self.send_msg(msg)
        self.queue_time.put_nowait("Message reboot is send " + self.get_time())
        self.rebootDevice.setEnabled(False)
        return 0

    # Reboot device end

    # Fill combo box begin
    def fill_combo_box(self, arr):
        for i in arr:
            self.cw_cmd.addItem(str(i))
            print(i)

    # Fill combo box end

    # Disable all tabs begin
    def disable_all_tabs(self):
        self.tabMessage.setTabEnabled(int(TabIndex.DEV_INFO), False)
        self.tabMessage.setTabEnabled(int(TabIndex.MCU_TELEMETRY), False)
        self.tabMessage.setTabEnabled(int(TabIndex.JOIN_KEY), False)
        self.tabMessage.setTabEnabled(int(TabIndex.DS18B20), False)
        self.tabMessage.setTabEnabled(int(TabIndex.ADXL345), False)
        self.tabMessage.setTabEnabled(int(TabIndex.REBOOT), False)
        self.tabMessage.setTabEnabled(int(TabIndex.CW_MODE), False)

    # Disable all tabs end

    # Close event begin
    def closeEvent(self, event):
        self.isOpen = False
        self.disable_all_tabs()
        event.accept()

    # Close event end

    # Enable tab begin
    def enable_tab(self, index):
        self.tabMessage.setTabEnabled(int(index), True)

    # Enable tab end

    # Send message begin
    def send_msg(self, data):
        self.write_msg_json(data, exch())
    # Send message end

    # Get time begin
    def get_time(self):
        t = time.localtime()  # get current time
        return str(t[2]) + ":" + str(t[1]) + ":" + str(t[0]) + " " + str(t[3]) + ":" + str(t[4]) + ":" + str(t[5])
    # Get time end
