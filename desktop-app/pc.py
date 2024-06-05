import os
import asyncio
import socket
import ssl

import websockets
from PyQt5.QtCore import QObject, pyqtSignal

setting_path = os.path.join(
    os.path.expanduser("~"), ".config", "clipwarp", "assets", "setting.txt"
)


class Client(QObject):
    recv_signal = pyqtSignal(str)

    def load_port(self):
        if os.path.exists(setting_path):
            with open(setting_path, "r") as f:
                port = f.read()
                return port
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
