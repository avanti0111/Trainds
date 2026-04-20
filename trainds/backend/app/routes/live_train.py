"""
Live train endpoint.
In production: integrate with RailYatri / NTES scraper or paid railway API.
For now: returns realistic simulated data so the UI is fully functional.
"""

import random
from datetime import datetime, timedelta
from flask import Blueprint, request
from app.utils.helpers import api_response, handle_errors

bp = Blueprint('live_train', __name__)

TRAIN_CACHE = {}

LINES = {
    "Western": [
      "Churchgate", "Marine Lines", "Charni Road", "Grant Road",
      "Mumbai Central", "Mahalaxmi", "Lower Parel", "Elphinstone Road",
      "Dadar", "Matunga Road", "Mahim", "Bandra", "Khar Road",
      "Santacruz", "Vile Parle", "Andheri", "Jogeshwari", "Ram Mandir",
      "Goregaon", "Malad", "Kandivali", "Borivali", "Dahisar",
      "Mira Road", "Bhayander", "Naigaon", "Vasai Road", "Nallasopara",
      "Virar", "Vaitarna", "Saphale", "Kelve Road", "Palghar"
    ],
    "Central": [
      "CSMT", "Masjid", "Sandhurst Road", "Byculla", "Chinchpokli",
      "Currey Road", "Parel", "Dadar", "Matunga", "Sion", "Kurla",
      "Vidyavihar", "Ghatkopar", "Vikhroli", "Kanjurmarg", "Bhandup",
      "Nahur", "Mulund", "Thane", "Kalwa", "Mumbra", "Diva",
      "Kopar", "Dombivali", "Thakurli", "Kalyan", "Shahad",
      "Ambivali", "Titwala", "Khadavli", "Vasind", "Asangaon",
      "Atgaon", "Khardi", "Kasara", "Karjat", "Khopoli"
    ],
    "Harbour": [
      "CSMT", "Dockyard Road", "Reay Road", "Cotton Green", "Sewri",
      "Wadala Road", "Kings Circle", "GTB Nagar", "Chunabhatti",
      "Kurla", "Tilak Nagar", "Chembur", "Govandi", "Mankhurd",
      "Vashi", "Sanpada", "Juinagar", "Nerul", "Seawoods", "Belapur",
      "Kharghar", "Mansarovar", "Khandeshwar", "Panvel"
    ],
    "Trans Harbour": [
      "Thane", "Airoli", "Rabale", "Ghansoli", "Kopar Khairane",
      "Turbhe", "Sanpada", "Juinagar", "Vashi", "Mankhurd"
    ]
}

TERMINALS = {
    "Western": ["Churchgate", "Dadar", "Bandra", "Andheri", "Goregaon", "Borivali", "Bhayander", "Vasai Road", "Virar", "Palghar"],
    "Central": ["CSMT", "Dadar", "Kurla", "Thane", "Dombivali", "Kalyan", "Titwala", "Asangaon", "Kasara", "Badlapur", "Karjat", "Khopoli"],
    "Harbour": ["CSMT", "Wadala Road", "Mankhurd", "Vashi", "Belapur", "Panvel", "Bandra", "Goregaon"],
    "Trans Harbour": ["Thane", "Vashi", "Nerul", "Panvel"]
}

TRAIN_NAMES = [
    'Fast Local', 'Semi-Fast', 'Slow Local', 'Express Local', 'Peak Special'
]

def _nearest_line(station: str) -> str:
    station = station.lower().strip()
    for line, stations in LINES.items():
        if any(s.lower() == station for s in stations):
            return line
    return None

def _generate_trains(station: str, n: int = 8) -> list:
    line   = _nearest_line(station)
    if not line:
        raise ValueError("Invalid station")
        
    stops  = LINES[line]
    now    = datetime.now()
    trains = []

    stops_lower = [s.lower() for s in stops]
    station_index = stops_lower.index(station.lower())
    station = stops[station_index]

    attempts = 0
    while len(trains) < n and attempts < 100:
        attempts += 1
        dep_time = now + timedelta(minutes=random.randint(2, 8) + len(trains) * random.randint(4, 7))
        arr_time  = dep_time + timedelta(minutes=random.randint(15, 90))
        delay_min = random.choices([0, 0, 0, 2, 3, 5, 8, 12, 15],
                                   weights=[30, 20, 10, 10, 8, 8, 5, 5, 4])[0]
        status    = (
            'On Time'   if delay_min == 0 else
            'Delayed'   if delay_min <= 10 else
            'Cancelled' if random.random() < 0.03 else
            'Delayed'
        )

        valid_terminals = [t for t in TERMINALS[line] if t in stops]
        
        direction = random.choice(["UP", "DOWN"])
        if direction == "DOWN":
            possible_starts = [t for t in valid_terminals if stops.index(t) <= station_index]
            possible_ends   = [t for t in valid_terminals if stops.index(t) > station_index]
            if station in valid_terminals and random.random() > 0.5:
                possible_ends.append(station)
        else:
            possible_starts = [t for t in valid_terminals if stops.index(t) >= station_index]
            possible_ends   = [t for t in valid_terminals if stops.index(t) < station_index]
            if station in valid_terminals and random.random() > 0.5:
                possible_ends.append(station)

        if not possible_starts or not possible_ends:
            continue

        from_station = random.choice(possible_starts)
        to_station = random.choice(possible_ends)
        
        if from_station == to_station:
            continue

        if line == "Harbour" or line == "Trans Harbour":
            train_name = "Slow Local"
        else:
            train_name = random.choice(TRAIN_NAMES)

        trains.append({
            'train_no':     f'{random.randint(90000, 99999)}',
            'name':         train_name,
            'from_station': from_station,
            'to_station':   to_station,
            'departure':    dep_time.strftime('%H:%M'),
            'arrival':      arr_time.strftime('%H:%M'),
            'platform':     str(random.randint(1, 6)),
            'status':       status,
            'delay_min':    delay_min if status != 'On Time' else 0,
            'line':         line,
        })

    return sorted(trains, key=lambda t: t['departure'])


@bp.route('/live-train', methods=['GET'])
@handle_errors
def live_train():
    station = request.args.get('station', 'CSMT').strip()

    cache = TRAIN_CACHE.get(station)

    if not cache or (datetime.now() - cache["time"]).seconds > 120:
        TRAIN_CACHE[station] = {
            "time": datetime.now(),
            "data": _generate_trains(station)
        }

    trains = TRAIN_CACHE[station]["data"]

    now = datetime.now()
    filtered = []
    for t in trains:
        dep = datetime.strptime(t['departure'], "%H:%M").replace(
            year=now.year,
            month=now.month,
            day=now.day
        )
        dep = dep + timedelta(minutes=t['delay_min'])
        if dep >= now:
            filtered.append(t)

    return api_response({
        'station': station,
        'trains': filtered,
        'updated': datetime.now().isoformat(),
    })
