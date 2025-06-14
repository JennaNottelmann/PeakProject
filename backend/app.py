import os
import json
from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for, render_template, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash

# === Pfade
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_DB_PATH = os.path.join(BASE_DIR, "user_db.json")

# === App Setup
app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.secret_key = "dein_geheimer_schlüssel"
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# === Nutzerdatenbank laden/speichern
def load_users():
    with open(USER_DB_PATH, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_DB_PATH, "w") as f:
        json.dump(users, f, indent=4)

# === Connected Pi Registry
connected_pis = {}  # {"pi_02": {"sid": ..., "ip": ...}}

@socketio.on("register_pi")
def register_pi(data):
    pi_id = data["pi_id"]
    ip = data.get("ip", "unknown")
    connected_pis[pi_id] = {
        "sid": request.sid,
        "ip": ip
    }
    print(f"[SERVER] Pi {pi_id} registriert mit IP {ip}")

    emit("registration_success", {"pi_id": pi_id, "ip": ip})
    
    #  Diese Zeile fügt das Fahrzeug dem Dashboard hinzu:
    emit("pi_list", [{"id": pi_id, "ip": info["ip"]} for pi_id, info in connected_pis.items()], broadcast=True)




@socketio.on("request_pi_list")
def handle_request_pi_list():
    pi_list = [{"id": pi_id, "ip": info["ip"]} for pi_id, info in connected_pis.items()]
    print("[SERVER] Sende aktuelle Pi-Liste an Dashboard:", connected_pis)
    emit("pi_list", [
        {"id": pid, "ip": info["ip"]}
        for pid, info in connected_pis.items()
    ])





@socketio.on("disconnect")
def handle_disconnect():
    disconnected = None
    for pi_id, info in list(connected_pis.items()):
        if info["sid"] == request.sid:
            disconnected = pi_id
            del connected_pis[pi_id]
            break
    print(f"[WS] Verbindung getrennt: {disconnected or 'Unbekannt'}")

@socketio.on("status_update")
def status_update(data):
    pi_id = data.get("pi_id")
    if pi_id in connected_pis:
        connected_pis[pi_id].update({
            "battery": data.get("battery"),
            "temp": data.get("temp"),
            "latency": data.get("latency"),
        })


def send_command_to_pi(pi_id, command):
    info = connected_pis.get(pi_id)
    if info:
        sid = info["sid"]
        socketio.emit("command", command, to=sid)
        print(f"[WS] → {pi_id}: {command}")
    else:
        print(f"[WS] Kein Pi verbunden für ID: {pi_id}")

# === Seiten-Routing
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

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

@app.route("/check-login")
def check_login():
    return jsonify({"logged_in": "username" in session})

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

# === Weitere Seiten
@app.route('/projekt')
def projekt():
    return send_from_directory(app.static_folder, 'projekt.html')

@app.route('/ueber-uns')
def ueber_uns():
    return send_from_directory(app.static_folder, 'ueber-uns.html')

@app.route('/shop')
def shop():
    return send_from_directory(app.static_folder, 'shop.html')

# === REST API
@app.route('/api/available_vehicles')
def available_vehicles():
        return jsonify([
            {"id": k, "ip": v.get("ip", "unknown")}
            for k, v in connected_pis.items()
        ])

@app.route('/api/drive', methods=['POST'])
def drive():
    data = request.json
    vid = data.get('vehicle_id')
    cmd = data.get('command')
    print(f"[API] {vid} ← {cmd}")
    send_command_to_pi(vid, cmd)
    return "OK"

@app.route('/api/status')
def status():
    vehicle_id = request.args.get("vehicle_id")
    info = connected_pis.get(vehicle_id)
    if not info:
        return jsonify({"battery": 0, "latency": 0, "temp": 0})
    return jsonify({
        "battery": info.get("battery", 0),
        "latency": info.get("latency", 0),
        "temp": info.get("temp", 0)
    })

@socketio.on("latency_ping")
def handle_latency_ping(data):
    pi_id = data.get("vehicle_id")
    info = connected_pis.get(pi_id)
    if info:
        sid = info["sid"]
        socketio.emit("latency_pong", {}, to=sid)



@app.route('/api/camera-start', methods=['POST'])
def camera_start():
    data = request.json
    vid = data.get('vehicle_id')
    print(f"[CAMERA] {vid} → STARTE MJPG-Streamer")
    # Kamera-Startcode einfügen, wenn gewünscht
    return "OK"

@app.route('/api/camera-control', methods=['POST'])
def camera_control():
    data = request.json
    vid = data.get('vehicle_id')
    direction = data.get('direction')
    print(f"[CAMERA] {vid} ← {direction}")
    send_command_to_pi(vid, f"camera:{direction}")
    return "OK"

@socketio.on("camera_frame")
def handle_camera_frame(data):
    vehicle_id = data.get("pi_id")
    frame_data = data.get("frame")
    # Weiterleiten an Frontend
    emit("camera_frame", {"vehicle_id": vehicle_id, "frame": frame_data}, broadcast=True)



@app.route('/api/run_challenge', methods=["POST"])
def run_challenge():
    data = request.json
    vehicle_id = data.get("vehicle_id")
    challenge = data.get("challenge")
    if not vehicle_id or not challenge:
        return jsonify({"error": "Fehlende Daten"}), 400

    send_command_to_pi(vehicle_id, f"run_challenge:{challenge}")
    return jsonify({"status": "gestartet", "challenge": challenge})




# === Server starten
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
