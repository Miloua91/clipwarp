import os
import socket

import requests
import toml
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication

from pushnotif import Push, PushThread

setting_path = os.path.join(
    os.path.expanduser("~"), ".config", "clipwarp", "assets", "setting.toml"
)


class Chat(QObject):
    message_signal = pyqtSignal(str)
    clips_fetched = pyqtSignal(list)

    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.http_session = requests.Session()
        self.http_session.verify = False
        self.fetch_clips()
        self.ui.Send.clicked.connect(self.on_button_click)
        self.ui.Paste.clicked.connect(self.paste_text)

    def load_port(self):
        if os.path.exists(setting_path):
            settings = toml.load(setting_path)
            port = settings.get("port", 42069)
            return int(port) + 1
        else:
            return 42070

    def fetch_clips(self):
        response = requests.get(
            f"http://{self.get_ip_address()}:{self.load_port()}", verify=False
        )
        if response.status_code == 200:
            clips = response.json()
            self.clips_fetched.emit(clips)
            self.ui.load_clips(clips)
        else:
            print("Failed to fetch clips from server")

    def on_delete(self, clip_id):
        response = requests.delete(
            f"http://{self.get_ip_address()}:{self.load_port()}/delete/{clip_id}",
            verify=False,
        )
        if response.status_code == 200:
            clips = response.json()
        else:
            print("Failed to delete clip from server")

    def refresh(self):
        response = requests.get(
            f"http://{self.get_ip_address()}:{self.load_port()}", verify=False
        )
        if response.status_code == 200:
            clips = response.json()
            self.clips_fetched.emit(clips)
        else:
            print("Failed to delete clip from server")

    def on_reset(self):
        response = requests.post(
            f"http://{self.get_ip_address()}:{self.load_port()}/reset", verify=False
        )
        if response.status_code == 200:
            print("Database has been reset")
            self.fetch_clips()
        else:
            print("Failed to reset database from server")

    def show_msg(self, msg):
        self.fetch_clips()

    def on_button_click(self):
        message = self.ui.plainTextEdit.toPlainText()
        if message:
            self.push = Push()
            self.push_thread = PushThread(message, self.push)
            self.push_thread.finished_signal.connect(self.cleanup_push_thread)
            self.push_thread.start()
            self.message_signal.emit(message)
            self.ui.plainTextEdit.setPlainText("")
        self.refresh()

    def cleanup_push_thread(self):
        if self.push_thread is not None:
            self.push_thread.quit()
            self.push_thread.wait()
            self.push_thread = None

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
