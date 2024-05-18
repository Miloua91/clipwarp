import sqlite3

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from PyQt5.QtCore import QObject


class FlaskAPI(QObject):
    def __init__(self):
        super(FlaskAPI, self).__init__()
        self.app = Flask(__name__)
        CORS(self.app)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.app.add_url_rule("/", "get_clips", self.get_clips, methods=["GET"])
        self.app.add_url_rule(
            "/delete/<int:clip_id>",
            "delete_clip",
            self.delete_clip,
            methods=["DELETE"],
        )
        self.app.add_url_rule(
            "/reset",
            "reset",
            self.reset_database,
            methods=["POST"],
        )

    def start(self):
        self.socketio.run(self.app, host="0.0.0.0")

    def get_db_connection(self):
        conn = sqlite3.connect("./assets/clipwarp.db")
        conn.row_factory = sqlite3.Row
        return conn

    def get_clips(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clips")
        clips = cursor.fetchall()
        conn.close()

        clip_data = [
            {
                "id": clip["id"],
                "clips_text": clip["clips_text"],
                "user_id": clip["user_id"],
            }
            for clip in clips
        ]

        self.socketio.emit("refresh")

        return jsonify(clip_data)

    def delete_clip(self, clip_id):
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM clips WHERE id = ?", (clip_id,))
        conn.commit()

        conn.close()

        self.socketio.emit("delete")

        return jsonify({"message": "Clip deleted successfully"}), 200

    def reset_database(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM clips")

        conn.commit()
        conn.close()

        self.socketio.emit("reset")

        return jsonify({"message": "Database reset successfully"}), 200
