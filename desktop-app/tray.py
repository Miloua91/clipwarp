import os

from PIL import Image, ImageDraw
from PyQt5.QtCore import QObject, pyqtSignal
from pystray import Icon
from pystray import Menu as menu
from pystray import MenuItem as item


class Tray(QObject):
    icon_clicked = pyqtSignal()
    exit_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.icon = Icon("CLipwarp", icon=Image.open("./assets/clipwarp.png"))
        self.icon.menu = menu(
            item(text="Open", action=lambda: self.icon_clicked.emit(), default=True),
            item("Exit", self.exit_icon),
        )

    def run(self):
        self.icon.run()

    def exit_icon(self):
        self.icon.visible = False
        self.icon.stop()
        self.exit_signal.emit()

