from flask import Flask, request, redirect, session, send_from_directory, jsonify
from auth import check_login
from websocket_server import send_command_to_pi, get_connected_pis
import os

app = Flask(__name__, static_folder="../frontend", static_url_path="")
app.secret_key = "supersecretkey"  # Durch sichere Schlüssel ersetzen

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if check_login(username, password):
            session["username"] = username
            return redirect("/dashboard")
        else:
            return "Login fehlgeschlagen", 403
    return send_from_directory(app.static_folder, "login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    return send_from_directory(app.static_folder, "dashboard.html")

@app.route("/api/available_vehicles")
def available_vehicles():
    return jsonify(get_connected_pis())

@app.route('/shop')
def shop():
    return send_from_directory(app.static_folder, 'shop.html')

@app.route("/api/drive", methods=["POST"])
def drive():
    if "user" not in session:
        return "Unauthorized", 401
    data = request.json
    command = data.get("command")
    vehicle_id = data.get("vehicle_id")
    send_command_to_pi(vehicle_id, command)
    return "Command sent"

if __name__ == "__main__":
    app.run(debug=True)