import json
import os

# Beispiel für eine einfache Authentifizierung
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_DB_PATH = os.path.join(BASE_DIR, "user_db.json")

# Beispiel für eine Benutzer-Datenbank
with open(USER_DB_PATH, "r") as f:
    USERS = json.load(f)

# Beispiel für eine Benutzer-Datenbank
def check_login(username, password):
    return USERS.get(username) == password