import asyncio
import os
import socket
import ssl

import toml
import websockets
from PyQt5.QtCore import QObject, pyqtSignal

from db import Database

setting_path = os.path.join(
    os.path.expanduser("~"), ".config", "clipwarp", "assets", "setting.toml"
)
db_path = os.path.join(
    os.path.expanduser("~"), ".config", "clipwarp", "assets", "clipwarp.db"
)


class Server(QObject):
    message_signal = pyqtSignal(tuple)
    CONNECTIONS = {}

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.server = None
        self.server_task = None
        self.current_port = None
        self.loop = None

    def load_port(self):
        if os.path.exists(setting_path):
            settings = toml.load(setting_path)
            return settings.get("port", 42069)
        else:
            return 42069

    def get_ip_address(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip

    async def start_server(self):
        self.current_port = self.load_port()
        self.server = await websockets.serve(
            self.register, self.get_ip_address(), self.current_port
        )
        print(f"Server started on port {self.current_port}")
        await self.server.wait_closed()

    async def stop_server(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            print("Server stopped")

    async def restart_server(self):
        await self.stop_server()

        await self.start_server()

    def run(self):
        print("Server is running")
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.server_task = self.loop.create_task(self.start_server())
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass

    def change_port(self):
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self.restart_server(), self.loop)
            return True
        return False

    async def register(self, websocket, path):
        name = path.strip("/")
        self.CONNECTIONS[name] = websocket
        print(f"{name} connected")

        connection = self.db.create_connection(db_path)
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
