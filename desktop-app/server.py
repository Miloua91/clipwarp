import os
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

    def load_port(self):
        if os.path.exists("settings.txt"):
            with open("settings.txt", "r") as f:
                port = f.read()
                return port
        else: 
            return 42069

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
        async with websockets.serve(self.register, self.get_ip_address(), self.load_port()):
            await asyncio.Future()

    async def register(self, websocket, path):
        name = path.strip("/")
        self.CONNECTIONS[name] = websocket
        print(f"{name} connected")

        connection = self.db.create_connection("./assets/clipwarp.db")

        # Check if the user exists, if not, insert the user and get the user_id
        select_user = "SELECT id FROM users WHERE name = ?"
        result = self.db.execute_read_query(connection, select_user, (name,))
        if result:
            user_id = result[0][0]
        else:
            insert_user = "INSERT INTO users (name) VALUES (?)"
            self.db.execute_query(connection, insert_user, (name,))
            # Rerun the select query to get the new user_id
            result = self.db.execute_read_query(connection, select_user, (name,))
            if result:
                user_id = result[0][0]
            else:
                print(f"Failed to insert or retrieve user_id for {name}")
                return

        try:
            async for message in websocket:
                # Broadcast the message to all connections except the current one
                for conn_name, conn in self.CONNECTIONS.items():
                    if conn != websocket:
                        await conn.send(message)
                    else:
                        # Emit signal for message received
                        if conn_name != "Server":
                            self.message_signal.emit((conn_name, message))
                        print(f"Message received from {conn_name}: {message}")
                        insert_clips = """
                            INSERT INTO clips (clips_text, user_id)
                            VALUES (?, ?)
                        """
                        params = (message, user_id)
                        self.db.execute_query(connection, insert_clips, params)
            await websocket.wait_closed()

        finally:
            # Check if the name exists in CONNECTIONS before deleting
            if name in self.CONNECTIONS:
                del self.CONNECTIONS[name]
                print(f"{name} disconnected")
