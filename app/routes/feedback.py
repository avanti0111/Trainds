from flask import Blueprint, request
from app.utils.helpers import api_response, handle_errors
from app.db import get_db
from app.routes.chat import get_user_from_token

bp = Blueprint('feedback', __name__)

@bp.route('/feedback', methods=['POST'])
@handle_errors
def submit_feedback():
    user_id = get_user_from_token()
    if not user_id:
        return api_response(error="Unauthorized. Please log in first.", status=401)
        
    body = request.get_json(force=True)
    rating = body.get('rating')
    comment = body.get('comment', '').strip()
    
    if not isinstance(rating, int) or not (1 <= rating <= 5):
        return api_response(error="Rating must be an integer between 1 and 5", status=400)
        
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO feedback (user_id, rating, comment) VALUES (?, ?, ?)",
        (user_id, rating, comment)
    )
    db.commit()
    
    return api_response({"message": "Thank you for your feedback!"})
