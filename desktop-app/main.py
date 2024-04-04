import sys

from notifypy import Notify
from PyQt5.QtCore import QObject, QThread
from PyQt5.QtWidgets import QApplication

from chat import Chat
from db import Database
from flaskapi import FlaskAPI
from pc import Client
from server import Server
from tray import Tray


class MyWindow(QObject):
    def __init__(self):
        super().__init__()

        self.start_api()
        self.Chat = Chat()
        self.show_chat()
        self.server_function()
        self.tray_function()
        self.client_function()
        self.db_function()

    def start_api(self):
        self.thread = QThread()
        self.api = FlaskAPI()
        self.api.moveToThread(self.thread)
        self.thread.started.connect(self.api.start)
        self.thread.start()

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
        self.tray = Tray()

    def show_msg(self, msg):
        notification = Notify()
        notification.title = msg[0]
        notification.message = msg[1]
        notification.icon = "./assets/clipwarp.png"
        notification.send()

    def show_chat(self):
        self.Chat.show()

    def db_function(self):
        self.connection = Database().create_db()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    window = MyWindow()
    sys.exit(app.exec_())
