import asyncio
import os
import socket

import socketio
import toml
from PyQt5.QtCore import QObject, QThread, pyqtSignal

setting_path = os.path.join(
    os.path.expanduser("~"), ".config", "clipwarp", "assets", "setting.toml"
)


class SocketWorker(QObject):
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    delete_clip = pyqtSignal()
    reset_db = pyqtSignal()
    edit_clip = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.socketio = socketio.AsyncClient()
        self.current_port = self.load_port()
        self.running = True
        self.loop = None

        @self.socketio.event
        def delete():
            self.delete_clip.emit()

        @self.socketio.event
        def reset():
            self.reset_db.emit()

        @self.socketio.event
        def edit():
            self.edit_clip.emit()

    def load_port(self):
        if os.path.exists(setting_path):
            settings = toml.load(setting_path)
            port = settings.get("port", 42069)
            return int(port) + 1
        return 42070

    def get_ip_address(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip

    async def run_async(self):
        retries = 0
        while self.running:
            try:
                url = f"http://{self.get_ip_address()}:{self.current_port}"
                await self.socketio.connect(url)
                self.connected.emit()
                while self.running and self.socketio.connected:
                    await asyncio.sleep(0.1)
                if not self.running:
                    await self.socketio.disconnect()
                    break
            except socketio.exceptions.ConnectionError:
                if not self.running:
                    break
                retries += 1
                delay = min(2**retries, 30)
                print(f"Connection failed. Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
            except Exception as e:
                print(f"Unexpected error: {e}")
                if not self.running:
                    break
                await asyncio.sleep(5)

    def run(self):
        try:
            self.running = True
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self.run_async())
        finally:
            self.running = False
            if self.loop and self.loop.is_running():
                self.loop.stop()
            if self.loop and not self.loop.is_closed():
                self.loop.close()

    def stop(self):
        self.running = False


class SocketClient(QObject):
    delete_clip = pyqtSignal()
    reset_db = pyqtSignal()
    edit_clip = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.thread = QThread()
        self.worker = SocketWorker()
        self.worker.moveToThread(self.thread)
        self.worker.delete_clip.connect(self.delete_clip)
        self.worker.reset_db.connect(self.reset_db)
        self.worker.edit_clip.connect(self.edit_clip)
        self.thread.started.connect(self.worker.run)

    def start(self):
        if not self.thread.isRunning():
            self.thread.start()

    def stop(self):
        if self.thread.isRunning():
            self.worker.stop()
            self.thread.quit()
            self.thread.wait(5000)
