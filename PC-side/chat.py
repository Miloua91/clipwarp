from PyQt5.QtWidgets import  QLabel, QVBoxLayout, QPushButton, QWidget, QLineEdit
from PyQt5.QtCore import pyqtSignal
import socket
import asyncio


class Chat(QWidget):
    message_signal = pyqtSignal(str)
    def __init__(self):
        super().__init__()

        # Create a vertical layout
        layout = QVBoxLayout()

        # Create a label
        label1 = QLabel(f'ip address: {self.get_ip_address()}')
        layout.addWidget(label1)

        # Create a QLineEdit widget
        self.input = QLineEdit()
        layout.addWidget(self.input)

        # Create a QPushButton widget
        button = QPushButton('Submit')
        button.clicked.connect(self.on_button_click)
        layout.addWidget(button)

        # Create a second label
        self.label2 = QLabel('')
        layout.addWidget(self.label2)

        # Set the layout for the widget
        self.setLayout(layout)

    def show_msg(self, msg):
        self.label2.setText(msg)

    def on_button_click(self):
        message = self.input.text()
        if message != '':
            self.message_signal.emit(message)
            self.input.setText('')

    def get_ip_address(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip