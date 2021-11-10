import time
import queue

from DVT_WIN import Ui_DVW_WIN
from PyQt5 import QtWidgets
from MyThreads import ProcessingThread, TransmitReceiveThread, ProcThreads
from dataclasses import dataclass
from PyQt5.QtCore import Qt


@dataclass
class QueueMessage:
    json_msg: str = ''
    msg_type: str = ''
    transit: bool = False


class DvtReq(QtWidgets.QMainWindow, Ui_DVW_WIN, QtWidgets.QMessageBox):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(self.width(), self.height())

        # Table label settings begin
        self.tableWidgetMasterInfo.setVerticalHeaderLabels(["DevEui", "Family", "Version", "Join Key",
                                                            "DS18B20", "MCU ADC"])
        self.tableWidgetMasterVibro.setVerticalHeaderLabels(["X", "Y", "Z"])
        self.tableWidgetMasterVibro.setHorizontalHeaderLabels(["VIBRO, vrms", "ADXL, g"])
        self.tableWidgetSlaveData.setVerticalHeaderLabels(["ACC x", "ACC y", "ACC z", "DS18B20", "MCU ADC"])
        self.tableWidgetSlaveInfo.setVerticalHeaderLabels(["DevEui", "Family", "Version", "Join Key"])
        self.tableWidgetSlaveRadio.setVerticalHeaderLabels(["RSSI", "SNR", "Fei", "PER"])
        self.tableWidgetSlaveVibro.setVerticalHeaderLabels(["VRMS x", "VRMS y", "VRMS z"])

        self.correct_tables()
        # Table label settings end

        # CW spin box begin
        # Master begin
        self.spinBoxMasterPower.setValue(0)
        self.spinBoxMasterDuration.setValue(5)
        self.spinBoxMasterFrequency.setValue(864500000)
        # Master end

        # Slave begin
        self.spinBoxSlavePower.setValue(0)
        self.spinBoxSlaveDuration.setValue(5)
        self.spinBoxSlaveFrequency.setValue(864500000)
        # Slave end
        # CW spin box end

        # For PER begin
        self.spinBoxSlavePER.setValue(25)
        # For PER end

        # For threads begin
        self.queue_message = queue.Queue(maxsize=15)
        self.queue_processing_master = queue.Queue(maxsize=15)
        self.queue_processing_slave = queue.Queue(maxsize=15)
        self.proc_thread_master = ProcessingThread(self.queue_processing_master, True)
        self.proc_thread_slave = ProcessingThread(self.queue_processing_slave, False)
        self.tx_rx_thread = TransmitReceiveThread(self.queue_message, self.queue_processing_master,
                                                  self.queue_processing_slave)
        self.threads = [self.tx_rx_thread, self.proc_thread_master, self.proc_thread_slave]
        # For threads end

        # Callbacks begin
        self.tx_rx_thread.start_proc_thread.connect(self.start_proc_thread)
        # Callbacks end

    # Send devinfo message begin
    def get_dev_info(self, transit):
        q_item = QueueMessage()
        q_item.msg_type = 'devinfo'
        if not transit:
            q_item.json_msg = """{"req":{"devinfo":{}},"transit":false}"""
        else:
            q_item.json_msg = """{"req":{"devinfo":{}},"transit":true}"""
            q_item.transit = True
        self.transmit_receive_msg(q_item)
        return 0

    # Send devinfo message end

    # Send mcuAdc message begin
    def get_mcu_adc(self, transit):
        q_item = QueueMessage()
        q_item.msg_type = 'mcuAdc'
        if not transit:
            q_item.json_msg = """{"req":{"mcuAdc":{}},"transit":false}"""
        else:
            q_item.json_msg = """{"req":{"mcuAdc":{}},"transit":true}"""
            q_item.transit = True
        self.transmit_receive_msg(q_item)
        return 0

    # Send mcuAdc message end

    # Send join key message begin
    def get_join_key(self, transit):
        q_item = QueueMessage()
        q_item.msg_type = 'joinKey'
        if not transit:
            q_item.json_msg = """{"req":{"joinKey":{"set_key":false}},"transit":false}"""
        else:
            q_item.json_msg = """{"req":{"joinKey":{"set_key":false}},"transit":true}"""
            q_item.transit = True
        self.transmit_receive_msg(q_item)
        return 0

    # Send join key message end

    # Send adxl345 message begin
    def get_adxl345(self, transit):
        q_item = QueueMessage()
        q_item.msg_type = 'adxl345'
        if not transit:
            q_item.json_msg = """{"req":{"adxl345":{}},"transit":false}"""
        else:
            q_item.json_msg = """{"req":{"adxl345":{}},"transit":true}"""
            q_item.transit = True
        self.transmit_receive_msg(q_item)
        return 0

    # Send adxl345 message end

    # Send ds18b20 message begin
    def get_ds18b20(self, transit):
        q_item = QueueMessage()
        q_item.msg_type = 'ds18b20'
        if not transit:
            q_item.json_msg = """{"req":{"ds18b20":{}},"transit":false}"""
        else:
            q_item.json_msg = """{"req":{"ds18b20":{}},"transit":true}"""
            q_item.transit = True
        self.transmit_receive_msg(q_item)
        return 0

    # Send ds18b20 message end

    # Set device in cw mode message begin
    def set_cw_mode(self, cmd, transit):
        q_item = QueueMessage()
        q_item.msg_type = 'cw'
        if not transit:
            if cmd == "CW_ON":
                freq = str(self.spinBoxMasterFrequency.value())  # get frequency value
                pwr = str(self.spinBoxMasterPower.value())  # get power value
                dur = str(self.spinBoxMasterDuration.value())  # get duration value
                q_item.json_msg = """{"req":{"cw":{"cmd":"CW_ON", "cw_param":{"freq":""" + freq + """,""" \
                                  + """"pwr_dbm":""" + pwr + """,""" + """"duration":""" + dur + """}}}, 
                                "transit":false} """
            elif cmd == "CW_OFF":
                q_item.json_msg = """{"req":{"cw":{"cmd":"CW_OFF"}},"transit":false}"""
                q_item.transit = True
        else:
            if cmd == "CW_ON":
                freq = str(self.spinBoxMasterFrequency.value())  # get frequency value
                pwr = str(self.spinBoxMasterPower.value())  # get power value
                dur = str(self.spinBoxMasterDuration.value())  # get duration value
                q_item.json_msg = """{"req":{"cw":{"cmd":"CW_ON", "cw_param":{"freq":""" + freq + """,""" \
                                  + """"pwr_dbm":""" + pwr + """,""" + """"duration":""" + dur + """}}},
                                  "transit":true} """
            elif cmd == "CW_OFF":
                q_item.json_msg = """{"req":{"cw":{"cmd":"CW_OFF"}},"transit":true}"""
                q_item.transit = True
        self.transmit_receive_msg(q_item)
        return 0

    # Set device in cw mode message end

    # Reboot device begin
    def reboot_dev(self, transit):
        q_item = QueueMessage()
        q_item.msg_type = 'reboot_dev'
        if not transit:
            q_item.json_msg = """{"req":{"reboot":{"swap": true}},"transit":false}"""
        else:
            q_item.json_msg = """{"req":{"reboot":{"swap": true}},"transit":true}"""
            q_item.transit = True
        self.transmit_receive_msg(q_item)
        return 0

    # Reboot device end

    # Get vibro measurements begin
    def get_vibro(self, transit):
        q_item = QueueMessage()
        q_item.msg_type = 'vibro'
        if not transit:
            q_item.json_msg = """{"req":{"vibro":{}},"transit":false}"""
        else:
            q_item.json_msg = """{"req":{"vibro":{}},"transit":true}"""
            q_item.transit = True
        self.transmit_receive_msg(q_item)
        return 0

    # Get vibro measurements end

    def transmit_receive_msg(self, q_item):
        try:
            self.queue_message.put(q_item, block=True, timeout=1)
        except queue.Full:
            self.tx_rx_thread.queue_full_signal.emit("Your message not sending because one of queue "
                                                     "if full(queue_message), please try later")
            return
        if q_item.transit:
            self.listWidgetMessageStatus.addItem("Message " + q_item.msg_type + " for slave device is sending")
        else:
            self.listWidgetMessageStatus.addItem("Message " + q_item.msg_type + " for master device is sending")
        self.tx_rx_thread.start()

    def correct_tables(self):
        self.tableWidgetMasterInfo.verticalHeader().setFixedWidth(64)
        self.tableWidgetMasterVibro.verticalHeader().setFixedWidth(64)
        self.tableWidgetSlaveData.verticalHeader().setFixedWidth(64)
        self.tableWidgetSlaveVibro.verticalHeader().setFixedWidth(64)
        self.tableWidgetSlaveInfo.verticalHeader().setFixedWidth(64)
        self.tableWidgetSlaveRadio.verticalHeader().setFixedWidth(64)

        self.tableWidgetMasterVibro.horizontalHeader().setFixedWidth(300)

        self.tableWidgetMasterVibro.verticalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.tableWidgetMasterInfo.verticalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.tableWidgetSlaveRadio.verticalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.tableWidgetSlaveInfo.verticalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.tableWidgetSlaveVibro.verticalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.tableWidgetSlaveData.verticalHeader().setDefaultAlignment(Qt.AlignCenter)

    def start_proc_thread(self, status):
        if status.thread == ProcThreads.MASTER:
            self.listWidgetMessageStatus.addItem("Message " + status.msg_type + " for master device is received")
            self.proc_thread_master.start()
        elif status.thread == ProcThreads.SLAVE:
            self.listWidgetMessageStatus.addItem("Message " + status.msg_type + " for slave device is received")
            self.proc_thread_slave.start()

    def fill_table_field(self, table, row, col, item):
        table.setItem(
            row, col,
            QtWidgets.QTableWidgetItem(str(item))
        )


# Get time begin
def get_time():
    t = time.localtime()  # get current time
    return str(t[2]) + ":" + str(t[1]) + ":" + str(t[0]) + " " + str(t[3]) + ":" + str(t[4]) + ":" + str(t[5])
# Get time end
