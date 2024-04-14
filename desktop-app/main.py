import sys

from notifypy import Notify
from PyQt5.QtCore import QObject, QThread
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QSystemTrayIcon

from chat import Chat
from db import Database
from flaskapi import FlaskAPI
from pc import Client
from serve import Serve
from server import Server
from ui import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_connections()
        self.setStyleSheet(self.stylesheet())
        # self.setFixedSize(612, 392)
        self.set_window_icon("./assets/cw.ico")
        self.setup_system_tray()

    def init_ui(self):
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    def setup_connections(self):
        self.start_api()
        self.serve_function()
        self.server_function()
        self.db_function()
        self.Chat = Chat(self.ui)
        self.client_function()

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
        self.Chat.clips_fetched.connect(self.ui.load_clips)
        self.ui.itemDeleted.connect(self.Chat.delete_clip)
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

    def show_msg(self, msg):
        notification = Notify()
        notification.title = msg[0]
        notification.message = msg[1]
        notification.icon = "./assets/cw.svg"
        notification.send()

    def db_function(self):
        self.connection = Database().create_db()

    def serve_function(self):
        self.serve_thread = QThread()
        self.serve = Serve()
        self.serve.moveToThread(self.serve_thread)
        self.serve_thread.started.connect(self.serve.start)
        self.serve_thread.start()

    def setup_system_tray(self):
        self.tray = QSystemTrayIcon(self)
        if self.tray.isSystemTrayAvailable():
            self.tray.setIcon(self.windowIcon())
            ctmenu = QMenu()
            actionshow = ctmenu.addAction("Show/Hide")
            actionshow.triggered.connect(
                lambda: self.hide() if self.isVisible() else self.show()
            )
            actionquit = ctmenu.addAction("Quit")
            actionquit.triggered.connect(self.close)
            self.tray.setContextMenu(ctmenu)

            # Connect the activated signal to a slot
            self.tray.activated.connect(self.trayActivated)

            self.tray.show()

    def trayActivated(self, reason):
        # Check if the reason for activation is a left mouse button click
        if reason == QSystemTrayIcon.Trigger:
            # Show or hide the main window depending on its visibility
            if self.isVisible():
                self.hide()
            else:
                self.show()

    def stylesheet(self):
        return """
                QPlainTextEdit, QMainWindow, QFrame, QLabel, QPushButton, VerticalTabWidget {
                    background-color: #333;
                    color: #FFF;
                }
                QPlainTextEdit,TabBar, QListWidget {
                    background-color: #4d4d4d;
                    color: #FFF;
                }
                TabBar::tab {
                    width: 32px;
                    height: 139px; 
                }
                QListWidget::item {
                    padding: 5px;            
                }

            """

    def set_window_icon(self, icon_path):
        icon = QIcon(icon_path)
        self.setWindowIcon(icon)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
