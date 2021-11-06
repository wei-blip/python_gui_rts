import json
import queue
import socket
import time

from rs_0006_0_icp_pb2 import *
from PyQt5.QtCore import QThread, QMutex, pyqtSignal
from PyQt5 import QtWidgets
from json_protobuf_proto import JSONProtobufProto
from enum import IntEnum
from dataclasses import dataclass
from random import randrange


class TableRow(IntEnum):
    FIRST_ROW = 0
    SECOND_ROW = 1
    THIRD_ROW = 2
    FOURTH_ROW = 3
    FIFTH_ROW = 4
    SIXTH_ROW = 5


class TableColumn(IntEnum):
    FIRST_COLUMN = 0
    SECOND_COLUMN = 1
    THIRD_COLUMN = 2


@dataclass
class QueueProcessing:
    json_string: str = ''
    msg_type: str = ''


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


# This class transmit and receive messages from socket and putting into processing queue for next processing
# If was socket timeout exception generated socket_timeout_signal and thread sleeping on 1 second
class TransmitReceiveThread(QThread, JSONProtobufProto):
    # mutex = QMutex()
    per_signal = pyqtSignal(str)
    socket_timeout_signal = pyqtSignal()
    queue_full_signal = pyqtSignal(str)
    queue_empty_signal = pyqtSignal(str)

    def __init__(self, queue_message, queue_processing_master, queue_processing_slave):
        super().__init__()
        # Queues begin
        self.queue_message = queue_message
        self.queue_processing_master = queue_processing_master
        self.queue_processing_slave = queue_processing_slave
        # Queues end

        # For PER begin
        self.per = False
        self.num_packet = 5
        # For PER end

        # Error dialog begin
        self.error_dialog = QtWidgets.QMessageBox()  # create error dialog object
        self.error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
        self.error_dialog.setWindowTitle("Error")
        # Error dialog end

        # For socket
        self.sock = socket.socket()
        self.sock.settimeout(5)
        self.sock_port = 5050
        self.socketIsConnect = False
        self.sock_connect()
        # For socket

    def run(self):
        while True:
            # This for sending and receive message through socket
            # This is default mode
            if (not self.queue_message.empty()) and self.socketIsConnect and (not self.per):
                # TransmitReceiveThread.mutex.lock()
                q_item_msg = self.queue_message.get_nowait()
                json_msg = q_item_msg.json_msg
                msg_type = q_item_msg.msg_type
                transit = q_item_msg.transit
                buf = bytearray()

                self.write_msg_json(json_msg, exch())
                data = b''
                if msg_type == 'cw' or msg_type == 'reboot_dev':
                    TransmitReceiveThread.mutex.unlock()
                    continue
                try:
                    data = self.sock.recv(128)
                except socket.timeout:
                    self.socket_timeout_signal.emit()
                    self.msleep(1000)
                    continue
                self.queue_message.task_done()

                if data:
                    buf.extend(data)
                    while self.TERMINATOR in buf:
                        packet, buf = buf.split(self.TERMINATOR, 1)
                        self.handle_packet(packet)
                    q_item_proc = QueueProcessing()
                    q_item_proc.msg_type = q_item_msg.msg_type
                    q_item_proc.json_string = self.json_string
                    if not transit:
                        try:
                            self.queue_processing_master.put(q_item_proc, block=True, timeout=1)
                        except queue.Full:
                            self.queue_full_signal.emit("Your message not sending because one of"
                                                        " queue (queue_processing_master) if full, please try later")
                            break
                    else:
                        try:
                            self.queue_processing_slave.put(q_item_proc, block=True, timeout=1)
                        except queue.Full:
                            self.queue_full_signal.emit("Your message not sending because one of"
                                                        " queue (queue_processing_slave) if full, please try later")
                            break

            # This for measurement PER
            if self.per:
                buf = bytearray()
                self.sock.settimeout(1)
                json_msg = """{"req":{"devinfo":{}},"transit":true}"""
                n = 0
                error = 0
                while n < self.num_packet:
                    req_id = randrange(0, 2 ** 32 - 1)
                    json_dict = json.loads(json_msg)
                    json_dict.get("req")["req_id"] = req_id
                    json_msg = json.dumps(json_dict)
                    self.write_msg_json(json_msg, exch())
                    data = b''
                    backup = self.get_last_message()
                    if not backup:
                        error = error + 1
                        n = n + 1
                        continue
                    resp_id = json.loads(backup).get("resp").get("respId")
                    if resp_id != req_id:
                        error = error + 1
                    n = n + 1
                s = """Transfer is over\nPackets send: """ + str(self.num_packet) + """\nPackets lost: """ \
                    + str(error) + """\n """
                self.per = False
                self.sock.settimeout(5)
                self.per_signal.emit(s)
            self.msleep(100)

    # Socket connection begin
    # This function connected to socket port
    def sock_connect(self):
        try:
            self.sock.connect(('localhost', self.sock_port))
        except socket.error:
            self.error_dialog.setText("Address " + str(self.sock_port) + " already use")
            self.error_dialog.show()
            return 1
        self.socketIsConnect = True
        return 0
    # Socket connection end

    # Getting last message from socket buffer begin
    # After call this method socket buffer will be clear
    # Return value: last message in socket buffer
    def get_last_message(self):
        backup = ''
        buf = bytearray()
        data = b''
        while True:
            try:
                data = self.sock.recv(128)
            except socket.timeout:
                break
            if data:
                buf.extend(data)
                while self.TERMINATOR in buf:
                    packet, buf = buf.split(self.TERMINATOR, 1)
                    self.handle_packet(packet)
                backup = self.json_string
        return backup
    # Getting last message from socket buffer end


class ProcessingThread(QThread):
    mutex = QMutex()

    def __init__(self, win, queue_processing, is_master, parent=None):
        QThread.__init__(self, parent)
        self.win = win
        self.queue_processing = queue_processing
        self.is_master = is_master
        self.per = False

    def run(self):
        while True:
            if (not self.queue_processing.empty()) and (not self.per):
                ProcessingThread.mutex.lock()
                q_elem = self.queue_processing.get_nowait()
                msg_type = q_elem.msg_type
                json_string = q_elem.json_string
                self.queue_processing.task_done()
                if msg_type == 'devinfo':
                    json_dict = json.loads(json_string)
                    devinfo_elem = json_dict.get("resp").get("devinfo")
                    if self.is_master:
                        self.fill_devinfo_field_from_master_info_table(devinfo_elem)
                    else:
                        self.fill_devinfo_field_from_slave_info_table(devinfo_elem)
                elif msg_type == 'joinKey':
                    json_dict = json.loads(json_string)
                    if self.is_master:
                        self.fill_join_key_field_from_master_info_table(json_dict)
                    else:
                        self.fill_join_key_field_from_slave_info_table(json_dict)
                        self.fill_radio_table(json_dict.get("resp"))
                elif msg_type == 'ds18b20':
                    json_dict = json.loads(json_string)
                    if self.is_master:
                        self.fill_ds18b20_field_from_master_info_table(json_dict)
                    else:
                        self.fill_ds18b20_field_from_slave_data_table(json_dict)
                elif msg_type == 'mcuAdc':
                    json_dict = json.loads(json_string)
                    if self.is_master:
                        self.fill_mcu_adc_field_from_master_info_table(json_dict)
                    else:
                        self.fill_mcu_adc_field_from_slave_data_table(json_dict)
                elif msg_type == 'vibro':
                    json_dict = json.loads(json_string)
                    vrms = json_dict.get("resp").get("vibro").get("vrms")
                    if self.is_master:
                        self.fill_vibro_field_from_master_vibro_table(vrms)
                    else:
                        self.fill_vibro_field_from_slave_vibro_table(vrms)
                        self.fill_radio_table(json_dict.get("resp"))
                elif msg_type == 'adxl345':
                    json_dict = json.loads(json_string)
                    acc_g = json_dict.get("resp").get("adxl345").get("accG")
                    if self.is_master:
                        self.fill_adxl345_field_from_master_vibro_table(acc_g)
                    else:
                        self.fill_adxl345_field_from_slave_data_table(acc_g)
                        self.fill_radio_table(json_dict.get("resp"))
                ProcessingThread.mutex.unlock()
            self.msleep(100)

