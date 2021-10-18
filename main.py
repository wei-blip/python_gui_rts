import serv
import sys
import socket
import time
import queue

from msg_window_cls import MsgWindow, TabIndex
# import msg_window_cls
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread


# Thread for sending and receiving message from socket
class SockThread(QThread):
    def __init__(self, serv_win, queue, parent=None):
        QThread.__init__(self, parent)
        self.queue = queue
        self.serv_win = serv_win
        self.run = False

    def run(self):
         while self.run:
            self.serv_win.listWidget.addItem("socket thread")
            time.sleep(0.5)


# Thread for scanning GUI
class ScanThread(QThread):
    def __init__(self, serv_win, queue, parent=None):
        QThread.__init__(self, parent)
        self.serv_win = serv_win
        self.queue = queue
        self.run = False

    def run(self):
         while self.run:
            self.serv_win.listWidget.addItem("scan thread")
            # if not self.queue.empty():
            #     data = self.queue.get_nowait()
            #     rx_win.listWidget.addItem(("Data recv: " + str(data)))  # if we have a data, we print data on window.
            # # if not self.queue.empty():
            # #     data = self.queue.get_nowait()
            # #     rx_win.listWidget.addItem(("Data recv: " + data))  # if we have a data, we print data on window.
            time.sleep(1)


class ServWindow(QtWidgets.QMainWindow, serv.Ui_MainWindow, QtWidgets.QMessageBox):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

        # Other window begin
        self.windowIsOpen = False
        self.messagesWindow = MsgWindow()  # if window not opened, created new MsgWindow object
        # Other window end

        # Error dialog begin
        self.error_dialog = QtWidgets.QMessageBox()  # create error dialog object
        self.error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
        self.error_dialog.setWindowTitle("Error")
        # Error dialog end

        # For GUI begin
        self.createMessage.clicked.connect(self.create_message)  # methods for sending created message to client
        choice_message_arr = ["Choice message", "devinfo_req", "mcu_telemetry_req", "ds18b20_req", "adx1345_req",
                              "vibro_rms_req", "reboot", "cw_req", "join_key_req"]
        self.fill_combo_box(choice_message_arr)  # fill combo box field
        self.serialPort.setPlaceholderText("Serial port")
        self.socketPort.setPlaceholderText("Socket port")
        # For GUI end

        # For socket and serial begin
        self.socketIsConnect = False
        self.sock_port = 0 # socket port
        self.ser_port = 0  # serial port
        self.sock = 0
        self.conn = 0
        # For socket end

        # For threading begin
        self.queue = queue.Queue()
        self.scan_thread = ScanThread(self, self.queue)
        self.sock_thread = SockThread(self, self.queue)
        # For threading end

# This function filling combo box items
# arr - array of with elements combo box items
# combo_box - select combo box which will be filling
    def fill_combo_box(self, arr):
        for i in arr:
            self.choiceMessage.addItem(str(i))
            print(i)

# This function returns condition of GUI fields
# return value is list of elements GUI fields
# value has GUI fields order
    def get_sock_ser_ports(self):
        port = self.socketPort.text()  # get socket port
        ser = self.serialPort.text()  # get serial port
        if (not port) or (not ser):
            self.error_dialog.setText("Please fill in all fields")
            self.error_dialog.exec_()
            self.createMessage.setEnabled(True)
            return 1
        arr = [port, ser]
        # msg = self.choiceMessage.currentText()
        # enm = self.enumField.currentText()
        # checkbox = self.BoolField.isChecked()  # get value from check box
        # integer = self.integerField.value()  # get value from integer spin box
        # dbl = self.doubleField.value()  # get value from double spin box
        # str = self.stringField.text()  # get value from string
        # arr = [msg, enm, checkbox, integer, dbl, str]
        return arr

    def select_msg_param(self):
        msg = self.choiceMessage.currentText()  # selected message
        if msg == "Choice message":
            self.error_dialog.setText("Please select message")
            self.listWidget.addItem("Please select message")
            return 1
        elif msg == "devinfo_req":
            self.check_window()
            self.messagesWindow.enable_tab(TabIndex.DEV_INFO)
            self.createMessage.setEnabled(True)
            return 0
        elif msg == "mcu_telemetry_req":
            self.check_window()
            self.messagesWindow.enable_tab(TabIndex.MCU_TELEMETRY)
            self.createMessage.setEnabled(True)
            return 0
        elif msg == "ds18b20_req":
            self.check_window()
            self.messagesWindow.enable_tab(TabIndex.DS18B20)
            self.createMessage.setEnabled(True)
            return 0
        elif msg == "adx1345_req":
            self.check_window()
            self.messagesWindow.enable_tab(TabIndex.ADXL345)
            self.createMessage.setEnabled(True)
            return 0
        elif msg == "vibro_rms_req":
            self.check_window()
            self.createMessage.setEnabled(True)
            return 0
        elif msg == "reboot":
            self.check_window()
            self.messagesWindow.enable_tab(TabIndex.REBOOT)
            self.createMessage.setEnabled(True)
            return 0
        elif msg == "cw_req":
            self.check_window()
            self.messagesWindow.enable_tab(TabIndex.CW_MODE)
            self.createMessage.setEnabled(True)
            return 0
        elif msg == "join_key_req":
            self.check_window()
            self.messagesWindow.enable_tab(TabIndex.JOIN_KEY)
            self.createMessage.setEnabled(True)
            return 0

# This function is callback on button pushing
# here launched threading
# here connect socket
    def create_message(self):
        self.createMessage.setEnabled(False)  # disable button while message sending

        if not self.socketIsConnect:  # check socket connection
            self.socketIsConnect = True
            arr = self.get_sock_ser_ports()
            if arr == 1:
                self.listWidget.addItem("Please fill in all fields")
                return 1
            self.sock_port = arr[0]
            self.ser_port = arr[1]
            self.sock_connect()
            self.serialPort.setEnabled(False)  # block fields with input serial port
            self.socketPort.setEnabled(False)  # block fields with input socket port

        self.sock_thread.run = True
        self.scan_thread.run = True
        self.scan_thread.start()  # start scan thread
        self.sock_thread.start()  # start sock thread

        if self.select_msg_param() == 1:
            return 1

# This function connected to socket port
    def sock_connect(self):
        port = int(self.sock_port)
        self.sock = socket.socket()
        try:
            self.sock.bind(('', port))
        except socket.error:
            self.listWidget.addItem("Address " + str(port) + " already used")
            sys.exit(1)
        self.sock.listen(5)
        self.conn, addr = self.sock.accept()
        self.listWidget.addItem("socket connected: " + str(port) + str(',') + str(addr))

    def check_window(self):
        if not self.windowIsOpen:
            self.windowIsOpen = True
            self.messagesWindow.show()


def main():
    serv_app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    serv_win = ServWindow()  # Создаём объект класса serv_app
    serv_win.show()  # Показываем окно
    serv_app.exec_()  # и запускаем приложение
    serv_win.sock.close()   # closing socket connection


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
