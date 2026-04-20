"""
Data fetching utilities for TRAiNDS.

Sources:
 1. data.gov.in – open government datasets (Indian Railways)
 2. OpenWeatherMap historical API
 3. Fallback to mock data for offline development

Usage:
    python fetch_data.py --source weather --city Mumbai
    python fetch_data.py --source stations
"""

import argparse
import json
import os
import sys
import requests
import csv
from datetime import datetime, timedelta

# ── Config ────────────────────────────────────────────────────────────────

DATA_DIR        = os.path.join(os.path.dirname(__file__), '..')
OWM_API_KEY     = os.getenv('OPENWEATHER_API_KEY', '')
DATA_GOV_TOKEN  = os.getenv('DATA_GOV_TOKEN', '')    # optional

# ── Helpers ───────────────────────────────────────────────────────────────

def save_json(data, filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f'Saved → {path}')


def save_csv(rows, fieldnames, filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f'Saved → {path}')


# ── Fetchers ──────────────────────────────────────────────────────────────

def fetch_weather_history(city: str = 'Mumbai', days: int = 30):
    """
    Fetches historical weather data using OpenWeatherMap One Call API.
    Requires a paid OWM plan for history; falls back to generating
    synthetic weather rows aligned with Mumbai climate patterns.
    """
    if not OWM_API_KEY:
        print('No OPENWEATHER_API_KEY – generating synthetic weather data')
        _generate_synthetic_weather(city, days)
        return

    # Current conditions (free tier)
    try:
        resp = requests.get(
            '[api.openweathermap.org](https://api.openweathermap.org/data/2.5/weather)',
            params={'q': city, 'appid': OWM_API_KEY, 'units': 'metric'},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        save_json({
            'city':        data['name'],
            'temperature': data['main']['temp'],
            'humidity':    data['main']['humidity'],
            'condition':   data['weather'][0]['main'],
            'description': data['weather'][0]['description'],
            'fetched_at':  datetime.now().isoformat(),
        }, 'weather_current.json')
    except Exception as e:
        print(f'Weather fetch failed: {e}')


def _generate_synthetic_weather(city: str, days: int):
    """
    Generates realistic Mumbai weather patterns (Jun–Sep = monsoon).
    """
    import random
    random.seed(42)

    MONSOON_MONTHS = {6, 7, 8, 9}
    rows = []
    base = datetime.now() - timedelta(days=days)

    for i in range(days * 24):  # hourly
        ts = base + timedelta(hours=i)
        month = ts.month
        hour  = ts.hour

        if month in MONSOON_MONTHS:
            conditions   = ['Rain'] * 50 + ['Thunderstorm'] * 20 + ['Clouds'] * 20 + ['Clear'] * 10
            rainfall_max = 50
        else:
            conditions   = ['Clear'] * 50 + ['Clouds'] * 30 + ['Haze'] * 15 + ['Mist'] * 5
            rainfall_max = 5

        cond     = random.choice(conditions)
        rainfall = round(random.uniform(0, rainfall_max), 1) if cond in ('Rain', 'Thunderstorm') else 0.0
        temp     = 28 + (2 if 10 <= hour <= 16 else 0) + (3 if month in MONSOON_MONTHS else 2)

        rows.append({
            'timestamp':   ts.strftime('%Y-%m-%d %H:%M'),
            'condition':   cond,
            'temperature': temp,
            'humidity':    75 if month in MONSOON_MONTHS else 60,
            'rainfall_mm': rainfall,
        })

    save_csv(rows,
             ['timestamp', 'condition', 'temperature', 'humidity', 'rainfall_mm'],
             'weather_history.csv')
    print(f'Generated {len(rows)} synthetic hourly weather rows for {city}')


def fetch_stations():
    """
    Loads from local stations.json (already curated).
    In production, you would call data.gov.in/resource/railway-stations
    with your DATA_GOV_TOKEN.
    """
    path = os.path.join(DATA_DIR, 'stations.json')
    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
        total = sum(len(v) for v in data.get('lines', {}).values())
        print(f'Stations file already present – {total} stations across {len(data["lines"])} lines')
    else:
        print('stations.json not found. Please ensure data/ directory is populated.')


def generate_delay_dataset(n_rows: int = 2000):
    """
    Generates a realistic delay CSV combining weather and time-of-day patterns.
    Use this to bootstrap training data before you have real historical data.
    """
    import random
    random.seed(0)

    LINES    = ['Western', 'Central', 'Harbour', 'Trans Harbour']
    WEATHERS = ['Clear', 'Clouds', 'Rain', 'Thunderstorm', 'Mist', 'Haze']
    STATIONS = [
        'Churchgate', 'Dadar', 'Andheri', 'Borivali', 'Virar',
        'CST', 'Kurla', 'Thane', 'Kalyan',
        'CSMT', 'Vashi', 'Nerul', 'Panvel',
    ]

    rows = []
    for _ in range(n_rows):
        hour        = random.randint(0, 23)
        day         = random.randint(0, 6)
        weather     = random.choice(WEATHERS)
        rainfall    = (
            round(random.uniform(0, 60), 1)
            if weather in ('Rain', 'Thunderstorm')
            else round(random.uniform(0, 3), 1)
        )
        line        = random.choice(LINES)
        station     = random.choice(STATIONS)

        # Delay heuristic (mirrors ml_service heuristic)
        delay = 0.0
        if 7 <= hour <= 10 or 17 <= hour <= 21:
            delay += random.uniform(4, 9)
        elif 10 < hour < 17:
            delay += random.uniform(0.5, 3)
        else:
            delay += random.uniform(0, 1.5)

        if day in (0, 6):
            delay = max(delay - 2.0, 0)

        weather_add = {'Rain': 5, 'Thunderstorm': 9, 'Mist': 2, 'Haze': 1.5, 'Clouds': 0.5}.get(weather, 0)
        delay += weather_add + rainfall * 0.06

        delay += random.gauss(0, 1.2)
        delay  = max(round(delay, 1), 0.0)

        rows.append({
            'hour':        hour,
            'day_of_week': day,
            'weather':     weather,
            'rainfall_mm': rainfall,
            'delay_min':   delay,
            'line':        line,
            'station':     station,
        })

    save_csv(
        rows,
        ['hour', 'day_of_week', 'weather', 'rainfall_mm', 'delay_min', 'line', 'station'],
        'sample_delays.csv',
    )
    print(f'Generated {n_rows} delay records → data/sample_delays.csv')


# ── CLI ───────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TRAiNDS data fetcher')
    parser.add_argument(
        '--source',
        choices=['weather', 'stations', 'delays', 'all'],
        default='all',
    )
    parser.add_argument('--city',   default='Mumbai')
    parser.add_argument('--days',   type=int, default=30)
    parser.add_argument('--rows',   type=int, default=2000)
    args = parser.parse_args()

    if args.source in ('weather', 'all'):
        fetch_weather_history(args.city, args.days)
    if args.source in ('stations', 'all'):
        fetch_stations()
    if args.source in ('delays', 'all'):
        generate_delay_dataset(args.rows)
