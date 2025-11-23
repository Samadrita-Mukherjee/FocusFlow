import json
from utils.paths import USERS_FILE
from models.user import User

def load_users():
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2)

def register():
    users = load_users()
    print('--- Register ---')
    username = input('Choose username: ').strip()
    if username in users:
        print('Username exists')
        return
    password = input('Choose password: ').strip()
    users[username] = {'password': password}
    save_users(users)
    print('Registered. Please login.')

def login():
    users = load_users()
    print('--- Login ---')
    username = input('Username: ').strip()
    password = input('Password: ').strip()
    if username in users and users[username]['password'] == password:
        print(f'Welcome {username}')
        return User(username)
    print('Invalid credentials')
    return None

