import os
import re
import socket
import sys
import webbrowser

import toml
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QFontMetrics, QIcon
from PyQt5.QtWidgets import *

# TODO: Try to change the maximize button behavior and icon
# TODO: Display link metadata
# TODO: Add note to links
# PERF: Add time
# PERF: Add a dot to links tab to notify for new links in that tab
# PERF: Minimize the app to the system tray instead of quitting


def resource_path(relative_path):
    if getattr(sys, "frozen", False):
        application_path = sys._MEIPASS
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(application_path, relative_path)


def load_svg(file_name):
    file_path = resource_path(os.path.join("assets", file_name))
    if not os.path.isfile(file_path):
        print(f"Cannot open file '{file_path}', because: No such file or directory")
    else:
        return file_path


setting_path = os.path.join(
    os.path.expanduser("~"), ".config", "clipwarp", "assets", "setting.toml"
)


class TabBar(QTabBar):
    def tabSizeHint(self, index):
        return QtCore.QSize(158, 32)

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
    resetDB = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.current_tab_index = 0
        self.updated_tabs = set()

    def load_port(self):
        if os.path.exists(setting_path):
            settings = toml.load(setting_path)
            port = settings.get("port", 42069)
            return int(port) + 1
        else:
            return 42070

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("ClipWarp")
        MainWindow.setGeometry(QtCore.QRect(160, 0, 632, 392))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.frame_2 = QtWidgets.QFrame(self.centralwidget)
        self.frame_2.setGeometry(QtCore.QRect(160, 0, 490, 71))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.frame_2)
        self.plainTextEdit.setGeometry(QtCore.QRect(25, 8, 331, 54))
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.Send = QtWidgets.QPushButton(self.frame_2)
        self.Send.setGeometry(QtCore.QRect(380, 38, 81, 24))
        self.Send.setObjectName("Send")
        self.Send.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.Paste = QtWidgets.QPushButton(self.frame_2)
        self.Paste.setGeometry(QtCore.QRect(380, 8, 80, 24))
        self.Paste.setObjectName("Paste")
        self.Paste.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.tabWidget = VerticalTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(2, 70, 628, 301))
        self.tabWidget.setObjectName("tabWidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 25, 57, 24))
        self.label.setObjectName("label")
        self.setting = QtWidgets.QPushButton(self.centralwidget)
        self.setting.setGeometry(QtCore.QRect(125, 25, 24, 24))
        self.setting.setObjectName("pushButton")
        self.setting.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.setting.clicked.connect(self.open_new_window)
        setting_icon = QIcon(load_svg("setting.svg"))
        self.setting.setIcon(setting_icon)
        self.openapp = QtWidgets.QPushButton(self.centralwidget)
        self.openapp.setGeometry(QtCore.QRect(90, 25, 24, 24))
        self.openapp.setObjectName("openApp")
        self.openapp.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.openapp.clicked.connect(self.open_app)
        webapp_icon = QIcon(load_svg("webapp.svg"))
        self.openapp.setIcon(webapp_icon)
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
        self.tabWidget.currentChanged.connect(self.on_tab_changed)

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

    def on_tab_changed(self, index):
        self.update_status_for_tab(index)

    def update_status_for_tab(self, index):
        list_widget = self.tabWidget.widget(index)
        if list_widget:
            clip_ids = [
                item.data(Qt.UserRole)
                for i in range(list_widget.count())
                for item in [list_widget.item(i)]
                if isinstance(item.data(Qt.UserRole), int)
            ]

            payload = {"ids": clip_ids}
            self.send_update_request(payload)

    def send_update_request(self, payload):
        import requests

        url = f"http://{self.get_ip_address()}:{self.load_port()}/noti"
        response = requests.post(url, json=payload)

    def truncate_text_to_width(self, text, font, max_width):
        metrics = QFontMetrics(font)
        ellipsis = "..."
        text_width = metrics.width(text)
        if text_width <= max_width:
            return text
        for i in range(len(text), 0, -1):
            truncated_text = text[:i] + ellipsis
            if metrics.width(truncated_text) <= max_width:
                return truncated_text
        return text[:max_width]

    def render_tabs(self, categorized_clips):
        self.current_tab_index = self.tabWidget.currentIndex()
        self.tabWidget.blockSignals(True)
        self.tabWidget.clear()
        for category, clips in categorized_clips.items():
            is_category_seen = False
            list_widget = QListWidget()
            list_widget.setFixedWidth(468)
            reversed_clips = reversed(clips)
            for clip in reversed_clips:
                if not clip["is_seen"]:
                    is_category_seen = True
                clip_text = clip["clips_text"]
                username = clip["user_name"]
                date = clip["date"]
                max_pixel_width = 340
                font = list_widget.font()
                clip_text = self.truncate_text_to_width(
                    clip_text, font, max_pixel_width
                )
                item = QListWidgetItem(clip_text)
                item.setData(Qt.UserRole, clip["id"])
                item.setSizeHint(QSize(400, 68))
                delete_button = QPushButton("")
                delete_button.setStyleSheet(
                    """
                    QPushButton {
                        border: none; 
                        background-color: transparent; 
                    }
                    QPushButton:hover {
                        background-color: #e76f51; 
                        border-radius: 4px;
                    }
                    QPushButton:pressed {
                        background-color: #333; 
                    }
                    """
                )
                delete_button.setFixedSize(24, 24)
                delete_icon = QIcon(load_svg("delete.svg"))
                delete_button.setIcon(delete_icon)
                delete_button.clicked.connect(
                    lambda _, item=item, list_widget=list_widget: self.delete_item(
                        item, list_widget
                    )
                )

                copy_button = QPushButton("")
                copy_button.setStyleSheet(
                    """
                    QPushButton {
                        border: none; 
                        background-color: transparent; 
                    }
                    QPushButton:hover {
                        background-color: #2a9d8f; 
                        border-radius: 4px;
                    }
                    QPushButton:pressed {
                        background-color: #333; 
                    }
                    """
                )
                copy_button.setFixedSize(24, 24)
                copy_icon = QIcon(load_svg("copy.svg"))
                copy_button.setIcon(copy_icon)
                copy_button.clicked.connect(
                    lambda _, text=clip["clips_text"]: self.copy_clip(text)
                )

                url_button = QPushButton("")
                url_button.setStyleSheet(
                    """
                    QPushButton {
                        border: none; 
                        background-color: transparent; 
                    }
                    QPushButton:hover {
                        background-color: #e9c46a; 
                        border-radius: 4px;
                    }
                    QPushButton:pressed {
                        background-color: #333; 
                    }
                    """
                )
                url_button.setFixedSize(24, 24)
                url_icon = QIcon(load_svg("open.svg"))
                url_button.setIcon(url_icon)
                url_button.clicked.connect(
                    lambda _, text=clip["clips_text"]: self.open_url(text)
                )

                user_label = QLabel()
                user_label.setStyleSheet(
                    """
                        QLabel {
                            font: 10px;
                            background-color: transparent; 
                            padding-top: 28px;
                        }
                        """
                )
                user_label.setText(username)

                date_label = QLabel()
                date_label.setStyleSheet(
                    """
                        QLabel {
                            font: 10px;
                            background-color: transparent; 
                            padding-top: 28px;
                        }
                        """
                )
                date_label.setText(date)

                list_widget.addItem(item)

                button_layout = QHBoxLayout()
                button_layout.addWidget(user_label)
                button_layout.addWidget(date_label)
                if self.tabWidget.count() > 0:
                    button_layout.addWidget(url_button)
                button_layout.addWidget(copy_button)
                button_layout.addWidget(delete_button)
                button_layout.setAlignment(Qt.AlignRight)

                button_widget = QWidget()
                button_widget.setLayout(button_layout)
                list_widget.setItemWidget(item, button_widget)

            max_pixel_width = 100
            font = list_widget.font()
            category = self.truncate_text_to_width(category, font, max_pixel_width)

            if is_category_seen:
                tab_label = f"{category} ({len(clips)})"
                self.tabWidget.setIconSize(QSize(8, 8))
                tab_icon = QIcon(load_svg("active-tab-indicator.svg"))
                self.tabWidget.addTab(list_widget, tab_icon, tab_label)
            else:
                self.tabWidget.addTab(list_widget, category)

        if (
            self.current_tab_index >= 0
            and self.current_tab_index < self.tabWidget.count()
        ):
            self.tabWidget.setCurrentIndex(self.current_tab_index)
        else:
            self.tabWidget.setCurrentIndex(0)

        self.tabWidget.blockSignals(False)
        self.update_notifications(categorized_clips)

    def update_notifications(self, categorized_clips):
        current_tab_text = self.tabWidget.tabText(self.current_tab_index)

        if current_tab_text in self.updated_tabs:
            return

        for category, clips in categorized_clips.items():
            if category in current_tab_text:
                clip_ids = [clip["id"] for clip in clips]
                payload = {"ids": clip_ids}
                self.send_update_request(payload)
                self.updated_tabs.add(current_tab_text)
                break

    def clear_updated_tabs(self):
        self.updated_tabs.clear()

    def delete_item(self, item, list_widget):
        row = list_widget.row(item)
        if row != -1:
            clip_id = item.data(Qt.UserRole)
            list_widget.takeItem(row)
            self.itemDeleted.emit(clip_id)

    def open_url(self, text):
        webbrowser.open(f"{text}")

    def copy_clip(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def open_app(self):
        webbrowser.open(f"http://{self.get_ip_address()}:6969")

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
        self.port_edit = QPlainTextEdit("42069")
        self.port_edit.setFixedHeight(26)
        self.port_edit.setFixedWidth(90)
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

        reset_button = QPushButton("Reset Database")
        reset_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        reset_button.setStyleSheet(
            """
                        QPushButton {
                                height: 32px;
                                background-color: #ef4444;
        color: #f0f0f0;
        border: 1px solid #ccc;
        border-radius: 5px;    
    }
    QPushButton::hover {
        background-color: #f87171;
        color: #f9fafb;
    }
    """
        )
        reset_button.clicked.connect(self.reset_db)
        layout.addWidget(reset_button)

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
        new_window.setFixedSize(200, 160)
        new_window.exec_()

    def reset_db(self):
        dlg = QDialog()
        dlg.setFixedSize(340, 100)

        layout = QVBoxLayout()
        message_label = QLabel(
            "Resetting the Clips database is irreversible. Are you sure you want to proceed?"
        )
        message_label.setWordWrap(True)
        message_layout = QHBoxLayout()
        message_layout.addWidget(message_label)

        yes_button = QPushButton("Yes")
        yes_button.setFixedSize(42, 33)
        yes_button.clicked.connect(dlg.accept)
        yes_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        yes_button.setStyleSheet(
            """
                    QPushButton {
                        height: 32px;
                        background-color: #ef4444;
                        color: #f0f0f0;
                        border: 1px solid #ccc;
                        border-radius: 5px;    
                    }
                    QPushButton::hover {
                        background-color: #f87171
                    }
                """
        )
        no_button = QPushButton("No")
        no_button.setFixedSize(42, 33)
        no_button.clicked.connect(dlg.reject)
        no_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        no_button.setStyleSheet(
            """
                    QPushButton {
                        height: 32px;
                        background-color: #d4d4d4;
                        color: #18181b;
                        border: 1px solid #ccc;
                        border-radius: 5px;    
                    }
                    QPushButton::hover {
                        background-color: #e5e5e5
                    }
                """
        )

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(yes_button)
        button_layout.addWidget(no_button)
        layout.addLayout(message_layout)
        layout.addLayout(button_layout)

        dlg.setLayout(layout)
        dlg.setWindowTitle("Reset Database")
        result = dlg.exec()
        if result == QDialog.Accepted:
            self.resetDB.emit()

    def save_port(self):
        port = self.port_edit.toPlainText()
        if port.isdigit():
            dlg = QDialog()
            dlg.setFixedSize(340, 100)

            layout = QVBoxLayout()
            message_label = QLabel("You must exit the application to save the changes!")
            message_label.setWordWrap(True)
            message_layout = QHBoxLayout()
            message_layout.addWidget(message_label)

            exit_button = QPushButton("Exit")
            exit_button.setFixedSize(50, 33)
            exit_button.clicked.connect(dlg.accept)
            exit_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            exit_button.setStyleSheet(
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
            cancel_button = QPushButton("Cancel")
            cancel_button.setFixedSize(50, 33)
            cancel_button.clicked.connect(dlg.reject)
            cancel_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            cancel_button.setStyleSheet(
                """
                        QPushButton {
                            height: 32px;
                            background-color: #d4d4d4;
                            color: #18181b;
                            border: 1px solid #ccc;
                            border-radius: 5px;    
                        }
                        QPushButton::hover {
                            background-color: #e5e5e5
                        }
                    """
            )

            button_layout = QHBoxLayout()
            button_layout.addStretch()
            button_layout.addWidget(exit_button)
            button_layout.addWidget(cancel_button)
            layout.addLayout(message_layout)
            layout.addLayout(button_layout)

            dlg.setLayout(layout)
            dlg.setWindowTitle("Change Port")
            result = dlg.exec()
            if result == QDialog.Accepted:
                settings = {}
                if os.path.exists(setting_path):
                    settings = toml.load(setting_path)
                settings["port"] = int(port)
                with open(setting_path, "w") as f:
                    toml.dump(settings, f)
                os._exit(1)
            print("Port saved successfully.")
        else:
            dlg = QDialog()
            dlg.setFixedSize(240, 100)

            layout = QVBoxLayout()
            message_label = QLabel("Invalid port value. Port must be a number.")
            message_label.setWordWrap(True)
            message_layout = QHBoxLayout()
            message_layout.addWidget(message_label)

            ok_button = QPushButton("Ok")
            ok_button.setFixedSize(42, 33)
            ok_button.clicked.connect(dlg.accept)
            ok_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            ok_button.setStyleSheet(
                """
                        QPushButton {
                            height: 32px;
                            background-color: #0ea5e9;
                            color: #f0f0f0;
                            border: 1px solid #ccc;
                            border-radius: 5px;    
                        }
                        QPushButton::hover {
                            background-color: #38bdf8
                        }
                    """
            )
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            button_layout.addWidget(ok_button)
            layout.addLayout(message_layout)
            layout.addLayout(button_layout)

            dlg.setLayout(layout)
            dlg.setWindowTitle("Invalid Input")
            result = dlg.exec()
            if result == QDialog.Accepted:
                print("Database reset confirmed")

    def load_settings(self):
        if os.path.exists(setting_path):
            settings = toml.load(setting_path)
            port = str(settings.get('port', ''))
            self.port_edit.setPlainText(port)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "ClipWarp"))
        self.Send.setText(_translate("MainWindow", "Send"))
        self.Paste.setText(_translate("MainWindow", "Paste"))
        self.label.setText(_translate("MainWindow", "ClipWarp"))

    def get_ip_address(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
