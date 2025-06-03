connected_pis = {}  # { "pi_01": {"socket": ws, "ip": "192.168...." }}

def register_pi(pi_id, socket, ip):
    connected_pis[pi_id] = {"socket": socket, "ip": ip}
    print(f"Registered Raspberry Pi: {pi_id}")

def send_command_to_pi(pi_id, command):
    socket = connected_pis.get(pi_id)
    if socket:
        socket.send(command)
        
def get_connected_pis():
    return list(connected_pis.keys())