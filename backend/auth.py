import json

with open("/backend/user_db.json", "r") as f:
    USERS = json.load(f)

def check_login(username, password):
    return USERS.get(username) == password