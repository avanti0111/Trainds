from flask import Blueprint, request
from app.utils.helpers import api_response, handle_errors
from app.utils.translator import translate_text

bp = Blueprint('translation', __name__)

@bp.route('/translate', methods=['POST'])
@handle_errors
def translate_texts():
    body = request.get_json(force=True)
    texts = body.get('texts', [])
    target_lang = body.get('target_lang', 'hi')
    
    if not isinstance(texts, list):
        return api_response(error="texts must be a list of strings", status=400)
    
    translations = {}
    for text in texts:
        if not text or not isinstance(text, str):
            continue
        try:
            translated = translate_text(text, target_lang)
            translations[text] = translated
        except Exception as e:
            # Fallback to original text on error
            translations[text] = text
            
    return api_response({"translations": translations})
