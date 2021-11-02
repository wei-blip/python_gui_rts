import time
import queue
import socket

from DVT_WIN import Ui_DVW_WIN
from json_protobuf_proto import JSONProtobufProto
from PyQt5 import QtWidgets
from MyThreads import TransmitReceiveThread


class DvtReq(QtWidgets.QMainWindow, Ui_DVW_WIN, QtWidgets.QMessageBox, JSONProtobufProto):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(1082, 898)

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
        self.socketIsConnect = False
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.transport.settimeout(5)
        self.sock_port = 5050
        self.sock_connect()
        # For socket end

        self.queue_message = queue.Queue()
        self.queue_processing = queue.Queue()
        self.tx_rx_thread = TransmitReceiveThread(self, self.queue_message, self.queue_processing)
        self.tx_rx_thread.start()

        self.current_msg = ''

    # Send devinfo message begin
    def get_dev_info(self, transit):
        if not transit:
            json_msg = """{"req":{"devinfo":{}}}"""
            self.current_msg = 'devinfo'
            self.transmit_receive_msg(json_msg, 'devinfo')
        return 0
    # Send devinfo message end

    # Send mcuAdc message begin
    def get_mcu_adc(self, transit):
        if not transit:
            json_msg = """{"req":{"mcuAdc":{}}}"""
            self.current_msg = 'mcuAdc'
            self.transmit_receive_msg(json_msg, 'mcuAdc')
        return 0
    # Send mcuAdc message end

    def get_join_key(self, transit):
        if not transit:
            json_msg = """{"req":{"joinKey":{"set_key":false}}}"""
            self.current_msg = 'joinKey'
            self.transmit_receive_msg(json_msg, 'joinKey')
        return 0

    # Send adxl345 message begin
    def get_adxl345(self, transit):
        if not transit:
            json_msg = """{"req":{"adxl345":{}}}"""
            self.current_msg = 'adxl345'
            self.transmit_receive_msg(json_msg, 'adxl345')
        return 0

    # Send adxl345 message end

    # Send ds18b20 message begin
    def get_ds18b20(self, transit):
        if not transit:
            json_msg = """{"req":{"ds18b20":{}}}"""
            self.current_msg = 'ds18b20'
            self.transmit_receive_msg(json_msg, 'ds18b20')
        return 0
    # Send ds18b20 message end

    # Set device in cw mode message begin
    def set_cw_mode(self, cmd, transit):
        if not transit:
            self.current_msg = 'cw'
            json_msg = """{}"""
            if cmd == "CW_ON":
                freq = str(self.spinBoxMasterFrequency.value())  # get frequency value
                pwr = str(self.spinBoxMasterPower.value())  # get power value
                dur = str(self.spinBoxMasterDuration.value())  # get duration value
                json_msg = """{"req":{"cw":{"cmd":"CW_ON", "cw_param":{"freq":""" + freq + """,""" \
                           + """"pwr_dbm":""" + pwr + """,""" + """"duration":""" + dur + """}}}}"""
            elif cmd == "CW_OFF":
                json_msg = """{"req":{"cw":{"cmd":"CW_OFF"}}}"""
            self.transmit_receive_msg(json_msg, 'cw')
        return 0

    # Set device in cw mode message end

    # Reboot device begin
    def reboot_dev(self, transit):
        if not transit:
            json_msg = """{"req":{"reboot":{"swap": true}}}"""
            self.current_msg = 'reboot_dev'
            self.transmit_receive_msg(json_msg, 'reboot_dev')
        return 0

    # Reboot device end

    # Get vibro measurements begin
    def get_vibro(self, transit):
        if not transit:
            json_msg = """{"req":{"vibro":{}}}"""
            self.current_msg = 'vibro'
            self.transmit_receive_msg(json_msg, 'vibro')
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
        self.socketIsConnect = True
        return 0
    # Socket connection end

    def transmit_receive_msg(self, data, msg_type):
        self.queue_message.put_nowait({msg_type: data})


# Get time begin
def get_time():
    t = time.localtime()  # get current time
    return str(t[2]) + ":" + str(t[1]) + ":" + str(t[0]) + " " + str(t[3]) + ":" + str(t[4]) + ":" + str(t[5])
# Get time end
