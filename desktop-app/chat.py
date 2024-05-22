import os
import socket

import requests
import socketio
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QSystemTrayIcon


class Chat(QObject):
    message_signal = pyqtSignal(str)
    clips_fetched = pyqtSignal(list)

    def __init__(self, ui):
        super().__init__()
        self.ui = ui

        self.socketio = socketio.Client()

        self.socketio.on("delete", self.on_delete)
        self.socketio.on("reset", self.on_delete)
        self.socketio.connect(f"http://{self.get_ip_address()}:{self.load_port()}")

        self.fetch_clips()

        self.ui.Send.clicked.connect(self.on_button_click)
        self.ui.Paste.clicked.connect(self.paste_text)
        

    def load_port(self):
        if os.path.exists("settings.txt"):
            with open("settings.txt", "r") as f:
                port = f.read()
                return (int(port) + 1)
        else: 
            return 42070


    def fetch_clips(self):
        response = requests.get(f"http://{self.get_ip_address()}:{self.load_port()}")
        if response.status_code == 200:
            clips = response.json()
            self.clips_fetched.emit(clips)
            self.ui.load_clips(clips)
        else:
            print("Failed to fetch clips from server")

    def delete_clip(self, clip_id):
        response = requests.delete(
            f"http://{self.get_ip_address()}:{self.load_port()}/delete/{clip_id}"
        )
        if response.status_code == 200:
            clips = response.json()
        else:
            print("Failed to delete clip from server")

    def on_delete(self):
        response = requests.get(f"http://{self.get_ip_address()}:{self.load_port()}")
        if response.status_code == 200:
            clips = response.json()
            self.clips_fetched.emit(clips)
        else:
            print("Failed to fetch clips from server")

    def reset_db(self):
        response = requests.post(f"http://{self.get_ip_address()}:{self.load_port()}/reset")
        if response.status_code == 200:
            self.fetch_clips
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
