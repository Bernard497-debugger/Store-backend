import os
import json
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

# --- Paths ---
BASE_DIR = os.getenv("DB_DIR", "/var/data")  # persistent disk on Render
os.makedirs(BASE_DIR, exist_ok=True)
DATA_FILE = os.path.join(BASE_DIR, "apps.json")

# --- Helpers ---
def load_apps():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump([], f)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_apps(apps):
    with open(DATA_FILE, "w") as f:
        json.dump(apps, f, indent=2)

# --- Routes ---
@app.route("/")
def index():
    apps = load_apps()
    return render_template("index.html", apps=apps)

@app.route("/admin", methods=["GET"])
def admin():
    return render_template("admin.html")

@app.route("/upload", methods=["POST"])
def upload():
    name = request.form.get("name")
    description = request.form.get("description")
    file = request.form.get("file") or request.files.get("file")
    image = request.form.get("image") or request.files.get("image")

    if not name or not description:
        return "Missing required fields", 400

    apps = load_apps()
    apps.append({
        "name": name,
        "description": description,
        "file": file.filename if file else "",
        "image": image.filename if image else ""
    })
    save_apps(apps)
    return redirect(url_for("index"))

@app.route("/api/apps")
def api_apps():
    return jsonify(load_apps())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
