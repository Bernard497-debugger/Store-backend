import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- Persistent DB path for Render ---
BASE_DIR = os.getenv("DB_DIR", "/var/data")  # /var/data is Render disk mount
os.makedirs(BASE_DIR, exist_ok=True)
DB_PATH = os.path.join(BASE_DIR, "appstore.db")

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# --- Example App model ---
class AppStoreItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    download_link = db.Column(db.String(200), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "download_link": self.download_link,
        }

# --- Routes ---
@app.route("/")
def index():
    apps = AppStoreItem.query.all()
    return render_template("index.html", apps=apps)

@app.route("/add", methods=["POST"])
def add_app():
    name = request.form["name"]
    description = request.form["description"]
    download_link = request.form["download_link"]

    new_app = AppStoreItem(name=name, description=description, download_link=download_link)
    db.session.add(new_app)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/api/apps")
def api_apps():
    apps = AppStoreItem.query.all()
    return jsonify([app.to_dict() for app in apps])

# --- Run locally ---
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)