import os
import sqlite3
import time
from sqlite3 import Error

import pyperclip
import toml
from PyQt5.QtCore import QObject, pyqtSignal

db_path = os.path.join(
    os.path.expanduser("~"), ".config", "clipwarp", "assets", "clipwarp.db"
)

setting_path = os.path.join(
    os.path.expanduser("~"), ".config", "clipwarp", "assets", "setting.toml"
)


class Database(QObject):
    def create_connection(self, path):
        connection = None
        try:
            connection = sqlite3.connect(
                path, check_same_thread=False
            )  # Thread-safe SQLite connection
        except Error as e:
            print(f"The error '{e}' occurred")
        return connection

    def execute_query(self, connection, query, params=None):
        cursor = connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            connection.commit()
        except Error as e:
            print(f"The error '{e}' occurred")

    def execute_read_query(self, connection, query, params=None):
        cursor = connection.cursor()
        result = None
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"The error '{e}' occurred")
            return result

    def create_db(self):
        connection = self.create_connection(db_path)

        create_users_table = """
        CREATE TABLE IF NOT EXISTS users(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL
        );
        """

        create_clips_table = """
        CREATE TABLE IF NOT EXISTS clips(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          clips_text TEXT NOT NULL,
          user_id INTEGER NOT NULL,
          is_seen BOOLEAN DEFAULT FALSE,
          createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (user_id) REFERENCES users (id)
        );
        """

        self.execute_query(connection, create_users_table)
        self.execute_query(connection, create_clips_table)

        return connection

    def save_clip(self, text, user_id=1):
        connection = self.create_db()
        query = "INSERT INTO clips (clips_text, user_id) VALUES (?, ?)"
        self.execute_query(connection, query, (text, user_id))
        connection.close()


class ClipboardMonitor(QObject):
    new_clip = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.last_text = ""

    def running(self):
        if os.path.exists(setting_path):
            settings = toml.load(setting_path)
            return settings.get("monitor", True)
        else:
            return True

    def run(self):
        while self.running():
            try:
                current_text = pyperclip.paste()
                if current_text != self.last_text:
                    self.last_text = current_text
                    self.new_clip.emit(current_text)
            except Exception as e:
                print(f"Error monitoring clipboard: {e}")
            time.sleep(0.5)

    def stop(self):
        self.running = False
