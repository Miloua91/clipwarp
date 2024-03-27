import sqlite3

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

CORS(app)


def get_db_connection():
    conn = sqlite3.connect("./assets/clipwarp.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def get_clips():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clips")
    clips = cursor.fetchall()
    conn.close()

    clip_data = [
        {"id": clip["id"], "clips_text": clip["clips_text"], "user_id": clip["user_id"]}
        for clip in clips
    ]

    socketio.emit("refresh")

    return jsonify(clip_data)


@app.route("/delete/<int:clip_id>", methods=["DELETE"])
def delete_clip(clip_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM clips WHERE id = ?", (clip_id,))
    conn.commit()

    conn.close()

    socketio.emit("refresh")

    return jsonify({"message": "Clip deleted successfully"}), 200


@app.route("/reset", methods=["POST"])
def reset_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM clips")

    conn.commit()
    conn.close()

    socketio.emit("refresh")

    return jsonify({"message": "Database reset successfully"}), 200


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", debug=True)
