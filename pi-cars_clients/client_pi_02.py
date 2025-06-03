import websocket
import control
import time

# WebSocket-Adresse zum Server (achte darauf, dass IP & Port korrekt sind)
WS_URL = "ws://192.168.2.220:5000/ws/pi"

def connect_and_listen():
    while True:
        try:
            ws = websocket.WebSocket()
            ws.connect(WS_URL)
            ws.send("pi_02")  # Registrierung des Fahrzeugs beim Server
            print("[INFO] ✅ Verbunden mit Server")

            while True:
                cmd = ws.recv()
                print(f"[RECV] ⬅ {cmd}")
                control.execute_command(cmd)

        except Exception as e:
            print(f"[ERROR] Verbindung fehlgeschlagen: {e}")
            print("[INFO] ⏳ Neuer Verbindungsversuch in 5 Sekunden...")
            time.sleep(5)

if __name__ == "__main__":
    connect_and_listen()

