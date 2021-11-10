import json
import queue
import socket

from rs_0006_0_icp_pb2 import *
from PyQt5.QtCore import QThread, QMutex, pyqtSignal
from PyQt5 import QtWidgets
from json_protobuf_proto import JSONProtobufProto
from dataclasses import dataclass
from random import randrange
from enum import IntEnum


class ProcThreads(IntEnum):
    MASTER = 0
    SLAVE = 1


@dataclass
class Status:
    thread: ProcThreads
    msg_type: str = ''


@dataclass
class QueueProcessing:
    json_string: str = ''
    msg_type: str = ''


@dataclass
class FillTable:
    status: Status
    data: dict


# This class transmit and receive messages from socket and putting into processing queue for next processing
# If was socket timeout exception generated socket_timeout_signal and thread sleeping on 1 second
class TransmitReceiveThread(QThread, JSONProtobufProto):
    # mutex = QMutex()
    per_signal = pyqtSignal(int)
    socket_timeout_signal = pyqtSignal()
    queue_full_signal = pyqtSignal(str)
    start_proc_thread = pyqtSignal(Status)

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
        # while True:
        # This for sending and receive message through socket
        # This is default mode
        while (not self.queue_message.empty()) and self.socketIsConnect and (not self.per):
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
                    status = Status(thread=ProcThreads.MASTER, msg_type=msg_type)
                    self.start_proc_thread.emit(status)
                else:
                    try:
                        self.queue_processing_slave.put(q_item_proc, block=True, timeout=1)
                    except queue.Full:
                        self.queue_full_signal.emit("Your message not sending because one of"
                                                    " queue (queue_processing_slave) if full, please try later")
                        break
                    status = Status(thread=ProcThreads.SLAVE, msg_type=msg_type)
                    self.start_proc_thread.emit(status)

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
                msg = self.get_last_message()
                if not msg:
                    error = error + 1
                    n = n + 1
                    continue
                resp_id = json.loads(msg).get("resp").get("respId")
                if resp_id != req_id:
                    error = error + 1
                n = n + 1
            # s = """Transfer is over\nPackets send: """ + str(self.num_packet) + """\nPackets lost: """ \
            #     + str(error) + """\n """
            self.per = False
            self.sock.settimeout(5)
            self.per_signal.emit(error)

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
        msg = ''
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
                msg = self.json_string
        return msg
    # Getting last message from socket buffer end


class ProcessingThread(QThread):
    mutex = QMutex()
    fill_table_signal = pyqtSignal(FillTable)

    def __init__(self, queue_processing, is_master, parent=None):
        QThread.__init__(self, parent)
        self.queue_processing = queue_processing
        self.is_master = is_master

    def run(self):
        while not self.queue_processing.empty():
            ProcessingThread.mutex.lock()
            q_elem = self.queue_processing.get_nowait()
            msg_type = q_elem.msg_type
            json_string = q_elem.json_string
            self.queue_processing.task_done()
            if msg_type == 'devinfo':
                json_dict = json.loads(json_string)
                if self.is_master:
                    status = Status(msg_type=msg_type, thread=ProcThreads.MASTER)
                    fill_table = FillTable(status=status, data=json_dict)
                    self.fill_table_signal.emit(fill_table)
                else:
                    status = Status(msg_type=msg_type, thread=ProcThreads.SLAVE)
                    fill_table = FillTable(status=status, data=json_dict)
                    self.fill_table_signal.emit(fill_table)
            elif msg_type == 'joinKey':
                json_dict = json.loads(json_string)
                if self.is_master:
                    status = Status(msg_type=msg_type, thread=ProcThreads.MASTER)
                    fill_table = FillTable(status=status, data=json_dict)
                    self.fill_table_signal.emit(fill_table)
                else:
                    status = Status(msg_type=msg_type, thread=ProcThreads.SLAVE)
                    fill_table = FillTable(status=status, data=json_dict)
                    self.fill_table_signal.emit(fill_table)
            elif msg_type == 'ds18b20':
                json_dict = json.loads(json_string)
                if self.is_master:
                    status = Status(msg_type=msg_type, thread=ProcThreads.MASTER)
                    fill_table = FillTable(status=status, data=json_dict)
                    self.fill_table_signal.emit(fill_table)
                else:
                    status = Status(msg_type=msg_type, thread=ProcThreads.SLAVE)
                    fill_table = FillTable(status=status, data=json_dict)
                    self.fill_table_signal.emit(fill_table)
            elif msg_type == 'mcuAdc':
                json_dict = json.loads(json_string)
                if self.is_master:
                    status = Status(msg_type=msg_type, thread=ProcThreads.MASTER)
                    fill_table = FillTable(status=status, data=json_dict)
                    self.fill_table_signal.emit(fill_table)
                else:
                    status = Status(msg_type=msg_type, thread=ProcThreads.SLAVE)
                    fill_table = FillTable(status=status, data=json_dict)
                    self.fill_table_signal.emit(fill_table)
            elif msg_type == 'vibro':
                json_dict = json.loads(json_string)
                if self.is_master:
                    status = Status(msg_type=msg_type, thread=ProcThreads.MASTER)
                    fill_table = FillTable(status=status, data=json_dict)
                    self.fill_table_signal.emit(fill_table)
                else:
                    status = Status(msg_type=msg_type, thread=ProcThreads.SLAVE)
                    fill_table = FillTable(status=status, data=json_dict)
                    self.fill_table_signal.emit(fill_table)
            elif msg_type == 'adxl345':
                json_dict = json.loads(json_string)
                if self.is_master:
                    status = Status(msg_type=msg_type, thread=ProcThreads.MASTER)
                    fill_table = FillTable(status=status, data=json_dict)
                    self.fill_table_signal.emit(fill_table)
                else:
                    status = Status(msg_type=msg_type, thread=ProcThreads.SLAVE)
                    fill_table = FillTable(status=status, data=json_dict)
                    self.fill_table_signal.emit(fill_table)
            ProcessingThread.mutex.unlock()
