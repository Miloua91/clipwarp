import os
import re
import socket
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *


class TabBar(QTabBar):
    def tabSizeHint(self, index):
        s = QTabBar.tabSizeHint(self, index)
        s.transpose()
        return s

    def paintEvent(self, event):
        painter = QStylePainter(self)
        opt = QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(opt, i)
            painter.drawControl(QStyle.CE_TabBarTabShape, opt)
            painter.save()

            s = opt.rect.size()
            s.transpose()
            r = QtCore.QRect(QtCore.QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r

            c = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QStyle.CE_TabBarTabLabel, opt)
            painter.restore()


class VerticalTabWidget(QTabWidget):
    def __init__(self, *args, **kwargs):
        QTabWidget.__init__(self, *args, **kwargs)
        self.setTabBar(TabBar())
        self.setTabPosition(QtWidgets.QTabWidget.West)


class Ui_MainWindow(QObject):
    itemDeleted = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.current_tab_index = 0

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("ClipWarp")
        MainWindow.setGeometry(QtCore.QRect(140, 0, 612, 392))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.frame_2 = QtWidgets.QFrame(self.centralwidget)
        self.frame_2.setGeometry(QtCore.QRect(140, 0, 470, 71))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.frame_2)
        self.plainTextEdit.setGeometry(QtCore.QRect(20, 8, 331, 54))
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.Send = QtWidgets.QPushButton(self.frame_2)
        self.Send.setGeometry(QtCore.QRect(370, 38, 81, 24))
        self.Send.setObjectName("Send")
        self.Send.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.Paste = QtWidgets.QPushButton(self.frame_2)
        self.Paste.setGeometry(QtCore.QRect(370, 8, 80, 24))
        self.Paste.setObjectName("Paste")
        self.Paste.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.tabWidget = VerticalTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(2, 70, 608, 301))
        self.tabWidget.setObjectName("tabWidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 25, 57, 24))
        self.label.setObjectName("label")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(110, 25, 24, 24))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton.clicked.connect(self.open_new_window)
        setting_icon = QIcon("./assets/setting.svg")
        self.pushButton.setIcon(setting_icon)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 619, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def categorize_clips(self, clips):
        categorized = {"Text": []}
        for clip in clips:
            url_regex = re.compile(r"(https?://[^\s]+)")
            match = url_regex.search(clip["clips_text"])
            if match:
                url = match.group(0)
                domain = url.split("/")[2].replace("www.", "").replace(".com", "")
                if domain not in categorized:
                    categorized[domain] = []
                categorized[domain].append(clip)
            else:
                categorized["Text"].append(clip)
        return categorized

    def load_clips(self, clips):
        categorized_clips = self.categorize_clips(clips)
        self.render_tabs(categorized_clips)

    def render_tabs(self, categorized_clips):
        self.current_tab_index = self.tabWidget.currentIndex()
        self.tabWidget.clear()
        for category, clips in categorized_clips.items():
            list_widget = QListWidget()
            reversed_clips = reversed(clips)
            for clip in reversed_clips:
                clip_text = clip["clips_text"]
                max_text_length = 63
                if len(clip_text.replace(" ", "")) > max_text_length:
                    clip_text = clip_text[: max_text_length - 3] + "..."
                item = QListWidgetItem(clip_text)
                item.setData(Qt.UserRole, clip["id"])
                item.setSizeHint(QSize(200, 50))
                delete_button = QPushButton("")
                delete_button.setStyleSheet(
                    """
                    QPushButton {
                        border: none; 
                        background-color: transparent; 
                    }
                    QPushButton:hover {
                        background-color: #E08976; 
                        border-radius: 4px;
                    }
                    QPushButton:pressed {
                        background-color: #333; 
                    }
                    """
                )
                delete_button.setFixedSize(24, 24)
                delete_icon = QIcon("./assets/delete.svg")
                delete_button.setIcon(delete_icon)
                delete_button.clicked.connect(
                    lambda _, item=item: self.delete_item(item, list_widget)
                )

                copy_button = QPushButton("")
                copy_button.setStyleSheet(
                    """
                    QPushButton {
                        border: none; 
                        background-color: transparent; 
                    }
                    QPushButton:hover {
                        background-color: #A46877; 
                        border-radius: 4px;
                    }
                    QPushButton:pressed {
                        background-color: #333; 
                    }
                    """
                )
                copy_button.setFixedSize(24, 24)
                copy_icon = QIcon("./assets/copy.svg")
                copy_button.setIcon(copy_icon)
                copy_button.clicked.connect(
                    lambda _, text=clip["clips_text"]: self.copy_clip(text)
                )

                list_widget.addItem(item)

                button_layout = QHBoxLayout()
                button_layout.addWidget(delete_button)
                button_layout.addWidget(copy_button)
                button_layout.setAlignment(Qt.AlignRight)

                button_widget = QWidget()
                button_widget.setLayout(button_layout)
                list_widget.setItemWidget(item, button_widget)

            self.tabWidget.addTab(list_widget, category)
        self.tabWidget.setCurrentIndex(self.current_tab_index)

    def delete_item(self, item, list_widget):
        row = list_widget.row(item)
        if row != -1:
            clip_id = item.data(Qt.UserRole)
            list_widget.takeItem(row)
            self.itemDeleted.emit(clip_id)

    def copy_clip(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def open_new_window(self):
        new_window = QDialog()
        new_window.setStyleSheet(
            """
                QDialog {
                    background-color: #d6d6d6;
                }
            """
        )
        new_window.setWindowTitle("Settings")

        layout = QVBoxLayout()

        ip_label = QLabel("IP Address")
        ip_value_label = QLabel(f"{self.get_ip_address()}")
        ip_layout = QHBoxLayout()
        ip_layout.addWidget(ip_label)
        ip_layout.addWidget(ip_value_label)
        layout.addLayout(ip_layout)

        port_label = QLabel("Port")
        self.port_edit = QPlainTextEdit("6969")
        self.port_edit.setFixedHeight(26)
        self.port_edit.setStyleSheet(
            """
                QPlainTextEdit {
                    background-color: #f0f0f0;
                    color: #333;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                }
            """
        )
        port_layout = QHBoxLayout()
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.port_edit)
        layout.addLayout(port_layout)

        save_button = QPushButton("Save")
        save_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        save_button.setStyleSheet(
            """
                    QPushButton {
                        height: 32px;
                        background-color: #333;
                        color: #f0f0f0;
                        border: 1px solid #ccc;
                        border-radius: 5px;    
                    }
                    QPushButton::hover {
                        background-color: #474747
                    }
                """
        )
        save_button.clicked.connect(self.save_port)
        layout.addWidget(save_button)

        new_window.setLayout(layout)
        self.load_settings()
        new_window.setFixedSize(200, 120)
        new_window.exec_()

    def save_port(self):
        port = self.port_edit.toPlainText()
        if port.isdigit():
            with open("settings.txt", "w") as f:
                f.write(port)
            print("Port saved successfully.")
        else:
            print("Invalid port value. Port must be a number.")

    def load_settings(self):
        if os.path.exists("settings.txt"):
            with open("settings.txt", "r") as f:
                port = f.read()
                self.port_edit.setPlainText(port)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "ClipWarp"))
        self.Send.setText(_translate("MainWindow", "Send"))
        self.Paste.setText(_translate("MainWindow", "Paste"))
        self.label.setText(_translate("MainWindow", "ClipWarp"))
        self.pushButton.setText(_translate("MainWindow", ""))

    def get_ip_address(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
