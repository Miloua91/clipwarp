
from PyQt5.QtCore import QObject, pyqtSignal
import asyncio
import websockets

class Server(QObject):
    message_signal = pyqtSignal(tuple)
    CONNECTIONS={}
    def __init__(self):
        super().__init__()

    def run(self):
        print('server is runnig')
        asyncio.run(self.start_server())

    async def start_server(self):
        async with websockets.serve(self.register, "localhost", 5678):
            await asyncio.Future()

    async def register(self, websocket):
        name ='PC' if len(self.CONNECTIONS)==0 else f'Phone_{len(self.CONNECTIONS)}'
        self.CONNECTIONS[name] = websocket
        print(f"{name} connected")
        try:
            async for message in websocket:
                for conn_name, conn in self.CONNECTIONS.items():
                    if conn != websocket:
                        await conn.send(message)
                    else:
                        if conn_name != 'PC':
                            self.message_signal.emit((conn_name, message))
                        print(f"Message received from {conn_name}: {message}")
            await websocket.wait_closed()
        finally:
            del self.CONNECTIONS[name]
            print(f"{name} disconnected")

