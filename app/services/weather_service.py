import requests
import time
import json
import os

_CACHE = {}
CACHE_TTL = 600  # 10 minutes cache
_COORDS_CACHE = {}

def get_coords(station_name: str):
    if not _COORDS_CACHE:
        base = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base, '..', '..', '..', 'data', 'routes.json')
        path = os.path.normpath(path)
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.load(f)
                for s in data.get('stations', []):
                    _COORDS_CACHE[s['name']] = {'lat': s.get('lat'), 'lon': s.get('lon')}
    return _COORDS_CACHE.get(station_name)

def parse_wmo(code: int) -> str:
    if code == 0: return 'Clear'
    if code in (1, 2, 3): return 'Clouds'
    if code in (45, 48): return 'Mist'
    if code in (51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82): return 'Rain'
    if code in (95, 96, 99): return 'Thunderstorm'
    return 'Clear'

def get_weather_data(station_name: str) -> dict:
    now = time.time()
    if station_name in _CACHE:
        cached_data, timestamp = _CACHE[station_name]
        if now - timestamp < CACHE_TTL:
            return cached_data

    coords = get_coords(station_name)
    if not coords or coords['lat'] is None or coords['lon'] is None:
        # Fallback to sensible defaults
        return {"rainfall": 0.0, "condition": "Clear"}

    try:
        lat, lon = coords['lat'], coords['lon']
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=precipitation,weather_code"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        current = data.get('current', {})
        
        rainfall = float(current.get('precipitation', 0.0))
        code = int(current.get('weather_code', 0))
        condition = parse_wmo(code)

        result = {"rainfall": rainfall, "condition": condition}
        _CACHE[station_name] = (result, now)
        return result
    except Exception as e:
        print(f"Weather API error: {e}")
        return {"rainfall": 0.0, "condition": "Clear"}

def get_weather(city: str) -> dict:
    """Legacy alias used by app/routes/weather.py"""
    if city and "mumbai" in city.lower():
        # Fallback to general Mumbai coords if queried explicitly via city route
        return get_weather_data("CSMT")
    return {"rainfall": 0.0, "condition": "Clear"}
