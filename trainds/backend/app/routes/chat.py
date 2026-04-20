import jwt
from flask import Blueprint, request
from app.services.chat_service import process_chat_query
from app.utils.helpers import api_response, handle_errors
from app.routes.auth import SECRET_KEY
from app.db import get_db

bp = Blueprint('chat', __name__)

def get_user_from_token():
    auth = request.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        token = auth.split(' ')[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return payload.get('user_id')
        except:
            pass
    return None

@bp.route('/chat', methods=['POST'])
@handle_errors
def chat():
    body = request.get_json(force=True)
    message = body.get('message', '').strip()
    
    if not message:
        return api_response(error="Message cannot be empty", status=400)
        
    user_id = get_user_from_token()
    history = []
    db = None
    if user_id:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT message, sender FROM chat_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT 6", (user_id,))
        rows = cursor.fetchall()
        # reverse to get chronological order
        for r in reversed(rows):
            history.append({"role": "user" if r["sender"] == "user" else "model", "parts": [r["message"]]})

    reply = process_chat_query(message, history=history)
        
    if user_id and db:
        cursor = db.cursor()
        cursor.execute("INSERT INTO chat_history (user_id, message, sender) VALUES (?, ?, ?)", (user_id, message, "user"))
        cursor.execute("INSERT INTO chat_history (user_id, message, sender) VALUES (?, ?, ?)", (user_id, reply, "bot"))
        db.commit()
    
    return api_response({"reply": reply})

@bp.route('/chat/history', methods=['GET'])
@handle_errors
def chat_history():
    user_id = get_user_from_token()
    if not user_id:
        return api_response(error="Unauthorized", status=401)
        
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT message, sender, timestamp FROM chat_history WHERE user_id = ? ORDER BY timestamp ASC", (user_id,))
    
    history = [{"text": r['message'], "sender": r['sender'], "timestamp": r['timestamp']} for r in cursor.fetchall()]
    return api_response({"history": history})
