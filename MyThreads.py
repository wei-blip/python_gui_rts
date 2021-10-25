from PyQt5.QtCore import QThread
import time
# from msg_window_cls import q


# Thread for sending and receiving message from socket maybe unused ???
class SockThread(QThread):
    def __init__(self, serv_win, queue, parent=None):
        QThread.__init__(self, parent)
        self.queue = queue
        self.serv_win = serv_win
        self.run = False

    def run(self):
        while self.run:
            # self.serv_win.listWidget.addItem("socket thread")
            # time.sleep(0.5)
            pass


# Thread to display time begin
class TimeThread(QThread):
    def __init__(self, serv_win, queue, parent=None):
        QThread.__init__(self, parent)
        self.serv_win = serv_win
        self.queue = queue

    def run(self):
        while True:
            if not self.queue.empty():
                self.serv_win.listWidget.addItem(self.queue.get_nowait())
                self.queue.task_done()
            time.sleep(1)
# Thread to display time end


# Thread for scanning GUI maybe unused ???
class ScanThread(QThread):
    def __init__(self, serv_win, queue, parent=None):
        QThread.__init__(self, parent)
        self.serv_win = serv_win
        self.queue = queue
        self.run = False

    def run(self):
        while self.run:
            # self.serv_win.listWidget.addItem("scan thread")
            # time.sleep(1)
            pass


# class ReceivingFromQueueThread(QThread):
#     def __init__(self, win, parent=None):
#         QThread.__init__(self, parent)
#         self.win = win
#
#     def run(self):
#         while True:
#             if not q.empty():
#                 if self.win.current_msg == 'devinfo':
#                     self.win.getDevInfo.setEnabled(True)
#                     self.win.listWidgetDevInfo.addItem(q.get_nowait())
#                     self.win.queue_time.put_nowait("Message devinfo is received " + self.win.get_time())
#                 elif self.win.current_msg == 'ds18b20':
#                     self.win.getDs18b20.setEnabled(True)
#                     self.win.listWidgetDs18b20.addItem(q.get_nowait())
#                     self.win.queue_time.put_nowait("Message ds18b20 is received " + self.win.get_time())
#                 elif self.win.current_msg == 'reboot_dev':
#                     self.win.rebootDevice.setEnabled(True)
#                     self.win.listWidgetReboot.addItem(q.get_nowait())
#                     self.win.queue_time.put_nowait("Message reboot is received " + self.win.get_time())
#                 q.task_done()


class ReaderSocketThread(QThread):
    def __init__(self, win, parent=None):
        QThread.__init__(self, parent)
        self.win = win
        self.buf = bytearray()

    def run(self):
        while True:
            try:
                data = self.win.transport.recv(1024)
                if data:
                    self.buf.extend(data)
                    while self.win.TERMINATOR in self.buf:
                        packet, self.buf = self.buf.split(self.win.TERMINATOR, 1)
                        self.win.handle_packet(packet)
                    if self.win.current_msg == 'devinfo':
                        # self.win.listWidget.addItem("Message devinfo is received " + self.win.messagesWindow.get_time())
                        self.win.listWidgetDevInfo.addItem(self.win.output_data)
                        self.win.getDevInfo.setEnabled(True)
            except:
                pass