# This methods for filling table into window
# Methods for filling table fields begin
    def fill_devinfo_field_from_master_info_table(self, json_dict):
        table = self.win.tableWidgetMasterInfo
        self.fill_table_field(table, TableRow.FIRST_ROW, TableColumn.FIRST_COLUMN, json_dict.get("devEui"))
        self.fill_table_field(table, TableRow.SECOND_ROW, TableColumn.FIRST_COLUMN, json_dict.get("family"))
        self.fill_table_field(table, TableRow.THIRD_ROW, TableColumn.FIRST_COLUMN, json_dict.get("version"))

    def fill_devinfo_field_from_slave_info_table(self, json_dict):
        table = self.win.tableWidgetSlaveInfo
        self.fill_table_field(table, TableRow.FIRST_ROW, TableColumn.FIRST_COLUMN, json_dict.get("devEui"))
        self.fill_table_field(table, TableRow.SECOND_ROW, TableColumn.FIRST_COLUMN, json_dict.get("family"))
        self.fill_table_field(table, TableRow.THIRD_ROW, TableColumn.FIRST_COLUMN, json_dict.get("version"))

    def fill_join_key_field_from_master_info_table(self, json_dict):
        self.fill_table_field(self.win.tableWidgetMasterInfo, TableRow.FOURTH_ROW, TableColumn.FIRST_COLUMN,
                              json_dict.get("resp").get("joinKey").get("joinKey"))

    def fill_join_key_field_from_slave_info_table(self, json_dict):
        self.fill_table_field(self.win.tableWidgetSlaveInfo, TableRow.FOURTH_ROW, TableColumn.FIRST_COLUMN,
                              json_dict.get("resp").get("joinKey").get("joinKey"))

    def fill_ds18b20_field_from_master_info_table(self, json_dict):
        self.fill_table_field(self.win.tableWidgetMasterInfo, TableRow.FIFTH_ROW, TableColumn.FIRST_COLUMN,
                              json_dict.get("resp").get("ds18b20").get("temp"))

    def fill_ds18b20_field_from_slave_data_table(self, json_dict):
        self.fill_table_field(self.win.tableWidgetSlaveData, TableRow.FOURTH_ROW, TableColumn.FIRST_COLUMN,
                              json_dict.get("resp").get("ds18b20").get("temp"))

    def fill_mcu_adc_field_from_master_info_table(self, json_dict):
        self.fill_table_field(self.win.tableWidgetMasterInfo, TableRow.SIXTH_ROW, TableColumn.FIRST_COLUMN,
                              json_dict.get("resp").get("mcuAdc").get("mcuTemperature"))

    def fill_mcu_adc_field_from_slave_data_table(self, json_dict):
        self.fill_table_field(self.win.tableWidgetSlaveData, TableRow.FIFTH_ROW, TableColumn.FIRST_COLUMN,
                              json_dict.get("resp").get("mcuAdc").get("mcuTemperature"))

    def fill_vibro_field_from_master_vibro_table(self, json_dict):
        table = self.win.tableWidgetMasterVibro
        self.fill_table_field(table, TableRow.FIRST_ROW, TableColumn.FIRST_COLUMN, json_dict.get("x"))
        self.fill_table_field(table, TableRow.SECOND_ROW, TableColumn.FIRST_COLUMN, json_dict.get("y"))
        self.fill_table_field(table, TableRow.THIRD_ROW, TableColumn.FIRST_COLUMN, json_dict.get("z"))

    def fill_vibro_field_from_slave_vibro_table(self, json_dict):
        table = self.win.tableWidgetSlaveVibro
        self.fill_table_field(table, TableRow.FIRST_ROW, TableColumn.FIRST_COLUMN, json_dict.get("x"))
        self.fill_table_field(table, TableRow.SECOND_ROW, TableColumn.FIRST_COLUMN, json_dict.get("y"))
        self.fill_table_field(table, TableRow.THIRD_ROW, TableColumn.FIRST_COLUMN, json_dict.get("z"))

    def fill_adxl345_field_from_master_vibro_table(self, json_dict):
        table = self.win.tableWidgetMasterVibro
        self.fill_table_field(table, TableRow.FIRST_ROW, TableColumn.SECOND_COLUMN, json_dict.get("x"))
        self.fill_table_field(table, TableRow.SECOND_ROW, TableColumn.SECOND_COLUMN, json_dict.get("y"))
        self.fill_table_field(table, TableRow.THIRD_ROW, TableColumn.SECOND_COLUMN, json_dict.get("z"))

    def fill_adxl345_field_from_slave_data_table(self, json_dict):
        table = self.win.tableWidgetSlaveData
        self.fill_table_field(table, TableRow.FIRST_ROW, TableColumn.FIRST_COLUMN, json_dict.get("x"))
        self.fill_table_field(table, TableRow.SECOND_ROW, TableColumn.FIRST_COLUMN, json_dict.get("y"))
        self.fill_table_field(table, TableRow.THIRD_ROW, TableColumn.FIRST_COLUMN, json_dict.get("z"))

    def fill_radio_table(self, json_dict):
        table = self.win.tableWidgetSlaveRadio
        self.fill_table_field(table, TableRow.FIRST_ROW, TableColumn.FIRST_COLUMN, json_dict.get("rssi"))
        self.fill_table_field(table, TableRow.SECOND_ROW, TableColumn.FIRST_COLUMN, json_dict.get("snr"))
        self.fill_table_field(table, TableRow.THIRD_ROW, TableColumn.FIRST_COLUMN, json_dict.get("fei"))

    def fill_table_field(self, table, row, col, item):
        table.setItem(
            row, col,
            QtWidgets.QTableWidgetItem(str(item))
        )
# Methods for filling table fields end
