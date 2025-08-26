import os
import json
from flask import Flask, request, jsonify, send_from_directory, render_template_string
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

DATA_FILE = 'apps.json'
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/api/apps')
def get_apps():
    with open(DATA_FILE, 'r') as f:
        apps = json.load(f)
    return jsonify(apps)

@app.route('/upload', methods=['POST'])
def upload():
    name = request.form['name']
    description = request.form['description']

    file = request.files['file']
    image = request.files['image']

    filename = secure_filename(file.filename)
    image_name = secure_filename(image.filename)

    file.save(os.path.join(UPLOAD_FOLDER, filename))
    image.save(os.path.join(UPLOAD_FOLDER, image_name))

    app_data = {
        "name": name,
        "description": description,
        "file": f"/uploads/{filename}",
        "image": f"/uploads/{image_name}"
    }

    with open(DATA_FILE, 'r') as f:
        apps = json.load(f)
    apps.append(app_data)
    with open(DATA_FILE, 'w') as f:
        json.dump(apps, f, indent=2)

    return "App uploaded successfully! <a href='/admin'>Back</a>"

@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/admin')
def admin_panel():
    return send_from_directory('.', 'admin.html')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(debug=True)