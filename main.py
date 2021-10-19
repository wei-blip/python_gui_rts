import serv
import sys
import socket
import time
import queue
import serial

from msg_window_cls import MsgWindow, TabIndex
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
        # For GUI end

        # For socket and serial begin
        self.socketIsConnect = False
        self.ser = serial.Serial()
        self.sock_port = 0  # socket port
        self.ser_port = 0  # serial port
        self.ser_port_baudrate = 0  # baudrate serial port
        self.sock = socket.socket()
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
    def read_param(self):
        self.sock_port = self.socketPort.text()  # get socket port number
        self.ser_port = self.serialPort.text()  # get serial port number
        self.ser_port_baudrate = self.baudrateSerialPort.text()  # get serial port baudrate
        if (not self.sock_port) or (not self.ser_port) or (not self.ser_port_baudrate):
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
            if self.serial_connect():
                return 1
            if self.sock_connect():
                return 1
            self.messagesWindow.ser_port = self.ser
            self.serialPort.setEnabled(False)  # block fields with input serial port
            self.socketPort.setEnabled(False)  # block fields with input socket port
            self.baudrateSerialPort.setEnabled(False)  # block fields with input baudrate serial port
            self.socketIsConnect = True

        self.sock_thread.run = True
        self.scan_thread.run = True
        self.scan_thread.start()  # start scan thread
        self.sock_thread.start()  # start sock thread

        if self.select_msg_param() == 1:
            return 1

# This function connected to socket port
    def sock_connect(self):
        port = int(self.sock_port)
        # self.sock = socket.socket()
        try:
            self.sock.bind(('', port))
        except socket.error:
            self.error_dialog.setText("Address " + str(port) + " already use")
            self.listWidget.addItem("Please, change the socket port")
            return 1
        self.sock.listen(5)
        self.conn, addr = self.sock.accept()
        self.listWidget.addItem("socket connected: " + str(port) + str(', ') + str(addr))
        return 0

    def serial_connect(self):
        try:
            # init serial port: port_number=args.port, baudrate = args.baud, timeout = 1 sec
            self.ser = serial.serial_for_url(self.ser_port, int(self.ser_port_baudrate), timeout=1)
        except serial.SerialException:
            self.error_dialog.setText("Serial port " + str(self.ser_port) + " not found!")
            self.error_dialog.show()
            self.createMessage.setEnabled(True)
            return 1
            # print('\033[91mError: Port %s not found!' % self.ser_port, file=sys.stderr)
            # sys.exit(1)
        except ValueError:
            self.error_dialog.setText("Incorrect serial port parameters!")
            self.error_dialog.show()
            self.createMessage.setEnabled(True)
            return 1
            # print('\033[91mError: Incorrect serial port parameters!', file=sys.stderr)
            # sys.exit(1)
        return 0

    def open_tab(self, index):
        if not self.messagesWindow.isOpen:
            self.messagesWindow.isOpen = True
            self.messagesWindow.show()
        self.messagesWindow.enable_tab(index)
        self.createMessage.setEnabled(True)


def main():
    serv_app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    serv_win = ServWindow()  # Создаём объект класса serv_app
    serv_win.show()  # Показываем окно
    serv_app.exec_()  # и запускаем приложение
    serv_win.sock.close()  # closing socket connection
    serv_win.ser.close()  # closing serial port connection


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
