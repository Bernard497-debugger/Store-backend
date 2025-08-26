from flask import Flask, request, jsonify
import os
import json

app = Flask(__name__)

# Create a writable data folder inside the project
DATA_FOLDER = "data"
os.makedirs(DATA_FOLDER, exist_ok=True)

# Path to JSON file
APPS_FILE = os.path.join(DATA_FOLDER, "apps.json")

# Helper to read JSON
def read_apps():
    if not os.path.exists(APPS_FILE):
        return []
    with open(APPS_FILE, "r") as f:
        return json.load(f)

# Helper to write JSON
def write_apps(apps):
    with open(APPS_FILE, "w") as f:
        json.dump(apps, f, indent=4)

# --- Routes ---

# Get all apps
@app.route("/apps", methods=["GET"])
def get_apps():
    apps = read_apps()
    return jsonify(apps)

# Add a new app
@app.route("/apps", methods=["POST"])
def add_app():
    data = request.get_json()
    if not data or "name" not in data or "url" not in data:
        return jsonify({"error": "name and url required"}), 400

    apps = read_apps()
    apps.append({
        "name": data["name"],
        "url": data["url"]
    })
    write_apps(apps)
    return jsonify({"message": "App added"}), 201

# Health check
@app.route("/", methods=["GET"])
def index():
    return "App Store Backend is running"

# --- Run ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render uses $PORT
    app.run(host="0.0.0.0", port=port)
