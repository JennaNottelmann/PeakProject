import websocket
import control

WS_URL = "ws://<SERVER-IP>:5000/ws/pi"

ws = websocket.WebSocket()
ws.connect(WS_URL)

ws.send("REGISTER pi_01")

while True:
    cmd = ws.recv()
    control.execute_command(cmd)