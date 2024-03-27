import sqlite3

from PyQt5.QtCore import QObject


class Database(QObject):
    def create_connection(self, path):
        connection = None
        try:
            connection = sqlite3.connect(path)
        except Error as e:
            print(f"The error '{e}' occurred")

        return connection

    def execute_query(self, connection, query):
        cursor = connection.cursor()
        try:
            cursor.execute(query)
            connection.commit()
        except Error as e:
            print(f"The error '{e}' occurred")

    def create_db(self):
        connection = self.create_connection("./assets/clipwarp.db")

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
          FOREIGN KEY (user_id) REFERENCES users (id)
        );
        """

        self.execute_query(connection, create_users_table)
        self.execute_query(connection, create_clips_table)

        return connection
