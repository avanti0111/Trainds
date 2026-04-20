from flask import Blueprint, request
from app.services.ml_service import predict_delay
from app.services.weather_service import get_weather_data
from app.utils.helpers import api_response, handle_errors

bp = Blueprint('delay', __name__)


@bp.route('/predict-delay', methods=['POST'])
@handle_errors
def delay_prediction():
    body = request.get_json(force=True)

    hour         = int(body.get('hour', 8))
    day_of_week  = int(body.get('day_of_week', 1))
    line         = str(body.get('line', 'Central'))
    station      = str(body.get('station', ''))

    if not (0 <= hour <= 23):
        return api_response(error='hour must be 0–23', status=400)
    if not (0 <= day_of_week <= 6):
        return api_response(error='day_of_week must be 0–6', status=400)

    weather = body.get('weather')
    rainfall_mm = body.get('rainfall_mm')

    if weather:
        rainfall_mm = float(rainfall_mm) if rainfall_mm is not None else 0.0
        weather_payload = {'condition': weather, 'rainfall': rainfall_mm, 'is_simulated': True}
    else:
        weather_payload = get_weather_data(station)
        weather_payload['is_simulated'] = False
        weather = weather_payload['condition']
        rainfall_mm = weather_payload['rainfall']

    result = predict_delay(hour, day_of_week, weather, rainfall_mm, line)
    
    # Bundle weather data to return dynamically back to frontend
    result['weather_used'] = weather_payload
    return api_response(result)
