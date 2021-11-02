from MyThreads import ProcessingThread
from msg_window_cls import DvtReq
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from enum import IntEnum
from rs_0006_0_icp_pb2 import *


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


class DvtApp(DvtReq):
    def __init__(self):
        super().__init__()

        # Callbacks master begin
        self.pushButtonMasterReboot.clicked.connect(self.master_reboot)
        self.pushButtonMasterStartCW.clicked.connect(self.master_start_cw)
        self.pushButtonMasterStopCW.clicked.connect(self.master_stop_cw)
        # Callbacks master end

        # Callbacks slave begin
        self.pushButtonSlaveReboot.clicked.connect(self.slave_reboot)
        self.pushButtonSlaveStartCW.clicked.connect(self.slave_start_cw)
        self.pushButtonSlaveStopCW.clicked.connect(self.slave_stop_cw)
        self.pushButtonSlaveStartPER.clicked.connect(self.slave_start_per)
        self.pushButtonSlaveGetInfo.clicked.connect(self.slave_get_info)
        self.pushButtonSlaveGetData.clicked.connect(self.slave_get_data)
        self.pushButtonSlaveGetVibro.clicked.connect(self.slave_get_vibro)
        self.pushButtonSlaveGetAll.clicked.connect(self.slave_get_all)
        # Callbacks slave end

        # CW spin box begin
        self.spinBoxMasterPower.setValue(0)
        self.spinBoxMasterDuration.setValue(5)
        self.spinBoxMasterFrequency.setValue(864500000)
        # CW spin box end

        # Buffers begin
        self.cw_dict = dict()
        self.resp_buffer = list()
        self.vibro_buffer = list()
        self.msg_list = list()
        self.json_list = list()
        # Buffers end

        # For receive vibro data begin
        self.proc_thread = ProcessingThread(self, self.queue_processing)
        self.threads = [self.tx_rx_thread, self.proc_thread]
        # For receive vibro data end

        # Timer begin
        self.vibro_timer = QTimer()
        self.vibro_timer.setInterval(10000)
        self.vibro_timer.timeout.connect(self.measure_vibro)
        # Timer end

    # Filling master information table begin
    def master_get_info(self):
        self.get_dev_info(False)
        self.get_join_key(False)
        self.get_ds18b20(False)
        self.get_mcu_adc(False)

    def master_get_vibro(self):
        self.get_vibro(False)
        self.get_adxl345(False)

    def master_reboot(self):
        self.reboot_dev(False)

    def master_start_cw(self):
        self.set_cw_mode("CW_ON", False)

    def master_stop_cw(self):
        self.set_cw_mode("CW_OFF", False)

    def slave_reboot(self):
        pass

    def slave_start_cw(self):
        pass

    def slave_stop_cw(self):
        pass

    def slave_start_per(self):
        pass

    def slave_get_info(self):
        pass

    def slave_get_data(self):
        pass

    def slave_get_vibro(self):
        pass

    def slave_get_all(self):
        pass

    def showEvent(self, event):
        self.proc_thread.start()
        self.master_get_info()
        self.master_get_vibro()
        self.vibro_timer.start()
        event.accept()

    def measure_vibro(self):
        self.vibro_timer.stop()
        self.master_get_vibro()
        self.vibro_timer.start()

    def close_threads(self):
        for thread in self.threads:
            thread.quit()

    def closeEvent(self, event):
        close_dialog = QtWidgets.QMessageBox.question(
            self, "Message",
            "Are you sure you want to quit?",
            QtWidgets.QMessageBox.Close | QtWidgets.QMessageBox.Cancel
        )
        if close_dialog == QtWidgets.QMessageBox.Close:
            self.close_threads()
            self.transport.close()
            self.vibro_timer.killTimer(self.vibro_timer.timerId())
            event.accept()
        else:
            event.ignore()


def main():
    dvt_app = QtWidgets.QApplication(sys.argv)
    dvt_win = DvtApp()
    dvt_win.show()
    dvt_app.exec_()


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
