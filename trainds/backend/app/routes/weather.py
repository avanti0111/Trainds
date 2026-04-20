from flask import Blueprint, request
from app.services.weather_service import get_weather
from app.utils.helpers import api_response, handle_errors

bp = Blueprint('weather', __name__)


@bp.route('/weather', methods=['GET'])
@handle_errors
def weather():
    city   = request.args.get('city', 'Mumbai')
    result = get_weather(city)
    return api_response(result)
