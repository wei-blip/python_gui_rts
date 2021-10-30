from MyThreads import ReaderSocketThread
import time
import queue
import socket


from DVT_WIN import Ui_DVW_WIN
from json_protobuf_proto import JSONProtobufProto
from rs_0006_0_icp_pb2 import *
from PyQt5 import QtWidgets
from msg_window import Ui_MsgWindow

q = queue.Queue()


# class MsgWindow(QtWidgets.QMainWindow, Ui_MsgWindow, QtWidgets.QMessageBox, JSONProtobufProto):
#     def __init__(self, queue_time, sock, sock_thread):
#         super().__init__()
#         self.setupUi(self)  # Это нужно для инициализации нашего дизайна
#
#         # Attributes begin
#         self.transport = sock
#         self.in_msg = exch()
#         self.current_msg = 0
#         self.isOpen = False
#         self.thread = 0
#         self.queue_time = queue_time
#         self.reader_thread = sock_thread
#         # Attributes end
#
#         # Settings begin
#         # fill cw_cmd
#         self.fill_combo_box(["CW command", "CW_ON", "CW_OFF", "CW_FORM_START", "CW_FORM_FINISH"])
#         self.disable_all_tabs()
#         # self.recv_thread.start()
#         # Settings end
#
#         # Callback begin
#         self.getDevInfo.clicked.connect(self.get_dev_info)
#         self.getMcuTelemetry.clicked.connect(self.get_mcu_telemetry)
#         self.getJoinKey.clicked.connect(self.get_join_key)
#         self.getAdxl345.clicked.connect(self.get_adxl345)
#         self.getDs18b20.clicked.connect(self.get_ds18b20)
#         self.rebootDevice.clicked.connect(self.reboot_dev)
#         self.setCwMode.clicked.connect(self.set_cw_mode)
#         self.getVibro.clicked.connect(self.get_vibro)
#         # Callback end
#
#     # Send devinfo message begin
#     def get_dev_info(self):
#         msg = '{"req":{"devinfo":{}}}'
#         self.current_msg = 'devinfo'
#         self.queue_time.put_nowait("Message devinfo is send " + get_time())
#         self.send_msg(msg)
#         self.getDevInfo.setEnabled(False)
#         return 0
#     # Send devinfo message end
#
#     def get_mcu_telemetry(self):
#         pass
#         # Send mcu_telemetry message
#         return 0
#
#     def get_join_key(self):
#         self.current_msg = 'join_key'
#         key = self.joinKey.text()  # get text with key
#         if self.setKey.isChecked():
#             msg = '{"req":{"joinKey":{"set_key":true, "join_key":' + key + '}}}'
#         else:
#             msg = '{"req":{"joinKey":{"set_key":false, "join_key":' + key + '}}}'
#         msg = '{"req":{"loraParam":{"bw":"BW250","cr":"CR4_7","freq":868000000,"pwr":-3,"sf":12,"set_param":true}}}'
#         self.send_msg(msg)
#         self.queue_time.put_nowait("Message join key is send " + get_time())
#         self.getJoinKey.setEnabled(False)
#         # Send join_key message
#         return 0
#
#     # Send adxl345 message begin
#     def get_adxl345(self):
#         msg = '{"req":{"adxl345":{}}}'
#         self.current_msg = 'adxl345'
#         self.send_msg(msg)
#         self.queue_time.put_nowait("Message ADXL345 is send " + get_time())
#         self.getDs18b20.setEnabled(False)
#         return 0
#     # Send adxl345 message end
#
#     # Send ds18b20 message begin
#     def get_ds18b20(self):
#         msg = '{"req":{"ds18b20":{}}}'
#         self.current_msg = 'ds18b20'
#         self.send_msg(msg)
#         self.queue_time.put_nowait("Message DS18B20 is send " + get_time())
#         self.getDs18b20.setEnabled(False)
#         return 0
#     # Send ds18b20 message end
#
#     # Set device in cw mode message begin
#     def set_cw_mode(self):
#         cmd = self.cw_cmd.currentText()  # get cw command
#         freq = str(self.freq.value())  # get frequency value
#         pwr = str(self.pwr_dbm.value())  # get power value
#         dur = str(self.duration.value())  # get duration value
#         msg = '{"req":{""}'
#         return 0
#     # Set device in cw mode message end
#
#     # Reboot device begin
#     def reboot_dev(self):
#         if self.swap.isChecked():
#             msg = '{"req":{"reboot":{"swap": true}}}'
#         else:
#             msg = '{"req":{"reboot":{"swap": false}}}'
#         self.current_msg = 'reboot_dev'
#         self.send_msg(msg)
#         self.queue_time.put_nowait("Message reboot is send " + get_time())
#         self.rebootDevice.setEnabled(False)
#         return 0
#     # Reboot device end
#
#     # Get vibro measurements begin
#     def get_vibro(self):
#         self.current_msg = 'vibro'
#         msg = '{"req":{"vibro":{}}}'
#         self.send_msg(msg)
#         self.queue_time.put_nowait("Message vibro is send " + get_time())
#         self.getVibro.setEnabled(False)
#         return 0
#     # Get vibro measurements end
#
#     # Fill combo box begin
#     def fill_combo_box(self, arr):
#         for i in arr:
#             self.cw_cmd.addItem(str(i))
#             print(i)
#     # Fill combo box end
#
#     # Disable all tabs begin
#     def disable_all_tabs(self):
#         self.tabMessage.setTabEnabled(int(TabIndex.DEV_INFO), False)
#         self.tabMessage.setTabEnabled(int(TabIndex.MCU_TELEMETRY), False)
#         self.tabMessage.setTabEnabled(int(TabIndex.JOIN_KEY), False)
#         self.tabMessage.setTabEnabled(int(TabIndex.DS18B20), False)
#         self.tabMessage.setTabEnabled(int(TabIndex.ADXL345), False)
#         self.tabMessage.setTabEnabled(int(TabIndex.REBOOT), False)
#         self.tabMessage.setTabEnabled(int(TabIndex.CW_MODE), False)
#         self.tabMessage.setTabEnabled(int(TabIndex.VIBRO), False)
#     # Disable all tabs end
#
#     # Close event begin
#     def closeEvent(self, event):
#         self.isOpen = False
#         self.disable_all_tabs()
#         event.accept()
#     # Close event end
#
#     # Enable tab begin
#     def enable_tab(self, index):
#         self.tabMessage.setTabEnabled(int(index), True)
#     # Enable tab end
#
#     # Send message begin
#     def send_msg(self, data):
#         self.write_msg_json(data, exch())
#     # Send message end


