import os
import json
from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

# --- Persistent storage on Render ---
BASE_DIR = os.getenv("DB_DIR", "/var/data")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
DATA_FILE = os.path.join(BASE_DIR, "apps.json")

# --- Allowed file types ---
ALLOWED_APP_EXTENSIONS = {"apk", "zip", "exe", "msi", "dmg", "pkg"}
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

# --- Helper functions ---
def load_apps():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump([], f)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_apps(apps):
    with open(DATA_FILE, "w") as f:
        json.dump(apps, f, indent=2)

def allowed_file(filename, allowed):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed

# --- Routes ---
@app.route("/")
def index():
    apps = load_apps()
    return render_template("index.html", apps=apps)

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/upload", methods=["POST"])
def upload():
    name = request.form.get("name")
    description = request.form.get("description")
    app_file = request.files.get("file")
    image_file = request.files.get("image")

    if not all([name, description, app_file, image_file]):
        return "Missing required fields", 400

    if not allowed_file(app_file.filename, ALLOWED_APP_EXTENSIONS):
        return f"Invalid app file type: {app_file.filename}", 400
    if not allowed_file(image_file.filename, ALLOWED_IMAGE_EXTENSIONS):
        return f"Invalid image file type: {image_file.filename}", 400

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
    return redirect(url_for("index"))

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return app.send_static_file(os.path.join("uploads", filename))

@app.route("/api/apps")
def api_apps():
    return jsonify(load_apps())

# --- Run app ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
