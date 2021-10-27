import serv
import sys
import socket
import queue
import serial.tools.list_ports

from msg_window_cls import MsgWindow, TabIndex
from PyQt5 import QtWidgets
from MyThreads import TimeThread, ReaderSocketThread


class ServWindow(QtWidgets.QMainWindow, serv.Ui_MainWindow, QtWidgets.QMessageBox):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

        # Error dialog begin
        self.error_dialog = QtWidgets.QMessageBox()  # create error dialog object
        self.error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
        self.error_dialog.setWindowTitle("Error")
        # Error dialog end

        # For GUI begin
        self.createMessage.clicked.connect(self.create_message)  # methods for sending created message to client
        # fill combo box field
        self.fill_combo_box(["Choice message", "devinfo_req", "mcu_telemetry_req", "ds18b20_req", "adx1345_req",
                             "vibro_rms_req", "reboot", "cw_req", "join_key_req", "vibro_req"])
        # For GUI end

        # For socket begin
        self.socketIsConnect = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP
        self.sock_port = 0  # socket port
        self.conn = 0
        # For socket end

        # Threads begin
        self.queue_time = queue.Queue()
        self.reader_thread = ReaderSocketThread(self)  # Threads for reading from socke
        self.time_thread = TimeThread(self, self.queue_time)  # t
        self.threads_list = [self.reader_thread, self.time_thread]
        # Threads end

        # Other window begin
        self.messagesWindow = MsgWindow(self.queue_time, self.sock, self.reader_thread)
        # Other window end

    # This function filling combo box items
    # arr - array of with elements combo box items
    # combo_box - select combo box which will be filling
    def fill_combo_box(self, arr):
        for i in arr:
            self.choiceMessage.addItem(str(i))

    # This function returns condition of GUI fields
    # return value is list of elements GUI fields
    # value has GUI fields order
    def read_param(self):
        self.sock_port = self.socketPort.text()  # get socket port number
        if not self.sock_port:
            self.error_dialog.setText("Please fill in all fields")
            self.error_dialog.exec_()
            self.createMessage.setEnabled(True)
            return 1
        return 0

    def select_msg_param(self):
        msg = self.choiceMessage.currentText()  # selected message
        if msg == "Choice message":
            self.error_dialog.setText("Please select message")
            self.listWidget.addItem("Please select message")
            self.error_dialog.show()
            self.createMessage.setEnabled(True)
            return 1
        elif msg == "devinfo_req":
            self.open_tab(TabIndex.DEV_INFO)
            return 0
        elif msg == "mcu_telemetry_req":
            self.open_tab(TabIndex.MCU_TELEMETRY)
            return 0
        elif msg == "ds18b20_req":
            self.open_tab(TabIndex.DS18B20)
            return 0
        elif msg == "adx1345_req":
            self.open_tab(TabIndex.ADXL345)
            return 0
        elif msg == "reboot":
            self.open_tab(TabIndex.REBOOT)
            return 0
        elif msg == "cw_req":
            self.open_tab(TabIndex.CW_MODE)
            return 0
        elif msg == "join_key_req":
            self.open_tab(TabIndex.JOIN_KEY)
        elif msg == "vibro_req":
            self.open_tab(TabIndex.VIBRO)
            return 0

    # This function is callback on button pushing
    # here launched threading
    # here connect socket
    def create_message(self):
        self.createMessage.setEnabled(False)  # disable button while message sending
        if not self.socketIsConnect:  # check socket connection
            if self.read_param():
                self.listWidget.addItem("Please fill in all fields")
                self.createMessage.setEnabled(True)
                return 1
            # if self.serial_connect():
            #     return 1
            if self.sock_connect():
                return 1
            self.socketPort.setEnabled(False)  # block fields with input socket port
        self.time_thread.start()  # start time thread
        if self.select_msg_param() == 1:
            return 1

    # Socket connection begin
    # This function connected to socket port
    def sock_connect(self):
        port = int(self.sock_port)
        try:
            self.sock.connect(('localhost', port))
        except socket.error:
            self.error_dialog.setText("Address " + str(port) + " already use")
            self.listWidget.addItem("Please, change the socket port")
            self.createMessage.setEnabled(True)
            return 1
        self.listWidget.addItem("Socket connected to port: " + str(port))  # + str(', ') + str(addr))
        self.socketIsConnect = True
        self.reader_thread.start()
        return 0
    # Socket connection end

    def open_tab(self, index):
        if not self.messagesWindow.isOpen:
            self.messagesWindow.isOpen = True
            self.messagesWindow.show()
        self.messagesWindow.enable_tab(index)
        self.createMessage.setEnabled(True)

    # Close threads begin
    def close_threads(self):
        for thread in self.threads_list:
            thread.quit()
    # Close threads end

    def closeEvent(self, event):
        close_dialog = QtWidgets.QMessageBox.question(
            self, "Message",
            "Are you sure you want to quit?",
            QtWidgets.QMessageBox.Close | QtWidgets.QMessageBox.Cancel
        )
        if close_dialog == QtWidgets.QMessageBox.Close:
            self.close_threads()
            event.accept()
        else:
            event.ignore()


def main():
    serv_app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    serv_win = ServWindow()  # Создаём объект класса serv_app
    serv_win.show()  # Показываем окно
    serv_app.exec_()  # и запускаем приложение
    serv_win.sock.close()  # closing socket connection


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
