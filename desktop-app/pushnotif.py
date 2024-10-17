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
from PyQt5.QtCore import QObject
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
        try:
            response = PushClient(session=session).publish(
                PushMessage(
                    to=self.token(),
                    category="default",
                    title=self.title(),
                    body=message,
                    data=extra,
                )
            )
        except PushServerError as exc:
            rollbar.report_exc_info(
                extra_data={
                    "token": self.token(),
                    "title": self.title(),
                    "message": message,
                    "extra": extra,
                    "errors": exc.errors,
                    "response_data": exc.response_data,
                }
            )
            raise
        except (ConnectionError, HTTPError) as exc:
            rollbar.report_exc_info(
                extra_data={
                    "token": self.token(),
                    "title": self.title(),
                    "message": message,
                    "extra": extra,
                }
            )
            raise self.retry(exc=exc)

        try:
            response.validate_response()
        except DeviceNotRegisteredError:
            from notifications.models import PushToken

            PushToken.objects.filter(token=token).update(active=False)
        except PushTicketError as exc:
            rollbar.report_exc_info(
                extra_data={
                    "token": self.token(),
                    "title": self.title(),
                    "message": message,
                    "extra": extra,
                    "push_response": exc.push_response._asdict(),
                }
            )
            raise self.retry(exc=exc)
