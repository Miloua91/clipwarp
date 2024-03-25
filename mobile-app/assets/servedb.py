import sqlite3

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

CORS(app)


# Function to get a connection to the SQLite database
def get_db_connection():
    conn = sqlite3.connect("clipwarp.db")
    conn.row_factory = sqlite3.Row
    return conn


# Route to fetch all clips from the database
@app.route("/")
def get_clips():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clips")
    clips = cursor.fetchall()
    conn.close()

    # Convert the clips to JSON format
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

    # Execute the delete operation based on the clip ID
    cursor.execute("DELETE FROM clips WHERE id = ?", (clip_id,))
    conn.commit()

    conn.close()

    socketio.emit("refresh")

    # Return a success message or status code
    return jsonify({"message": "Clip deleted successfully"}), 200


@app.route("/reset", methods=["POST"])
def reset_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Execute SQL commands to delete all records from each table
    cursor.execute("DELETE FROM clips")
    # Add more DELETE statements if you have other tables

    conn.commit()
    conn.close()

    socketio.emit("refresh")

    # Return a success message
    return jsonify({"message": "Database reset successfully"}), 200


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", debug=True)
