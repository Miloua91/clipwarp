import os
import sys

from notifypy import Notify
from PyQt5.QtCore import QObject, QThread
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QDesktopWidget,
    QMainWindow,
    QMenu,
    QSystemTrayIcon,
)


def resource_path(relative_path):
    if getattr(sys, "frozen", False):
        application_path = sys._MEIPASS
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(application_path, relative_path)


def load_ico(file_name):
    file_path = resource_path(os.path.join("assets", file_name))
    if not os.path.isfile(file_path):
        print(f"Cannot open file '{file_path}', because: No such file or directory")
    else:
        return file_path


from chat import Chat
from db import Database
from flaskapi import FlaskAPI
from pc import Client
from serve import Serve
from server import Server
from ui import Ui_MainWindow

os.environ["QT_QPA_PLATFORM"] = "xcb"


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.init_ui()
        self.start_api()
        self.setup_connections()
        self.setStyleSheet(self.stylesheet())
        self.setFixedSize(632, 392)
        self.show_and_center()
        self.set_window_icon(load_ico("cw.ico"))
        self.setup_system_tray()

    def init_ui(self):
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    def setup_connections(self):
        self.serve_function()
        self.server_function()
        self.db_function()
        self.Chat = Chat(self.ui)
        self.client_function()
        self.ui.settingSave.connect(self.restart_api)

    def restart_api(self):
        self.api.stop()
        self.thread.quit()
        self.thread.wait()

        self.start_api()

    def start_api(self):
        self.thread = QThread()
        self.api = FlaskAPI()
        self.api.moveToThread(self.thread)
        self.thread.started.connect(self.api.start)
        self.thread.start()

    def server_function(self):
        self.server_thread = QThread()
        self.server = Server()
        self.server.message_signal.connect(lambda msg: self.show_msg(msg))
        self.ui.settingSave.connect(self.server.change_port)
        self.server.moveToThread(self.server_thread)
        self.server_thread.started.connect(self.server.run)
        self.server_thread.finished.connect(self.server_thread.deleteLater)
        self.server_thread.start()

    def show_msg(self, msg):
        notification = Notify()
        notification.application_name = "ClipWarp"
        notification.title = msg[0]
        notification.message = msg[1]
        notification.icon = load_ico("cw.svg")
        notification.send()

    def db_function(self):
        self.connection = Database().create_db()

    def serve_function(self):
        self.serve_thread = QThread()
        self.serve = Serve()
        self.serve.moveToThread(self.serve_thread)
        self.serve_thread.started.connect(self.serve.start)
        self.serve_thread.start()

    def client_function(self):
        self.client_thread = QThread()
        self.client = Client()
        self.Chat.message_signal.connect(self.client.bridge)
        self.Chat.clips_fetched.connect(self.ui.load_clips)
        self.ui.itemDeleted.connect(self.Chat.delete_clip)
        self.ui.resetDB.connect(self.Chat.reset_db)
        self.ui.settingSave.connect(self.client.change_port)
        self.client.recv_signal.connect(self.Chat.show_msg)
        self.client.moveToThread(self.client_thread)
        self.client_thread.started.connect(self.client.run)
        self.client_thread.finished.connect(self.client_thread.deleteLater)
        self.client_thread.start()

    def setup_system_tray(self):
        self.tray = QSystemTrayIcon(self)
        if self.tray.isSystemTrayAvailable():
            self.tray.setIcon(self.windowIcon())
            ctmenu = QMenu()
            actionshow = ctmenu.addAction("Show/Hide")
            actionshow.triggered.connect(
                lambda: self.hide() if self.isVisible() else self.show_and_center()
            )
            actionquit = ctmenu.addAction("Quit")
            actionquit.triggered.connect(self.close)
            self.tray.setContextMenu(ctmenu)

            self.tray.activated.connect(self.trayActivated)

            self.tray.show()

    def trayActivated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show_and_center()

    def close(self):
        self.tray.hide()
        self.app.quit()

    def show_and_center(self):
        screen = QDesktopWidget().availableGeometry()

        window_size = self.geometry()

        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2

        self.move(x, y)
        self.show()

    def stylesheet(self):
        return """
                QPlainTextEdit, QMainWindow, QFrame, QLabel, QPushButton {
                    background-color: #333;
                    color: #FFF;
                }
                VerticalTabWidget {
                    background-color: #333;
                    color: #FFF;
                    border: none;
                }
                QPlainTextEdit,TabBar, QListWidget {
                    background-color: #4d4d4d;
                    color: #ffffff;
                    border: none;
                    border-radius: 4px;
                    padding: 4px;
                }
                TabBar::tab {
                    height: 32px;
                    width: 158px; 
                    background-color: #424242;
                }
                QTabBar::tab:selected {
                    width: 158px;
                    height: 32px;
                    background-color: #c2c2c2;
                    color: #000;
                }
                QScrollBar:vertical {
                    border: none;
                    background: transparent;
                    width: 6px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background: #c2c2c2;
                    min-height: 20px;
                    border-radius: 3px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #aaaaaa;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    background: none;
                    height: 0px;
                }
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                    background: none;
                }
               """

    def set_window_icon(self, icon_path):
        icon = QIcon(icon_path)
        self.setWindowIcon(icon)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = MainWindow(app)
    window.show()
    sys.exit(app.exec_())
