import websocket
import control

WS_URL = "ws://192.168.2.46:5000/ws/pi"

ws = websocket.WebSocket()
ws.connect(WS_URL)

ws.send("REGISTER pi_02")

while True:
    cmd = ws.recv()
    control.execute_command(cmd)