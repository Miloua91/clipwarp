import socket

from flask import Flask, render_template
from PyQt5.QtCore import QObject

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


class Serve(QObject):
    def start(self):
        ip_address = self.get_ip_address()
        app.run(host=ip_address, port=6969)

    def get_ip_address(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
