import asyncio
import socket

import websockets
from db import Database
from PyQt5.QtCore import QObject, pyqtSignal


class Server(QObject):
    message_signal = pyqtSignal(tuple)
    CONNECTIONS = {}

    def __init__(self):
        super().__init__()
        self.db = Database()

    def run(self):
        print("server is runnig")
        asyncio.run(self.start_server())

    def get_ip_address(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip

    async def start_server(self):
        async with websockets.serve(self.register, self.get_ip_address(), 5678):
            await asyncio.Future()

    async def register(self, websocket, path):
        name = path
        self.CONNECTIONS[name] = websocket
        print(f"{name} connected")

        try:
            async for message in websocket:
                # Broadcast the message to all connections except the current one
                for conn_name, conn in self.CONNECTIONS.items():
                    if conn != websocket:
                        await conn.send(message)
                    else:
                        # Emit signal for message received
                        if conn_name != "/Server":
                            self.message_signal.emit((conn_name, message))
                        print(f"Message received from {conn_name}: {message}")
                        connection = self.db.create_connection("./assets/clipwarp.db")
                        insert_clips = """
                            INSERT INTO clips (clips_text, user_id)
                            VALUES (?, ?)
                        """
                        params = (message, 1)
                        self.db.execute_query(connection, insert_clips, params)
            await websocket.wait_closed()

        finally:
            # Check if the name exists in CONNECTIONS before deleting
            if name in self.CONNECTIONS:
                del self.CONNECTIONS[name]
                print(f"{name} disconnected")
