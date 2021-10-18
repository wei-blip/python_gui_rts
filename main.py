import serv
import sys
import socket
import time
import queue


from devinfo_window import DevInfoWindow
from mcu_telemetry_window import McuTelemetryWindow
from join_key_window import JoinKeyWindow
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
        self.devinfo_win = 0
        self.mcu_telemetry_win = 0
        self.join_key_win = 0
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
        self.fill_combo_box(choice_message_arr, "choice message")  # fill combo box field
        self.serialPort.setPlaceholderText("Serial port")
        self.socketPort.setPlaceholderText("Socket port")
        # enum_arr = ["CW command enumeration", "CW_ON", "CW_OFF", "CW_FORM_START", "CW_FORM_FINISH"]
        # self.fill_combo_box(enum_arr, "enum")
        # For GUI end

        # For socket and serial begin
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
    def fill_combo_box(self, arr, combo_box):
        if combo_box == "choice message":
            for i in arr:
                self.choiceMessage.addItem(str(i))
                print(i)
        # elif combo_box == "enum":
        #     for i in arr:
        #         self.enumField.addItem(str(i))
        #         print(i)

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
            self.devinfo_win = DevInfoWindow()  # new DevInfoWindow object
            self.devinfo_win.show()
            return 0
        elif msg == "mcu_telemetry_req":
            self.mcu_telemetry_win = McuTelemetryWindow()  # new McuTelemetryWindow object
            self.mcu_telemetry_win.show()
            return 0
        elif msg == "ds18b20_req":
            return 0
        elif msg == "adx1345_req":
            return 0
        elif msg == "vibro_rms_req":
            return 0
        elif msg == "reboot":
            return 0
        elif msg == "cw_req":
            return 0
        elif msg == "join_key_req":
            self.join_key_win = JoinKeyWindow()  # new JoinKeyWindow object
            self.join_key_win.show()
            return 0

# This function is callback on button pushing
# here launched threading
# here connect socket
    def create_message(self):
        self.createMessage.setEnabled(False)  # disable button while message sending
        # self.block_fields()  # disable all fields while message sending
        arr = self.get_sock_ser_ports()
        if arr == 1:
            self.listWidget.addItem("Please fill in all fields")
            return 1
        self.sock_port = arr[0]
        self.ser_port = arr[1]
        self.sock_connect()
        self.sock_thread.run = True
        self.scan_thread.run = True
        self.scan_thread.start()  # start scan thread
        self.sock_thread.start()  # start sock thread
        if self.select_msg_param() == 1:
            return 1

# This function blocked GUI fields that user couldn't change them before message request
#     def block_fields(self):
        # # disable all fields while message sending
        # self.stringField.setEnabled(False)
        # self.integerField.setEnabled(False)
        # self.doubleField.setEnabled(False)
        # self.BoolField.setEnabled(False)
        # self.choiceMessage.setEnabled(False)
        # self.enumField.setEnabled(False)

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

    # def stop_recv(self):
    #     self.scan_thread.run = False
    #     self.sock_thread.sock_connect = False
    #     rx_win.listWidget.addItem("receiving stopped")



def main():
    serv_app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    serv_win = ServWindow()  # Создаём объект класса serv_app
    serv_win.show()  # Показываем окно
    serv_app.exec_()  # и запускаем приложение
    serv_win.sock.close()   # closing socket connection

if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()