from msg_window_cls import DvtReq
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer, pyqtSignal
from rs_0006_0_icp_pb2 import *
from darktheme.widget_template import DarkPalette
# from MyThreads import PerThread


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

        # # Buffers begin
        # self.cw_dict = dict()
        # self.resp_buffer = list()
        # self.vibro_buffer = list()
        # self.msg_list = list()
        # self.json_list = list()
        # # Buffers end

        # For receive vibro data begin
        # self.per_thread = PerThread()
        self.tx_rx_thread.per_signal.connect(self.per_result)
        # For receive vibro data end

        # Timer begin
        self.vibro_timer = QTimer()
        self.vibro_timer.setInterval(60000)
        self.vibro_timer.timeout.connect(self.measure_vibro)
        # Timer end

        self.proc_thread_slave.start()

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
        self.reboot_dev(True)

    def slave_start_cw(self):
        self.set_cw_mode("CW_ON", True)

    def slave_stop_cw(self):
        self.set_cw_mode("CW_ON", True)

    def slave_start_per(self):
        self.tx_rx_thread.num_packet = self.spinBoxSlavePER.value()
        self.tx_rx_thread.per = True
        self.vibro_timer.stop()
        self.listWidgetPER.addItem("Transfer is started")

    def slave_get_info(self):
        self.get_dev_info(True)
        self.get_join_key(True)

    def slave_get_data(self):
        self.get_adxl345(True)
        self.get_ds18b20(True)
        self.get_mcu_adc(True)

    def slave_get_vibro(self):
        self.get_vibro(True)

    def slave_get_all(self):
        self.slave_get_info()
        self.slave_get_data()
        self.slave_get_vibro()

    def showEvent(self, event):
        self.proc_thread_master.start()
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
            self.tx_rx_thread.sock.close()
            self.close_threads()
            self.vibro_timer.stop()
            event.accept()
        else:
            event.ignore()

    def per_result(self, result):
        self.listWidgetPER.addItem(result)
        self.vibro_timer.start()


def main():
    dvt_app = QtWidgets.QApplication(sys.argv)
    dvt_app.setPalette(DarkPalette())
    dvt_win = DvtApp()
    dvt_win.show()
    dvt_app.exec_()


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
