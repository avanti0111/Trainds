import datetime
from app.services.weather_service import get_weather_data

def get_travel_decision(station_name, base_time_min):
    """
    Centralized heuristic engine to determine travel recommendations
    based on real-time weather, time of day, and safety buffers.
    """
    now = datetime.datetime.now()
    hour = now.hour + now.minute / 60.0
    
    reasoning = []
    
    # 1. Peak Hour Heuristics
    is_morning_peak = 7.5 <= hour <= 10.5
    is_evening_peak = 17.5 <= hour <= 21.0
    is_peak = is_morning_peak or is_evening_peak
    
    congestion = 10 if is_peak else 2
    if is_peak:
        reasoning.append(f"Peak hour congestion detected (+{congestion}m)")
    else:
        reasoning.append("Normal off-peak traffic conditions")

    # 2. Weather Integration
    weather = get_weather_data(station_name)
    weather_condition = weather.get('condition', 'Clear')
    rainfall = weather.get('rainfall', 0.0)
    
    weather_overhead = 0
    if rainfall > 20:
        weather_overhead = 15
        reasoning.append(f"Heavy rainfall ({rainfall}mm) – high risk of waterlogging (+{weather_overhead}m)")
    elif rainfall > 5:
        weather_overhead = 8
        reasoning.append(f"Moderate rain detected – signal delays expected (+{weather_overhead}m)")
    elif weather_condition in ['Thunderstorm', 'Mist']:
        weather_overhead = 5
        reasoning.append(f"Poor visibility/weather ({weather_condition}) – cautious speeds (+{weather_overhead}m)")

    # 3. Safety Buffer
    buffer_time = 8
    reasoning.append(f"Standard safety buffer applied (+{buffer_time}m)")

    total_added_time = congestion + weather_overhead + buffer_time
    est_total_time = base_time_min + total_added_time
    
    recommendation = "Leave Now"
    departure = now
    
    if total_added_time > 15:
        recommendation = f"Leave After {total_added_time} mins"
        departure = now + datetime.timedelta(minutes=total_added_time)
    
    return {
        "recommendation": recommendation,
        "departure_time": departure.strftime("%I:%M %p"),
        "estimated_total_time": round(est_total_time),
        "reasoning": reasoning,
        "weather": weather
    }
