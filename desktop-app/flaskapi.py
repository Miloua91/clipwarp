import os
import sqlite3

from engineio.async_drivers import gevent
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from PyQt5.QtCore import QObject

setting_path = os.path.join(
    os.path.expanduser("~"), ".config", "clipwarp", "assets", "setting.txt"
)

db_path = os.path.join(
    os.path.expanduser("~"), ".config", "clipwarp", "assets", "clipwarp.db"
)


class FlaskAPI(QObject):
    def __init__(self):
        super(FlaskAPI, self).__init__()
        self.app = Flask(__name__)
        CORS(self.app)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.app.add_url_rule("/", "get_clips", self.get_clips, methods=["GET"])
        self.app.add_url_rule(
            "/edit/<int:clip_id>",
            "edit_clip",
            self.edit_clip,
            methods=["PUT"],
        )
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

    def load_port(self):
        if os.path.exists(setting_path):
            with open(setting_path, "r") as f:
                port = f.read()
                return int(port) + 1
        else:
            return 42070

    def start(self):
        self.socketio.run(self.app, host="0.0.0.0", port=self.load_port())

    def get_db_connection(self):
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_clips(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id
            FROM clips
            ORDER BY createdAt DESC
            LIMIT 1
            """
        )
        latest_clip = cursor.fetchone()
        latest_clip_id = latest_clip["id"] if latest_clip else None

        cursor.execute(
            """
            SELECT clips.id, clips.clips_text, clips.user_id, users.name, createdAt
            FROM clips
            JOIN users ON clips.user_id = users.id
        """
        )
        clips = cursor.fetchall()
        conn.close()

        clip_data = [
            {
                "id": clip["id"],
                "clips_text": clip["clips_text"],
                "user_id": clip["user_id"],
                "user_name": clip["name"],
                "date": clip["createdAt"],
                "is_latest": (clip["id"] == latest_clip_id),
            }
            for clip in clips
        ]

        self.socketio.emit("refresh")

        return jsonify(clip_data)

    def edit_clip(self, clip_id):
        data = request.get_json()

        if "clip" not in data:
            return jsonify({"error": "Clip data is required"}), 400

        clip = data["clip"]

        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE clips SET clips_text = ? WHERE id = ?",
            (
                clip,
                clip_id,
            ),
        )
        conn.commit()

        conn.close()

        self.socketio.emit("edit")

        return jsonify({"message": "Clip edited successfully"}), 200

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
