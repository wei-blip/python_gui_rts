import json
import time

import msg_window
import serial, serial.tools.list_ports, serial.threaded
import queue

from PyQt5 import QtWidgets
from enum import IntEnum
from rs_0006_0_icp_pb2 import *
from serial_cobs_proto import ProtoCOBS, ProtoCOBSJSON
from cobs import cobs
from PyQt5.QtCore import QThread

q = queue.Queue()


class TabIndex(IntEnum):
    DEV_INFO = 0
    MCU_TELEMETRY = 1
    JOIN_KEY = 2
    DS18B20 = 3
    ADXL345 = 4
    REBOOT = 5
    CW_MODE = 6


def print_hex(data, fid=sys.stdout):
    for i in range(0, len(data)):
        print('%02X' % data[i], end=' ', file=fid)
    print('', file=fid)


class ReceivingThread(QThread):
    def __init__(self, win, parent=None):
        QThread.__init__(self, parent)
        self.win = win

    def run(self):
        while True:
            if not q.empty():
                if self.win.current_msg == 'devinfo':
                    self.win.getDevInfo.setEnabled(True)
                    self.win.listWidgetDevInfo.addItem(q.get_nowait())
                    self.win.queue_time.put_nowait("Message devinfo is received " + self.win.get_time())
                elif self.win.current_msg == 'ds18b20':
                    self.win.getDs18b20.setEnabled(True)
                    self.win.listWidgetDs18b20.addItem(q.get_nowait())
                    self.win.queue_time.put_nowait("Message ds18b20 is received " + self.win.get_time())
                elif self.win.current_msg == 'reboot_dev':
                    self.win.rebootDevice.setEnabled(True)
                    self.win.listWidgetReboot.addItem(q.get_nowait())
                    self.win.queue_time.put_nowait("Message reboot is received " + self.win.get_time())
                q.task_done()


class ProtoCOBSCat(ProtoCOBSJSON):
    def __init__(self):
        super().__init__()
        self.output = sys.stdout

    def register_output(self, output):
        self.output = output

    def handle_packet(self, packet):
        self.handle_cobs(cobs.decode(packet))

    def handle_cobs(self, data):
        self.in_msg.ParseFromString(data)
        self.handle_msg(self.in_msg)

    def write_cobs(self, data):
        packet = cobs.encode(data) + self.TERMINATOR
        self.transport.write(packet)

    def handle_msg_json(self, data):
        print('\033[95m', end='', file=self.output)
        print(data, file=self.output)
        q.put_nowait(str(data))
        print('\033[92m', end='', file=self.output)
        sys.stdout.flush()


class MsgWindow(QtWidgets.QMainWindow, msg_window.Ui_MsgWindow, QtWidgets.QMessageBox):
    def __init__(self, queue_time):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

        # Attributes begin
        self.current_msg = 0
        self.isOpen = False
        self.thread = 0
        self.protocol = 0
        self.transport = 0
        self.queue_time = queue_time
        self.recv_thread = ReceivingThread(self)
        # Attributes end

        # Settings begin
        # fill cw_cmd
        self.fill_combo_box(["CW command enumeration", "CW_ON", "CW_OFF", "CW_FORM_START", "CW_FORM_FINISH"])
        self.disable_all_tabs()
        self.recv_thread.start()
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
        self.getDevInfo.setEnabled(False)
        return 0
    # Send devinfo message end

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
        msg = '{"req":{"ds18b20":{}}}'
        self.current_msg = 'ds18b20'
        self.send_msg(msg)
        self.queue_time.put_nowait("Message ds18b20 is send " + self.get_time())
        self.getDs18b20.setEnabled(False)
        # Send ds18b20 message
        return 0

    def set_cw_mode(self):
        # Set device in cw mode message
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

    def init_thread(self, port):
        self.thread = serial.threaded.ReaderThread(port, ProtoCOBSCat)
        self.thread.start()

        (self.transport, self.protocol) = self.thread.connect()

        self.protocol.set_msg_class(exch())

    def send_msg(self, msg):
        self.protocol.write_msg_json(msg, exch())

    def get_time(self):
        t = time.localtime()  # get current time
        return str(t[2]) + ":" + str(t[1]) + ":" + str(t[0]) + " " + str(t[3]) + ":" + str(t[4]) + ":" + str(t[5])



