import asyncio
import os
import socket

import toml
import websockets
from PyQt5.QtCore import QObject, pyqtSignal

setting_path = os.path.join(
    os.path.expanduser("~"), ".config", "clipwarp", "assets", "setting.toml"
)


class Client(QObject):
    recv_signal = pyqtSignal(str)
    connection_status_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.websocket = None
        self.client_task = None
        self.loop = None
        self.current_port = None
        self.is_running = False

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

    async def connect(self):
        self.current_port = self.load_port()
        uri = f"ws://{self.get_ip_address()}:{self.current_port}/Server"
        try:
            self.websocket = await websockets.connect(uri)
            self.connection_status_signal.emit(True)
            async for message in self.websocket:
                self.recv_signal.emit(message)
        except Exception as e:
            print(f"Connection error: {e}")
            self.connection_status_signal.emit(False)
        finally:
            if self.websocket:
                await self.websocket.close()
                self.connection_status_signal.emit(False)

    async def disconnect(self):
        if self.websocket:
            try:
                await self.websocket.close()
                self.connection_status_signal.emit(False)
                print("Disconnected from server")
                await asyncio.sleep(0.1)
            except Exception as e:
                print(f"Error during disconnect: {e}")

    async def reconnect(self):
        await self.disconnect()

        await self.connect()

    def run(self):
        self.is_running = True
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        try:
            self.client_task = self.loop.create_task(self.connect())
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.is_running = False

    def stop(self):
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)
            self.is_running = False

    def change_port(self):
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self.reconnect(), self.loop)
            return True
        return False

    def bridge(self, msg):
        if self.loop and self.websocket and not self.websocket.closed:
            asyncio.run_coroutine_threadsafe(self.send_message(msg), self.loop)
        else:
            print("Cannot send message: Client not connected")

    async def send_message(self, message):
        if self.websocket and not self.websocket.closed:
            await self.websocket.send(message)
        else:
            print("Cannot send message: WebSocket is closed")
