import json
import bcrypt
import jwt
from datetime import datetime, timedelta
import os

SECRET_KEY = "supersecretkey123"
USERS_FILE = "users.json"

# Cargar usuarios
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

# Guardar usuarios
def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

# Hash de contraseña
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

# Verificar contraseña
def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

# Registrar usuario
def register_user(username: str, password: str, role: str):
    users = load_users()
    if username in users:
        return {"status": "error", "message": "Usuario ya registrado"}
    users[username] = {
        "password": hash_password(password),
        "role": role,
        "created_at": datetime.now().isoformat()
    }
    save_users(users)
    return {"status": "success", "message": "Usuario registrado correctamente"}

# Iniciar sesión
def login_user(username: str, password: str):
    users = load_users()
    if username not in users:
        return {"status": "error", "message": "Usuario no encontrado"}

    user = users[username]
    if not check_password(password, user["password"]):
        return {"status": "error", "message": "Contraseña incorrecta"}

    token = jwt.encode(
        {"username": username, "role": user["role"], "exp": datetime.utcnow() + timedelta(hours=2)},
        SECRET_KEY,
        algorithm="HS256"
    )
    return {"status": "success", "token": token, "role": user["role"]}

# Verificar token
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return {"status": "success", "data": payload}
    except jwt.ExpiredSignatureError:
        return {"status": "error", "message": "Token expirado"}
    except jwt.InvalidTokenError:
        return {"status": "error", "message": "Token inválido"}
