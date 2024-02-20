from PyQt5.QtWidgets import  QWidget
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal
import socket
from widget_ui import Ui_Widget

class Chat(QWidget):
    message_signal = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.ui = Ui_Widget()
        self.ui.setupUi(self)

        self.ui.ip_label.setText(f'ip address: {self.get_ip_address()}')
        self.ui.sendButton.clicked.connect(self.on_button_click)
        self.ui.copyButton.clicked.connect(self.copy_text)
        self.ui.textEdit_2.setReadOnly(True)

    def show_msg(self, msg):
        self.ui.textEdit_2.setText(msg)

    def on_button_click(self):
        message = self.ui.textEdit.toPlainText()
        if message != '':
            self.message_signal.emit(message)
            self.ui.textEdit.setText('')

    def copy_text(self):
        text = self.ui.textEdit_2.toPlainText()
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def get_ip_address(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip