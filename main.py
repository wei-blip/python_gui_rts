from msg_window_cls import DvtReq
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer, pyqtSignal
from rs_0006_0_icp_pb2 import *
from darktheme.widget_template import DarkPalette
from MyThreads import ProcThreads
from enum import IntEnum


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

        # Dialogs begin
        self.error_dialog = QtWidgets.QMessageBox()  # create error dialog object
        self.error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
        self.error_dialog.setWindowTitle("Error")

        self.warning_dialog = QtWidgets.QMessageBox()
        self.warning_dialog.setIcon(QtWidgets.QMessageBox.Warning)
        self.warning_dialog.setWindowTitle("Warning")
        # Dialogs end

        self.init_tables()

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
        self.pushButtonMessageStatusClear.clicked.connect(self.clear_message_status)
        # Callbacks slave end

        # My signal callbacks begin
        self.tx_rx_thread.per_signal.connect(self.per_result)
        self.tx_rx_thread.socket_timeout_signal.connect(self.socket_timeout)
        self.tx_rx_thread.queue_full_signal.connect(self.queue_warning)
        self.proc_thread_slave.fill_table_signal.connect(self.fill_table)
        self.proc_thread_master.fill_table_signal.connect(self.fill_table)
        # My signal callbacks end

        # Timer begin
        self.vibro_timer = QTimer()
        self.vibro_timer.setInterval(60000)
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
        self.tx_rx_thread.start()

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
        self.master_get_info()
        self.master_get_vibro()
        self.vibro_timer.start()
        event.accept()

    def measure_vibro(self):
        self.vibro_timer.stop()
        self.master_get_vibro()
        self.vibro_timer.start()

    def clear_message_status(self):
        self.listWidgetMessageStatus.clear()

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
        self.fill_table_field(self.tableWidgetSlaveRadio,
                              TableRow.FOURTH_ROW, TableColumn.FIRST_COLUMN, (result / self.tx_rx_thread.num_packet))
        self.listWidgetPER.addItem(result)
        self.vibro_timer.start()

    def socket_timeout(self):
        self.error_dialog.setText("Socket timeout!\n"
                                  "Maybe you are don't connect UART?")
        self.error_dialog.show()

    def queue_warning(self, text):
        self.warning_dialog.setText(text)
        self.warning_dialog.show()

    def init_tables(self):
        # slave info table
        for row in range(TableRow.FIRST_ROW, TableRow.FIFTH_ROW):
            self.fill_table_field(self.tableWidgetSlaveInfo, row, TableColumn.FIRST_COLUMN, "Not received")
        # slave data table
        for row in range(TableRow.FIRST_ROW, TableRow.SIXTH_ROW):
            self.fill_table_field(self.tableWidgetSlaveData, row, TableColumn.FIRST_COLUMN, "Not received")
        # slave radio table
        for row in range(TableRow.FIRST_ROW, TableRow.FIFTH_ROW):
            self.fill_table_field(self.tableWidgetSlaveRadio, row, TableColumn.FIRST_COLUMN, "Not received")
        # slave vibro table
        for row in range(TableRow.FIRST_ROW, TableRow.FOURTH_ROW):
            self.fill_table_field(self.tableWidgetSlaveVibro, row, TableColumn.FIRST_COLUMN, "Not received")

    def fill_table(self, fill_table):
        if fill_table.status.thread == ProcThreads.MASTER:
            if fill_table.status.msg_type == 'devinfo':
                devinfo_elem = fill_table.data.get("resp").get("devinfo")
                self.fill_devinfo_field_from_master_info_table(devinfo_elem)
            elif fill_table.status.msg_type == 'joinKey':
                self.fill_join_key_field_from_master_info_table(fill_table.data)
            elif fill_table.status.msg_type == 'ds18b20':
                self.fill_ds18b20_field_from_master_info_table(fill_table.data)
            elif fill_table.status.msg_type == 'mcuAdc':
                self.fill_mcu_adc_field_from_master_info_table(fill_table.data)
            elif fill_table.status.msg_type == 'vibro':
                vrms = fill_table.data.get("resp").get("vibro").get("vrms")
                self.fill_vibro_field_from_master_vibro_table(vrms)
            elif fill_table.status.msg_type == 'adxl345':
                acc_g = fill_table.data.get("resp").get("adxl345").get("accG")
                self.fill_adxl345_field_from_master_vibro_table(acc_g)
        elif fill_table.status.thread == ProcThreads.SLAVE:
            if fill_table.status.msg_type == 'devinfo':
                devinfo_elem = fill_table.data.get("resp").get("devinfo")
                self.fill_devinfo_field_from_slave_info_table(devinfo_elem)
            elif fill_table.status.msg_type == 'joinKey':
                self.fill_join_key_field_from_slave_info_table(fill_table.data)
                self.fill_radio_table(fill_table.data.get("resp"))
            elif fill_table.status.msg_type == 'ds18b20':
                self.fill_ds18b20_field_from_slave_data_table(fill_table.data)
            elif fill_table.status.msg_type == 'mcuAdc':
                self.fill_mcu_adc_field_from_slave_data_table(fill_table.data)
            elif fill_table.status.msg_type == 'vibro':
                vrms = fill_table.data.get("resp").get("vibro").get("vrms")
                self.fill_vibro_field_from_slave_vibro_table(vrms)
                self.fill_radio_table(fill_table.data.get("resp"))
            elif fill_table.status.msg_type == 'adxl345':
                acc_g = fill_table.data.get("resp").get("adxl345").get("accG")
                self.fill_adxl345_field_from_slave_data_table(acc_g)
                self.fill_radio_table(fill_table.data.get("resp"))

    # This methods for filling table into window
    # Methods for filling table fields begin
    def fill_devinfo_field_from_master_info_table(self, json_dict):
        table = self.tableWidgetMasterInfo
        self.fill_table_field(table, TableRow.FIRST_ROW, TableColumn.FIRST_COLUMN, json_dict.get("devEui"))
        self.fill_table_field(table, TableRow.SECOND_ROW, TableColumn.FIRST_COLUMN, json_dict.get("family"))
        self.fill_table_field(table, TableRow.THIRD_ROW, TableColumn.FIRST_COLUMN, json_dict.get("version"))

    def fill_devinfo_field_from_slave_info_table(self, json_dict):
        table = self.tableWidgetSlaveInfo
        self.fill_table_field(table, TableRow.FIRST_ROW, TableColumn.FIRST_COLUMN, json_dict.get("devEui"))
        self.fill_table_field(table, TableRow.SECOND_ROW, TableColumn.FIRST_COLUMN, json_dict.get("family"))
        self.fill_table_field(table, TableRow.THIRD_ROW, TableColumn.FIRST_COLUMN, json_dict.get("version"))

    def fill_join_key_field_from_master_info_table(self, json_dict):
        self.fill_table_field(self.tableWidgetMasterInfo, TableRow.FOURTH_ROW, TableColumn.FIRST_COLUMN,
                              json_dict.get("resp").get("joinKey").get("joinKey"))

    def fill_join_key_field_from_slave_info_table(self, json_dict):
        self.fill_table_field(self.tableWidgetSlaveInfo, TableRow.FOURTH_ROW, TableColumn.FIRST_COLUMN,
                              json_dict.get("resp").get("joinKey").get("joinKey"))

    def fill_ds18b20_field_from_master_info_table(self, json_dict):
        self.fill_table_field(self.tableWidgetMasterInfo, TableRow.FIFTH_ROW, TableColumn.FIRST_COLUMN,
                              json_dict.get("resp").get("ds18b20").get("temp"))

    def fill_ds18b20_field_from_slave_data_table(self, json_dict):
        self.fill_table_field(self.tableWidgetSlaveData, TableRow.FOURTH_ROW, TableColumn.FIRST_COLUMN,
                              json_dict.get("resp").get("ds18b20").get("temp"))

    def fill_mcu_adc_field_from_master_info_table(self, json_dict):
        self.fill_table_field(self.tableWidgetMasterInfo, TableRow.SIXTH_ROW, TableColumn.FIRST_COLUMN,
                              json_dict.get("resp").get("mcuAdc").get("mcuTemperature"))

    def fill_mcu_adc_field_from_slave_data_table(self, json_dict):
        self.fill_table_field(self.tableWidgetSlaveData, TableRow.FIFTH_ROW, TableColumn.FIRST_COLUMN,
                              json_dict.get("resp").get("mcuAdc").get("mcuTemperature"))

    def fill_vibro_field_from_master_vibro_table(self, json_dict):
        table = self.tableWidgetMasterVibro
        self.fill_table_field(table, TableRow.FIRST_ROW, TableColumn.FIRST_COLUMN, json_dict.get("x"))
        self.fill_table_field(table, TableRow.SECOND_ROW, TableColumn.FIRST_COLUMN, json_dict.get("y"))
        self.fill_table_field(table, TableRow.THIRD_ROW, TableColumn.FIRST_COLUMN, json_dict.get("z"))

    def fill_vibro_field_from_slave_vibro_table(self, json_dict):
        table = self.tableWidgetSlaveVibro
        self.fill_table_field(table, TableRow.FIRST_ROW, TableColumn.FIRST_COLUMN, json_dict.get("x"))
        self.fill_table_field(table, TableRow.SECOND_ROW, TableColumn.FIRST_COLUMN, json_dict.get("y"))
        self.fill_table_field(table, TableRow.THIRD_ROW, TableColumn.FIRST_COLUMN, json_dict.get("z"))

    def fill_adxl345_field_from_master_vibro_table(self, json_dict):
        table = self.tableWidgetMasterVibro
        self.fill_table_field(table, TableRow.FIRST_ROW, TableColumn.SECOND_COLUMN, json_dict.get("x"))
        self.fill_table_field(table, TableRow.SECOND_ROW, TableColumn.SECOND_COLUMN, json_dict.get("y"))
        self.fill_table_field(table, TableRow.THIRD_ROW, TableColumn.SECOND_COLUMN, json_dict.get("z"))

    def fill_adxl345_field_from_slave_data_table(self, json_dict):
        table = self.tableWidgetSlaveData
        self.fill_table_field(table, TableRow.FIRST_ROW, TableColumn.FIRST_COLUMN, json_dict.get("x"))
        self.fill_table_field(table, TableRow.SECOND_ROW, TableColumn.FIRST_COLUMN, json_dict.get("y"))
        self.fill_table_field(table, TableRow.THIRD_ROW, TableColumn.FIRST_COLUMN, json_dict.get("z"))

    def fill_radio_table(self, json_dict):
        table = self.tableWidgetSlaveRadio
        self.fill_table_field(table, TableRow.FIRST_ROW, TableColumn.FIRST_COLUMN, json_dict.get("rssi"))
        self.fill_table_field(table, TableRow.SECOND_ROW, TableColumn.FIRST_COLUMN, json_dict.get("snr"))
        self.fill_table_field(table, TableRow.THIRD_ROW, TableColumn.FIRST_COLUMN, json_dict.get("fei"))


def main():
    dvt_app = QtWidgets.QApplication(sys.argv)
    dvt_app.setPalette(DarkPalette())
    dvt_win = DvtApp()
    dvt_win.show()
    dvt_app.exec_()


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
