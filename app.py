from flask import Flask, request, jsonify
import os
import subprocess
import uuid

app = Flask(name)

DOWNLOAD_DIR = "/tmp/videos"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route("/")
def home():
return "Spiderlives Downloader API is running!"

@app.route("/download", methods=["POST"])
def download():
data = request.get_json(silent=True) or {}
url = data.get("url", "").strip()

if not url.startswith(("https://", "http://")):
    return jsonify({"error": "Please provide a valid URL"}), 400

try:
    filename = str(uuid.uuid4())
    output_template = os.path.join(
        DOWNLOAD_DIR, f"{filename}.%(ext)s"
    )

    result = subprocess.run(
        [
            "yt-dlp",
            "--no-playlist",
            "--max-filesize", "45M",
            "-f", "best[ext=mp4][height<=720]/best[height<=720]",
            "-o", output_template,
            url
        ],
        capture_output=True,
        text=True,
        timeout=120
    )

    if result.returncode != 0:
        return jsonify({
            "error": "Download failed. Check the URL and your permission to download the video."
        }), 400

    matching_files = [
        os.path.join(DOWNLOAD_DIR, name)
        for name in os.listdir(DOWNLOAD_DIR)
        if name.startswith(filename + ".")
    ]

    if not matching_files:
        return jsonify({"error": "No video file was created"}), 500

    return jsonify({
        "message": "Video downloaded successfully",
        "file_path": matching_files[0]
    })

except subprocess.TimeoutExpired:
    return jsonify({"error": "Download timed out"}), 504
except Exception:
    return jsonify({"error": "An unexpected error occurred"}), 500

if name == "main":
app.run(
host="0.0.0.0",
port=int(os.environ.get("PORT", 10000))
)
