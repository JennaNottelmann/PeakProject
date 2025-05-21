from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

connected_pis = {}  # "pi_01": websocket_object (Simulation)

# === Routing für Seiten ===
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/dashboard')
def dashboard():
    return send_from_directory(app.static_folder, 'dashboard.html')

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
