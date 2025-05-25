import json
from werkzeug.security import generate_password_hash

with open("user_db.json", "r") as f:
    raw_users = json.load(f)

# Neue Struktur mit Hashes
hashed_users = {}

for username, password in raw_users.items():
    hashed_users[username] = {
        "password": generate_password_hash(password)
    }

# Speichern
with open("user_db.json", "w") as f:
    json.dump(hashed_users, f, indent=2)

print("✅ Alle Passwörter wurden gehasht und gespeichert.")
