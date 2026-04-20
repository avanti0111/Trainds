import jwt
import datetime
from flask import Blueprint, request, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import get_db
from app.utils.helpers import api_response, handle_errors

bp = Blueprint('auth', __name__)
SECRET_KEY = "trainds_internal_secure_key_123" # Minimalist secure fallback

@bp.route('/auth/signup', methods=['POST'])
@handle_errors
def signup():
    body = request.get_json(force=True)
    username = body.get('username')
    email = body.get('email')
    password = body.get('password')
    
    if not username or not email or not password:
        return api_response(error="Missing required fields", status=400)
        
    db = get_db()
    cursor = db.cursor()
    
    # Verify uniqueness
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        return api_response(error="Email already registered", status=409)
        
    hashed = generate_password_hash(password)
    cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                   (username, email, hashed))
    db.commit()
    return api_response({"message": "User created successfully"})

@bp.route('/auth/login', methods=['POST'])
@handle_errors
def login():
    body = request.get_json(force=True)
    email = body.get('email')
    password = body.get('password')
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    
    if not user or not check_password_hash(user['password'], password):
        return api_response(error="Invalid email or password", status=401)
        
    token = jwt.encode({
        "user_id": user['id'],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, SECRET_KEY, algorithm="HS256")
    
    return api_response({
        "token": token,
        "user": {
            "id": user['id'],
            "username": user['username'],
            "email": user['email']
        }
    })