class DvtReq(QtWidgets.QMainWindow, Ui_DVW_WIN, QtWidgets.QMessageBox, JSONProtobufProto):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(1082, 898)

        # Parent attribute begin
        # self.in_msg = exch()
        # self.in_msg = exch()
        # self.json_string = '{}'
        # self.is_received = False
        # Parent attribute end

        # Error dialog begin
        self.error_dialog = QtWidgets.QMessageBox()  # create error dialog object
        self.error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
        self.error_dialog.setWindowTitle("Error")
        # Error dialog end

        # Fill table labels begin
        self.tableWidgetMasterInfo.setVerticalHeaderLabels(["DevEui", "Family", "Version", "Join Key",
                                                            "DS18B20", "MCU ADC"])
        self.tableWidgetMasterVibro.setVerticalHeaderLabels(["x", "y", "z"])
        self.tableWidgetMasterVibro.setHorizontalHeaderLabels(["VIBRO, rmms", "ADXL, g"])
        self.tableWidgetSlaveData.setVerticalHeaderLabels(["ACC x", "ACC y", "ACC z", "DS18B20", "MCU ADC"])
        self.tableWidgetSlaveInfo.setVerticalHeaderLabels(["DevEui", "Family", "Version", "Join Key"])
        self.tableWidgetSlaveRadio.setVerticalHeaderLabels(["RSSI", "SNR", "Fei"])
        self.tableWidgetSlaveVibro.setVerticalHeaderLabels(["x", "y", "z"])
        # Fill table labels end

        # For socket begin
        self.reader_thread = ReaderSocketThread(self)
        self.socketIsConnect = False
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_port = 5050
        self.sock_connect()
        # For socket end

        self.current_msg = 0

    # Send devinfo message begin
    def get_dev_info(self):
        json_msg = """{"req":{"devinfo":{}}}"""
        self.current_msg = 'devinfo'
        # self.queue_time.put_nowait("Message devinfo is send " + get_time())
        self.send_msg(json_msg)
        return 0
    # Send devinfo message end

    # Send mcuAdc message begin
    def get_mcu_adc(self):
        json_msg = """{"req":{"mcuAdc":{}}}"""
        self.current_msg = 'mcuAdc'
        self.send_msg(json_msg)
        return 0
    # Send mcuAdc message end

    def get_join_key(self):
        self.current_msg = 'join_key'
        json_msg = """{"req":{"joinKey":{"set_key":false}}}"""
        self.send_msg(json_msg)
        # # key = self.joinKey.text()  # get text with key
        # if self.setKey.isChecked():
        #     msg = '{"req":{"joinKey":{"set_key":true, "join_key":' + key + '}}}'
        # else:
        #     msg = '{"req":{"joinKey":{"set_key":false, "join_key":' + key + '}}}'
        # # msg = '{"req":{"loraParam":{"bw":"BW250","cr":"CR4_7","freq":868000000,"pwr":-3,"sf":12,"set_param":true}}}'
        # self.send_msg(msg)
        # self.queue_time.put_nowait("Message join key is send " + get_time())
        # self.getJoinKey.setEnabled(False)
        # # Send join_key message
        return 0

    # Send adxl345 message begin
    def get_adxl345(self):
        json_msg = """{"req":{"adxl345":{}}}"""
        self.current_msg = 'adxl345'
        self.send_msg(json_msg)
        self.queue_time.put_nowait("Message ADXL345 is send " + get_time())
        self.getDs18b20.setEnabled(False)
        return 0

    # Send adxl345 message end

    # Send ds18b20 message begin
    def get_ds18b20(self):
        json_msg = """{"req":{"ds18b20":{}}}"""
        self.current_msg = 'ds18b20'
        self.send_msg(json_msg)
        # self.queue_time.put_nowait("Message DS18B20 is send " + get_time())
        return 0

    # Send ds18b20 message end

    # Set device in cw mode message begin
    def set_cw_mode(self):
        cmd = self.cw_cmd.currentText()  # get cw command
        freq = str(self.freq.value())  # get frequency value
        pwr = str(self.pwr_dbm.value())  # get power value
        dur = str(self.duration.value())  # get duration value
        msg = '{"req":{""}'
        return 0

    # Set device in cw mode message end

    # Reboot device begin
    def reboot_dev(self):
        json_msg = """{"req":{"reboot":{"swap": true}}}"""
        self.current_msg = 'reboot_dev'
        self.send_msg(json_msg)
        # self.queue_time.put_nowait("Message reboot is send " + get_time())
        return 0

    # Reboot device end

    # Get vibro measurements begin
    def get_vibro(self):
        json_msg = """{"req":{"vibro":{}}}"""
        self.current_msg = 'vibro'
        self.send_msg(json_msg)
        # self.queue_time.put_nowait("Message vibro is send " + get_time())
        return 0
    # Get vibro measurements end

    # Socket connection begin
    # This function connected to socket port
    def sock_connect(self):
        try:
            self.transport.connect(('localhost', self.sock_port))
        except socket.error:
            self.error_dialog.setText("Address " + str(self.sock_port) + " already use")
            self.error_dialog.show()
            return 1
        # self.listWidget.addItem("Socket connected to port: " + str(self.sock_port))  # + str(', ') + str(addr))
        self.socketIsConnect = True
        self.reader_thread.start()
        return 0
    # Socket connection end

    def send_msg(self, data):
        self.is_received = False
        self.write_msg_json(data, exch())


# Get time begin
def get_time():
    t = time.localtime()  # get current time
    return str(t[2]) + ":" + str(t[1]) + ":" + str(t[0]) + " " + str(t[3]) + ":" + str(t[4]) + ":" + str(t[5])
# Get time end
