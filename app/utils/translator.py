from deep_translator import GoogleTranslator
from functools import lru_cache

# Caching translations indefinitely in active memory to prevent huge delays on recurring routes 
@lru_cache(maxsize=1024)
def _cached_translate(text, target_lang):
    if not text or not text.strip():
        return text
    if target_lang == 'en':
        return text
        
    try:
        translator = GoogleTranslator(source='auto', target=target_lang)
        return translator.translate(text)
    except Exception as e:
        print(f"Translation Error gracefully suppressed: {e}")
        return text

def translate_text(text, target_lang="hi"):
    """
    Safely translates texts into Hindi or specified target using Google Translate.
    Defaults to English silently if translations drop or string is empty natively.
    """
    try:
        if not target_lang or target_lang == 'en':
            return text
        return _cached_translate(text, target_lang)
    except:
        return text

def translate_recursive(data, target_lang="hi"):
    """
    Deeply traverses lists and dicts to translate all string values.
    Skips keys in dictionaries (translates only values).
    """
    if not target_lang or target_lang == 'en':
        return data

    if isinstance(data, str):
        # Improved heuristic: Only translate if it looks like actual text
        # Skip if: numeric, very short (likely ID/code), or no alphabetic characters
        if data.isdigit() or len(data) <= 2:
            return data
        
        # Heuristic: must contain at least one character that is part of a language
        import re
        if not re.search(r'[a-zA-Z]', data):
            return data
            
        return translate_text(data, target_lang)
    
    if isinstance(data, dict):
        return {k: translate_recursive(v, target_lang) for k, v in data.items()}
    
    if isinstance(data, list):
        return [translate_recursive(item, target_lang) for item in data]
    
    return data
