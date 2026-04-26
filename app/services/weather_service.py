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
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    for s in data.get('stations', []):
                        _COORDS_CACHE[s['name']] = {'lat': s.get('lat'), 'lon': s.get('lon')}
            except:
                pass
    return _COORDS_CACHE.get(station_name)

def get_weather_data(station_name: str) -> dict:
    now = time.time()
    if station_name in _CACHE:
        cached_data, timestamp = _CACHE[station_name]
        if now - timestamp < CACHE_TTL:
            return cached_data

    api_key = os.getenv('OPENWEATHER_API_KEY')
    coords = get_coords(station_name)
    
    # Defaults
    lat, lon = 18.9220, 72.8347 # Mumbai CST
    if coords and coords['lat'] and coords['lon']:
        lat, lon = coords['lat'], coords['lon']

    if not api_key:
        return {"temperature": "--", "description": "No API Key", "rainfall": 0.0}

    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        
        temp = data.get('main', {}).get('temp', 0.0)
        desc = data.get('weather', [{}])[0].get('main', 'Clear')
        rain = data.get('rain', {}).get('1h', 0.0)

        result = {
            "temperature": round(temp, 1),
            "description": desc,
            "rainfall": rain
        }
        _CACHE[station_name] = (result, now)
        return result
    except Exception as e:
        print(f"Weather API error: {e}")
        return {"temperature": "--", "description": "Offline", "rainfall": 0.0}

def get_weather(city: str) -> dict:
    return get_weather_data("CSMT")

