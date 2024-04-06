import requests
import socketio
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QSystemTrayIcon

from ui import Ui_MainWindow


class Chat(QMainWindow):
    message_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setFixedSize(612, 392)

        icon = QIcon("./assets/cw.ico")
        self.setWindowIcon(icon)
        self.tray = QSystemTrayIcon(self)

        # Check if System supports STray icons
        if self.tray.isSystemTrayAvailable():
            self.tray.setIcon(self.windowIcon())

            # Context Menu
            ctmenu = QMenu()
            actionshow = ctmenu.addAction("Show/Hide")
            actionshow.triggered.connect(
                lambda: self.hide() if self.isVisible() else self.show()
            )
            actionquit = ctmenu.addAction("Quit")
            actionquit.triggered.connect(self.close)

            self.tray.setContextMenu(ctmenu)
            self.tray.show()
        else:
            # Destroy unused var
            self.tray = None

        # Show App
        self.show()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setStyleSheet(
            """
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
        )

        self.socketio = socketio.Client()

        def on_refresh():
            print("wssup")

        self.socketio.on("refresh", on_refresh)
        self.socketio.connect("http://localhost:5000")

        self.fetch_clips()

        self.ui.Send.clicked.connect(self.on_button_click)
        self.ui.Paste.clicked.connect(self.paste_text)

    def fetch_clips(self):
        response = requests.get("http://localhost:5000")
        if response.status_code == 200:
            clips = response.json()
            self.ui.load_clips(clips)
        else:
            print("Failed to fetch clips from server")

    def show_msg(self, msg):
        self.fetch_clips()

    def on_button_click(self):
        message = self.ui.plainTextEdit.toPlainText()
        if message != "":
            self.message_signal.emit(message)
            self.ui.plainTextEdit.setPlainText("")
            self.fetch_clips()

    def paste_text(self):
        text_edit = self.ui.plainTextEdit
        clipboard = QApplication.clipboard()
        text_edit.insertPlainText(clipboard.text())

    def get_ip_address(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
