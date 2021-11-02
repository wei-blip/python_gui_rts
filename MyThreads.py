import json
import socket

from rs_0006_0_icp_pb2 import *
from PyQt5.QtCore import QThread, QMutex
from PyQt5 import QtWidgets
import time


# Thread to display time begin
class TimeThread(QThread):
    def __init__(self, serv_win, queue, parent=None):
        QThread.__init__(self, parent)
        self.serv_win = serv_win
        self.queue = queue

    def run(self):
        while True:
            if not self.queue.empty():
                self.serv_win.listWidget.addItem(self.queue.get_nowait())
                self.queue.task_done()
            time.sleep(1)


class TransmitReceiveThread(QThread):
    mutex = QMutex()

    def __init__(self, win, queue_message, queue_processing, parent=None):
        QThread.__init__(self, parent)
        self.win = win
        self.queue_message = queue_message
        self.queue_processing = queue_processing

    def run(self):
        while True:
            if not self.queue_message.empty():
                TransmitReceiveThread.mutex.lock()
                msg_dict = self.queue_message.get_nowait()
                msg_key = list(msg_dict.keys()).pop(0)
                buf = bytearray()
                self.win.write_msg_json(msg_dict.get(msg_key), exch())
                data = b''
                if msg_key == 'cw':
                    TransmitReceiveThread.mutex.unlock()
                    continue
                try:
                    data = self.win.transport.recv(1024)
                except socket.timeout:
                    self.win.error_dialog.setText("Socket timeout!")
                    self.win.error_dialog.show()
                    TransmitReceiveThread.mutex.unlock()
                    continue

                if data:
                    buf.extend(data)
                    while self.win.TERMINATOR in buf:
                        packet, buf = buf.split(self.win.TERMINATOR, 1)
                        self.win.handle_packet(packet)
                    elem = {msg_key: self.win.json_string}
                    self.queue_processing.put_nowait(elem)
                    self.queue_processing.task_done()
                    TransmitReceiveThread.mutex.unlock()


class ProcessingThread(QThread):
    mutex = QMutex()

    def __init__(self, win, queue_processing, parent=None):
        QThread.__init__(self, parent)
        self.win = win
        self.queue_processing = queue_processing

    def run(self):
        while True:
            if not self.queue_processing.empty():
                ProcessingThread.mutex.lock()
                elem = self.queue_processing.get_nowait()
                elem_key = list(elem.keys()).pop(0)
                if elem_key == 'devinfo':
                    elem = elem.get("devinfo")
                    json_elem = json.loads(elem)
                    devinfo_elem = json_elem.get("resp").get("devinfo")
                    self.win.tableWidgetMasterInfo.setItem(
                        0, 0, QtWidgets.QTableWidgetItem(str(devinfo_elem.get("devEui")))
                    )
                    self.win.tableWidgetMasterInfo.setItem(
                        1, 0, QtWidgets.QTableWidgetItem(str(devinfo_elem.get("family")))
                    )
                    self.win.tableWidgetMasterInfo.setItem(
                        2, 0, QtWidgets.QTableWidgetItem(str(devinfo_elem.get("version")))
                    )
                elif elem_key == 'joinKey':
                    elem = elem.get("joinKey")
                    json_elem = json.loads(elem)
                    self.win.tableWidgetMasterInfo.setItem(
                        3, 0, QtWidgets.QTableWidgetItem(str(json_elem.get("resp").get("joinKey").get("joinKey")))
                    )
                elif elem_key == 'ds18b20':
                    elem = elem.get("ds18b20")
                    json_elem = json.loads(elem)
                    self.win.tableWidgetMasterInfo.setItem(
                        4, 0, QtWidgets.QTableWidgetItem(str(json_elem.get("resp").get("ds18b20").get("temp")))
                    )
                elif elem_key == 'mcuAdc':
                    elem = elem.get("mcuAdc")
                    json_elem = json.loads(elem)
                    self.win.tableWidgetMasterInfo.setItem(
                        5, 0, QtWidgets.QTableWidgetItem(str(json_elem.get("resp").get("mcuAdc").get("mcuTemperature")))
                    )
                elif elem_key == 'vibro':
                    elem = elem.get("vibro")
                    json_elem = json.loads(elem)
                    vrms = json_elem.get("resp").get("vibro").get("vrms")
                    self.win.tableWidgetMasterVibro.setItem(
                        0, 0, QtWidgets.QTableWidgetItem(str(vrms.get("x")))
                    )
                    self.win.tableWidgetMasterVibro.setItem(
                        1, 0, QtWidgets.QTableWidgetItem(str(vrms.get("x")))
                    )
                    self.win.tableWidgetMasterVibro.setItem(
                        2, 0, QtWidgets.QTableWidgetItem(str(vrms.get("x")))
                    )
                elif elem_key == 'adxl345':
                    elem = elem.get("adxl345")
                    json_elem = json.loads(elem)
                    acc_g = json_elem.get("resp").get("adxl345").get("accG")
                    self.win.tableWidgetMasterVibro.setItem(
                        0, 1, QtWidgets.QTableWidgetItem(str(acc_g.get("x")))
                    )
                    self.win.tableWidgetMasterVibro.setItem(
                        1, 1, QtWidgets.QTableWidgetItem(str(acc_g.get("y")))
                    )
                    self.win.tableWidgetMasterVibro.setItem(
                        2, 1, QtWidgets.QTableWidgetItem(str(acc_g.get("z")))
                    )
                ProcessingThread.mutex.unlock()
