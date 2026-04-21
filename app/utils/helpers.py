from functools import wraps
from flask import jsonify, request
import traceback
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('trainds')

def api_response(data=None, error=None, status=200):
    if error:
        return jsonify({'error': error}), status

    # Automatic Translation Logic
    try:
        # Get lang from: 1. JSON body, 2. Query params, 3. Header
        lang = 'en'
        if request.is_json:
            try:
                # Use silent=True to avoid breaking if body is not valid JSON
                body = request.get_json(silent=True) or {}
                lang = body.get('lang', 'en')
            except:
                pass
        
        if lang == 'en':
            lang = request.args.get('lang', 'en')
            
        if lang == 'hi' and data:
            from app.utils.translator import translate_recursive
            data = translate_recursive(data, 'hi')
    except Exception as e:
        logger.error(f"Translation bridge error: {e}")
        # Continue with original data if translation fails
        pass

    return jsonify(data), status

def handle_errors(f):
    """Decorator: catches exceptions and returns JSON error response."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return api_response(error=str(e), status=400)
        except Exception as e:
            logger.error(traceback.format_exc())
            return api_response(error='Internal server error', status=500)
    return wrapper
