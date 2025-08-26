import os
import json
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow frontend requests from any origin

# --- Storage Setup ---
BASE_DIR = "uploads"  # Free plan: no persistent disk
os.makedirs(BASE_DIR, exist_ok=True)

UPLOAD_FOLDER = os.path.join(BASE_DIR)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DATA_FILE = os.path.join(BASE_DIR, "apps.json")
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

# --- Allowed file extensions ---
ALLOWED_APP_EXTENSIONS = {"apk", "zip", "exe", "msi", "dmg", "pkg"}
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

# --- Helpers ---
def load_apps():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_apps(apps):
    with open(DATA_FILE, "w") as f:
        json.dump(apps, f, indent=2)

def allowed_file(filename, allowed_ext):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_ext

# --- Routes ---
@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "Backend is live"})

@app.route("/api/apps", methods=["GET"])
def get_apps():
    return jsonify(load_apps())

@app.route("/upload", methods=["POST"])
def upload_app():
    name = request.form.get("name")
    description = request.form.get("description")
    app_file = request.files.get("file")
    image_file = request.files.get("image")

    if not all([name, description, app_file, image_file]):
        return jsonify({"error": "Missing required fields"}), 400

    if not allowed_file(app_file.filename, ALLOWED_APP_EXTENSIONS):
        return jsonify({"error": "Invalid app file type"}), 400
    if not allowed_file(image_file.filename, ALLOWED_IMAGE_EXTENSIONS):
        return jsonify({"error": "Invalid image file type"}), 400

    app_filename = secure_filename(app_file.filename)
    image_filename = secure_filename(image_file.filename)

    app_file.save(os.path.join(UPLOAD_FOLDER, app_filename))
    image_file.save(os.path.join(UPLOAD_FOLDER, image_filename))

    apps = load_apps()
    apps.append({
        "name": name,
        "description": description,
        "file": f"/uploads/{app_filename}",
        "image": f"/uploads/{image_filename}"
    })
    save_apps(apps)

    return jsonify({"message": "App uploaded successfully!"}), 201

@app.route("/uploads/<path:filename>")
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=False)

# --- Run ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render sets $PORT automatically
    app.run(host="0.0.0.0", port=port)
