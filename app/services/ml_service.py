"""
ML service: loads the trained XGBoost/RandomForest model and runs predictions.
Falls back to a rule-based heuristic if the model file is not found.
"""

import os
import numpy as np
import logging

logger = logging.getLogger('trainds')

_model = None
_encoder = None

WEATHER_MAP = {
    'Clear': 0, 'Clouds': 1, 'Rain': 2, 'Thunderstorm': 3,
    'Mist': 4, 'Haze': 5, 'Drizzle': 2, 'Snow': 3,
}

def _load_model():
    global _model, _encoder
    if _model is not None:
        return _model
    try:
        import joblib
        base = os.path.dirname(os.path.abspath(__file__))
        
        # Check multiple potential locations for the model file
        search_paths = [
            os.path.abspath(os.path.join(base, "..", "..", "ml", "model", "delay_model.pkl")), # Local/Dev
            os.path.abspath(os.path.join(base, "..", "..", "..", "ml", "model", "delay_model.pkl")), # Alternative
            os.path.join(os.getcwd(), "ml", "model", "delay_model.pkl"),             # Root Relative
            os.getenv('MODEL_PATH', '')                                             # Environment Override
        ]

        model_path = None
        for path in search_paths:
            if path and os.path.exists(path):
                model_path = path
                break

        if model_path:
            logger.info("Found ML model at: %s", model_path)
            _model = joblib.load(model_path)
        else:
            logger.warning("Model file not found in any expected location – using heuristic predictor. Searched: %s", search_paths)
    except Exception as e:
        logger.error('Failed to load model: %s', e)
    return _model


def _heuristic_predict(hour: int, day_of_week: int,
                        weather: str, rainfall_mm: float,
                        line: str) -> float:
    """
    Rule-based fallback when no trained model is available.
    Mirrors the same logic used to generate training labels.
    """
    delay = 0.0

    # Peak hours
    if 7 <= hour <= 10 or 17 <= hour <= 21:
        delay += 6.0
    elif 10 < hour < 17:
        delay += 1.5
    else:
        delay += 0.5

    # Day effect
    if day_of_week in (0, 6):      # weekend
        delay -= 2.0
    elif day_of_week == 5:         # Saturday
        delay -= 1.0

    # Weather
    weather_penalty = {
        'Thunderstorm': 8.0, 'Rain': 5.0, 'Drizzle': 2.5,
        'Mist': 2.0, 'Haze': 1.5, 'Clouds': 0.5, 'Clear': 0.0,
    }
    delay += weather_penalty.get(weather, 0.0)
    delay += rainfall_mm * 0.06

    # Line factor
    if line == 'Central':
        delay += 1.5
    elif line == 'Harbour':
        delay += 1.0

    return max(round(delay, 1), 0.0)


def predict_delay(hour: int, day_of_week: int,
                  weather: str, rainfall_mm: float,
                  line: str = None,
                  station: str = None) -> dict:
    """
    Returns prediction dict:
    { predicted_delay_min, risk_level, factors, model }
    """
    if not line:
        line = "Central"
    
    model = _load_model()
    weather_code = WEATHER_MAP.get(weather, 0)

    if model:
        try:
            features = np.array([[hour, day_of_week, weather_code, rainfall_mm]])
            pred     = float(model.predict(features)[0])
        except Exception as e:
            logger.error('Model predict error: %s', e)
            pred = _heuristic_predict(hour, day_of_week, weather, rainfall_mm, line)
        model_name = 'XGBoost (trained)'
    else:
        pred       = _heuristic_predict(hour, day_of_week, weather, rainfall_mm, line)
        model_name = 'Rule-based heuristic'

    # Adjust prediction slightly by line
    if line == "Central":
        pred += 1.2
    elif line == "Harbour":
        pred += 0.8
    elif line == "Western":
        pred += 0.6

    
    
    # Small station-based variation
    if station:
        station_factor = (sum(ord(c) for c in station) % 5) * 0.2
        pred += station_factor

    pred = max(round(pred, 1), 0.0)

    # Station delay factor
    station_factor = {
        "Dadar": 2.0,
        "Kurla": 1.5,
        "Thane": 1.2,
        "Kalyan": 1.4,
        "Ghatkopar": 1.0,
        "Andheri": 1.6,
        "Borivali": 1.3,
        "CST": 1.8
    }

    # Line delay factor
    line_factor = {
        "Central": 1.5,
        "Western": 1.0,
        "Harbour": 1.2
    }

    if station:
        pred += station_factor.get(station, 0)

    if line:
        pred += line_factor.get(line, 0)

    # Risk level
    risk = 'Low' if pred <= 3 else 'Medium' if pred <= 8 else 'High'

    # Human-readable factors
    factors = []
    if 7 <= hour <= 10 or 17 <= hour <= 21:
        factors.append('Peak hour – high congestion')
    if day_of_week in (1, 2, 3, 4, 5):
        factors.append('Weekday – heavy commuter traffic')
    if weather in ('Rain', 'Thunderstorm', 'Drizzle'):
        factors.append(f'Weather: {weather} – signal and track delays expected')
    if rainfall_mm > 20:
        factors.append(f'High rainfall ({rainfall_mm} mm) – waterlogging risk')
    if line == 'Central':
        factors.append('Central line – historically higher delay frequency')
    if not factors:
        factors.append('Normal operating conditions')

    return {
        'predicted_delay_min': pred,
        'risk_level':          risk,
        'factors':             factors,
        'model':               model_name,
    }
