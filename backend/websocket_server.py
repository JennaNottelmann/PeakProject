connected_pis = {}

def register_pi(pi_id, socket):
    connected_pis[pi_id] = socket
    print(f"Registered Raspberry Pi: {pi_id}")

def send_command_to_pi(pi_id, command):
    socket = connected_pis.get(pi_id)
    if socket:
        socket.send(command)
        
def get_connected_pis():
    return list(connected_pis.keys())