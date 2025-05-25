from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import json

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

connected_pis = {}  # "pi_01": websocket_object (Simulation)

# === Routing für Seiten ===
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/dashboard')
def dashboard():
    if "username" not in session:
        return send_from_directory(app.static_folder, 'dashboard.html')
    
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Username + Passwort prüfen
        username = request.form.get("username")
        # Hier sollte die Passwortprüfung erfolgen
        ...
        session["username"] = username
        return redirect(url_for("dashboard"))  # Weiterleitung
    return send_from_directory(app.static_folder, "login.html")

@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        current_user = session["username"]
        old_pw = request.form["old"]
        new_pw = request.form["new"]

        with open("backend/user_db.json", "r") as f:
            users = json.load(f)

        if check_password_hash(users[current_user]["password"], old_pw):
            users[current_user]["password"] = generate_password_hash(new_pw)
            with open("backend/user_db.json", "w") as f:
                json.dump(users, f, indent=2)
            return "✅ Passwort wurde geändert"
        else:
            return "❌ Altes Passwort falsch"

    return send_from_directory("frontend", "change-password.html")


@app.route('/projekt')
def projekt():
    return send_from_directory(app.static_folder, 'projekt.html')

@app.route('/ueber-uns')
def ueber_uns():
    return send_from_directory(app.static_folder, 'ueber-uns.html')

@app.route('/shop')
def shop():
    return send_from_directory(app.static_folder, 'shop.html')

# === API: Verfügbare Fahrzeuge ===
@app.route('/api/available_vehicles')
def available_vehicles():
    return jsonify(list(connected_pis.keys()))

# === API: Fahrzeugsteuerung ===
@app.route('/api/drive', methods=['POST'])
def drive():
    data = request.json
    vid = data.get('vehicle_id')
    cmd = data.get('command')
    print(f"[DRIVE] {vid} ← {cmd}")
    # Beispiel: connected_pis[vid].send(cmd)
    return "OK"

# === API: Kamera bewegen ===
@app.route('/api/camera-control', methods=['POST'])
def camera_control():
    data = request.json
    vid = data.get('vehicle_id')
    direction = data.get('direction')
    print(f"[CAMERA] {vid} ← {direction}")
    return "OK"

# === Kamera-Livestream ===
@app.route('/stream/<vehicle_id>')
def stream(vehicle_id):
    # Beispiel: MJPEG-Pfad des Fahrzeuges zurückgeben
    return f"<img src='http://<ip-vom-pi>:8080/stream.mjpg'>"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
