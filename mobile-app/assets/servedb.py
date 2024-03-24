import sqlite3

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)

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

    return jsonify(clip_data)


@app.route("/delete/<int:clip_id>", methods=["DELETE"])
def delete_clip(clip_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Execute the delete operation based on the clip ID
    cursor.execute("DELETE FROM clips WHERE id = ?", (clip_id,))
    conn.commit()

    conn.close()

    # Return a success message or status code
    return jsonify({"message": "Clip deleted successfully"}), 200


if __name__ == "__main__":
    app.run(debug=True)
