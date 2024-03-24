import sys

from notifypy import Notify
from PyQt5.QtCore import QObject, QThread
from PyQt5.QtWidgets import QApplication

from chat import Chat
from pc import Client
from server import Server
from tray import Tray


class MyWindow(QObject):
    def __init__(self):
        super().__init__()

        self.Chat = Chat()
        self.show_chat()
        self.server_function()
        self.tray_function()
        self.client_function()

    def client_function(self):
        self.client_thread = QThread()
        self.client = Client()
        self.Chat.message_signal.connect(self.client.bridge)
        self.client.recv_signal.connect(self.Chat.show_msg)
        self.client.moveToThread(self.client_thread)
        self.client_thread.started.connect(self.client.run)
        self.client_thread.finished.connect(self.client_thread.deleteLater)
        self.client_thread.start()

    def server_function(self):
        self.server_thread = QThread()
        self.server = Server()
        self.server.message_signal.connect(lambda msg: self.show_msg(msg))
        self.server.moveToThread(self.server_thread)
        self.server_thread.started.connect(self.server.run)
        self.server_thread.finished.connect(self.server_thread.deleteLater)
        self.server_thread.start()

    def tray_function(self):
        self.icon_thread = QThread()
        self.tray = Tray()
        self.tray.exit_signal.connect(lambda: app.quit())
        self.tray.icon_clicked.connect(self.show_chat)
        self.tray.moveToThread(self.icon_thread)
        self.icon_thread.started.connect(self.tray.run)
        self.icon_thread.finished.connect(self.icon_thread.deleteLater)
        self.icon_thread.start()

    def show_msg(self, msg):
        notification = Notify()
        notification.title = msg[0]
        notification.message = msg[1]
        notification.icon = "./assets/clipwarp.png"
        notification.send()

    def show_chat(self):
        self.Chat.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = MyWindow()
    sys.exit(app.exec_())
