import platform

try:
    if platform.system() == "Linux":
        from picarx import Picarx
        px = Picarx()
        USE_HARDWARE = True
    else:
        raise ImportError("Nicht auf Raspberry Pi")
except ImportError:
    print("[⚠ MOCK] Hardware nicht erkannt – SIMULATION aktiviert")
    USE_HARDWARE = False
    px = None  # Falls später verwendet

def execute_command(cmd):
    actions = {
        "forward": forward,
        "backward": backward,
        "left": left,
        "right": right,
        "stop": stop,
        "hammer": hammer
    }

    func = actions.get(cmd)
    if func:
        func()
    else:
        print(f"[WARN] ❓ Unbekannter Befehl: {cmd}")

def forward():
    if USE_HARDWARE:
        px.set_dir_servo_angle(0)
        px.forward(50)
    else:
        print("[SIMULATION] → forward()")

def backward():
    if USE_HARDWARE:
        px.set_dir_servo_angle(0)
        px.backward(50)
    else:
        print("[SIMULATION] → backward()")

def left():
    if USE_HARDWARE:
        px.set_dir_servo_angle(-35)
        px.forward(50)
    else:
        print("[SIMULATION] → left()")

def right():
    if USE_HARDWARE:
        px.set_dir_servo_angle(35)
        px.forward(50)
    else:
        print("[SIMULATION] → right()")

def stop():
    if USE_HARDWARE:
        px.stop()
    else:
        print("[SIMULATION] → stop()")

def hammer():
    print("[ACTION] 🔨 hammer() ausgelöst (Demo/Spezialfunktion)")
    if USE_HARDWARE:
        px.set_dir_servo_angle(0)
        px.forward(50)
        # Hier könnte eine echte Hammer-Funktion implementiert werden
    else:
        print("[SIMULATION] → hammer()")