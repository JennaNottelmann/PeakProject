import os
from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import json

# Pfad zum Ordner, in dem app.py liegt
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_DB_PATH = os.path.join(BASE_DIR, "user_db.json")

def load_users():
    with open(USER_DB_PATH, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_DB_PATH, "w") as f:
        json.dump(users, f, indent=4)

app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.secret_key = "dein_geheimer_schlüssel"
CORS(app)

connected_pis = {}  # "pi_01": websocket_object (Simulation)

# === Routing für Seiten ===
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route("/check-login")
def check_login():
    return jsonify({"logged_in": "username" in session})

@app.route('/dashboard')
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))
    return send_from_directory(app.static_folder, 'dashboard.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        users = load_users()

        if username in users and check_password_hash(users[username]["password"], password):
            session["username"] = username
            return redirect(url_for("dashboard"))
        else:
            return "❌ Falsche Anmeldedaten."

    return send_from_directory(app.static_folder, "login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        current_user = session["username"]
        old_pw = request.form["old"]
        new_pw = request.form["new"]

        users = load_users()
        if check_password_hash(users[current_user]["password"], old_pw):
            users[current_user]["password"] = generate_password_hash(new_pw)
            save_users(users)
            return "✅ Passwort geändert"
        else:
            return "❌ Altes Passwort falsch"

    return send_from_directory(app.static_folder, "change-password.html")

@app.route('/projekt')
def projekt():
    return send_from_directory(app.static_folder, 'projekt.html')

@app.route('/ueber-uns')
def ueber_uns():
    return send_from_directory(app.static_folder, 'ueber-uns.html')

@app.route('/shop')
def shop():
    return send_from_directory(app.static_folder, 'shop.html')

@app.route('/api/available_vehicles')
def available_vehicles():
    return jsonify(list(connected_pis.keys()))

@app.route('/api/drive', methods=['POST'])
def drive():
    data = request.json
    vid = data.get('vehicle_id')
    cmd = data.get('command')
    print(f"[DRIVE] {vid} ← {cmd}")
    return "OK"

@app.route('/api/camera-control', methods=['POST'])
def camera_control():
    data = request.json
    vid = data.get('vehicle_id')
    direction = data.get('direction')
    print(f"[CAMERA] {vid} ← {direction}")
    return "OK"

@app.route('/stream/<vehicle_id>')
def stream(vehicle_id):
    return f"<img src='http://<ip-vom-pi>:8080/stream.mjpg'>"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
