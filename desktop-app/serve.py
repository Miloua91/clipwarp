import socket

import uvicorn
from blacksheep import Application
from PyQt5.QtCore import QObject, pyqtSignal


class Serve(QObject):
    def start(self):
        app = Application()
        app.serve_files("assets/dist", index_document="index.html")
        uvicorn.run(app, host=self.get_ip_address(), port=6969)

    def get_ip_address(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
