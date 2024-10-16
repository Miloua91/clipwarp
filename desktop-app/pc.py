import asyncio
import os
import socket
import ssl

import toml
import websockets
from PyQt5.QtCore import QObject, pyqtSignal

setting_path = os.path.join(
    os.path.expanduser("~"), ".config", "clipwarp", "assets", "setting.toml"
)


class Client(QObject):
    recv_signal = pyqtSignal(str)

    def load_port(self):
        if os.path.exists(setting_path):
            settings = toml.load(setting_path)
            return settings.get("port", 42069)
        else:
            return 42069

    def run(self):
        asyncio.run(self.client())

    def get_ip_address(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip

    async def client(self):
        uri = f"ws://{self.get_ip_address()}:{self.load_port()}/Server"
        async with websockets.connect(uri) as self.websocket:
            async for message in self.websocket:
                self.recv_signal.emit(message)

    def bridge(self, msg):
        asyncio.run(self.send_message(msg))

    async def send_message(self, message):
        await self.websocket.send(message)
