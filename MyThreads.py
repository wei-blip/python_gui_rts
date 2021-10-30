from PyQt5.QtCore import QThread
import time
import msg_window_cls


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


class ReaderSocketThread(QThread):
    def __init__(self, win, parent=None):
        QThread.__init__(self, parent)
        self.win = win
        self.buf = bytearray()

    def run(self):
        while self.win.socketIsConnect:
            try:
                data = self.win.transport.recv(1024)
                if data:
                    self.buf.extend(data)
                    while self.win.TERMINATOR in self.buf:
                        packet, self.buf = self.buf.split(self.win.TERMINATOR, 1)
                        self.win.handle_packet(packet)
                    # if self.win.messagesWindow.current_msg == 'devinfo':
                    #     self.win.listWidget.addItem("Message devinfo is received " + msg_window_cls.get_time())
                    #     self.win.messagesWindow.listWidgetDevInfo.addItem(self.win.messagesWindow.output_data)
                    #     self.win.messagesWindow.getDevInfo.setEnabled(True)
                    # elif self.win.messagesWindow.current_msg == 'ds18b20':
                    #     self.win.listWidget.addItem("Message DS18B20 is received " + msg_window_cls.get_time())
                    #     self.win.messagesWindow.listWidgetDs18b20.addItem(self.win.messagesWindow.output_data)
                    #     self.win.messagesWindow.getDs18b20.setEnabled(True)
                    # elif self.win.messagesWindow.current_msg == 'join_key':
                    #     self.win.listWidget.addItem("Message join key is received " + msg_window_cls.get_time())
                    #     self.win.messagesWindow.listWidgetJoinKey.addItem(self.win.messagesWindow.output_data)
                    #     self.win.messagesWindow.getDs18b20.setEnabled(True)
                    # elif self.win.messagesWindow.current_msg == 'adxl345':
                    #     self.win.listWidget.addItem("Message ADXL345 is received " + msg_window_cls.get_time())
                    #     self.win.messagesWindow.listWidgetAdxl345.addItem(self.win.messagesWindow.output_data)
                    #     self.win.messagesWindow.getAdxl345.setEnabled(True)
                    # elif self.win.messagesWindow.current_msg == 'vibro':
                    #     self.win.listWidget.addItem("Message vibro is received " + msg_window_cls.get_time())
                    #     self.win.messagesWindow.listWidgetVibro.addItem(self.win.messagesWindow.output_data)
                    #     self.win.messagesWindow.getVibro.setEnabled(True)
            except:
                continue


# class MasterVibroThread(QThread):
#     def __init__(self, win, parent=None):
#         QThread.__init__(self, parent)
#         self.win = win
#
#     def run(self):