from PyQt5.QtCore import QObject, pyqtSignal
import asyncio
import websockets

class Client(QObject):
    recv_signal = pyqtSignal(str)
    def run(self):
        asyncio.run(self.client())


    async def client(self):
        uri = "ws://localhost:5678"
        async with websockets.connect(uri) as self.websocket:
            async for message in self.websocket:
                self.recv_signal.emit(message)

    def bridge(self,msg):
        asyncio.run(self.send_message(msg))

    async def send_message(self, message):
        await self.websocket.send(message)
