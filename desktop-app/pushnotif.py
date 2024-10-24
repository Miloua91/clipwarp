import os

import requests
import toml
from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
    PushTicketError,
)
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from requests.exceptions import ConnectionError, HTTPError

setting_path = os.path.join(
    os.path.expanduser("~"), ".config", "clipwarp", "assets", "setting.toml"
)

session = requests.Session()
session.headers.update(
    {
        "accept": "application/json",
        "accept-encoding": "gzip, deflate",
        "content-type": "application/json",
    }
)


class Push(QObject):
    message_sent = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.session = session

    def token(self):
        if os.path.exists(setting_path):
            try:
                settings = toml.load(setting_path)
                return settings.get("token", None)
            except toml.TomlDecodeError:
                print("Error decoding TOML file.")
                return None
        else:
            return None

    def title(self):
        if os.path.exists(setting_path):
            try:
                settings = toml.load(setting_path)
                return settings.get("server_name", "Server")
            except toml.TomlDecodeError:
                print("Error decoding TOML file.")
                return "Server"
        else:
            return "Server"

    def send_push_message(self, message, extra=None):
        if self.token():
            try:
                response = PushClient(session=self.session).publish(
                    PushMessage(
                        to=self.token(),
                        category="default",
                        title=self.title(),
                        body=message,
                        data=extra,
                    )
                )
                response.validate_response()
                self.message_sent.emit("Message sent successfully.")
            except DeviceNotRegisteredError:
                self.error_occurred.emit("The push token is no longer registered.")
            except (PushServerError, ConnectionError, HTTPError) as exc:
                self.error_occurred.emit(f"Error occurred: {str(exc)}")


class PushThread(QThread):
    finished_signal = pyqtSignal()

    def __init__(self, msg, push_obj):
        super().__init__()
        self.msg = msg
        self.push_obj = push_obj

    def run(self):
        try:
            self.push_obj.send_push_message(self.msg)
            self.finished_signal.emit()
        except Exception as e:
            print(f"Error sending notification: {e}")
