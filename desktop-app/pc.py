import asyncio
import socket

import websockets
from PyQt5.QtCore import QObject, pyqtSignal


class Client(QObject):
    recv_signal = pyqtSignal(str)

    def run(self):
        asyncio.run(self.client())

    def get_ip_address(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip

    async def client(self):
        uri = f"ws://{self.get_ip_address()}:5678/Server"
        async with websockets.connect(uri) as self.websocket:
            async for message in self.websocket:
                self.recv_signal.emit(message)

    def bridge(self, msg):
        asyncio.run(self.send_message(msg))

    async def send_message(self, message):
        await self.websocket.send(message)