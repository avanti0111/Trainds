import json

RENAME_MAP = {
    'Ambivili': 'Ambivali',
    'Bhayandar': 'Bhayander',
    'CBD Belapur': 'Belapur',
    'Dombivili': 'Dombivali',
    'Guru Tej Bahadur Nagar': 'GTB Nagar',
    'Kanjur Marg': 'Kanjurmarg',
    'Khadawali': 'Khadavli',
    'Kopar Kharine': 'Kopar Khairane',
    'Lower Kopar': 'Kopar',
    'Masjid Bunder': 'Masjid',
    'Prabhadevi': 'Elphinstone Road',
}

def rename_node(n):
    return RENAME_MAP.get(n, n)

with open('data/routes.json', 'r') as f:
    routes = json.load(f)

# Update existing node names and connection names
for station in routes['stations']:
    station['name'] = rename_node(station['name'])
    for conn in station.get('connections', []):
        conn['to'] = rename_node(conn['to'])

# Read the latest stations list
with open('data/stations.json', 'r') as f:
    st_data = json.load(f)

graph_stations = {s['name']: s for s in routes['stations']}

# Add missing stations and link them
for line, stns in st_data['lines'].items():
    for i in range(len(stns)):
        curr = stns[i]
        if curr not in graph_stations:
            # Missing node
            graph_stations[curr] = {
                'name': curr,
                'connections': []
            }
            routes['stations'].append(graph_stations[curr])
            
        # Check edges
        if i > 0:
            prev = stns[i-1]
            if prev in graph_stations:
                # Add forward edge if missing
                if not any(c['to'] == curr and c['line'] == line for c in graph_stations[prev]['connections']):
                    graph_stations[prev]['connections'].append({
                        'to': curr,
                        'time': 4,  # assume 4 mins 
                        'line': line
                    })
                # Add backward edge if missing
                if not any(c['to'] == prev and c['line'] == line for c in graph_stations[curr]['connections']):
                    graph_stations[curr]['connections'].append({
                        'to': prev,
                        'time': 4,
                        'line': line
                    })

with open('data/routes.json', 'w') as f:
    json.dump(routes, f, indent=2)

print("routes.json patched successfully!")
