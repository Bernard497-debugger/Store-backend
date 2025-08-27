from flask import Flask, request, jsonify, send_from_directory
import os
import json
import uuid

app = Flask(__name__)

# --- Folders ---
UPLOAD_FOLDER = os.path.join("/tmp", "uploads")  # Render free plan safe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
APPS_JSON = os.path.join(UPLOAD_FOLDER, "apps.json")

# --- Helpers ---
def read_apps():
    if not os.path.exists(APPS_JSON):
        return []
    with open(APPS_JSON, "r") as f:
        return json.load(f)

def write_apps(apps):
    with open(APPS_JSON, "w") as f:
        json.dump(apps, f, indent=4)

# --- Routes ---
@app.route("/", methods=["GET"])
def index():
    return "App Store Backend is running"

@app.route("/upload", methods=["POST"])
def upload_app():
    try:
        name = request.form.get("name")
        description = request.form.get("description")
        app_file = request.files.get("file")
        image_file = request.files.get("image")

        if not name or not description or not app_file or not image_file:
            return jsonify({"error":"All fields required"}), 400

        # Unique filenames
        app_filename = str(uuid.uuid4()) + "_" + app_file.filename
        image_filename = str(uuid.uuid4()) + "_" + image_file.filename

        # Save files
        app_file.save(os.path.join(UPLOAD_FOLDER, app_filename))
        image_file.save(os.path.join(UPLOAD_FOLDER, image_filename))

        # Save record in JSON
        apps = read_apps()
        apps.append({
            "name": name,
            "description": description,
            "file": "/uploads/" + app_filename,
            "image": "/uploads/" + image_filename
        })
        write_apps(apps)

        return jsonify({"message":"App uploaded successfully!"})
    except Exception as e:
        print("UPLOAD ERROR:", e)
        return jsonify({"error":"Server error during upload"}),500

@app.route("/uploads/<filename>")
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route("/api/apps", methods=["GET"])
def get_apps():
    return jsonify(read_apps())

# --- Run ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)