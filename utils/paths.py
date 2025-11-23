import os

DATA_DIR = "data"
USERS_FILE = "users.json"

os.makedirs(DATA_DIR, exist_ok=True)
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        f.write("{}")
