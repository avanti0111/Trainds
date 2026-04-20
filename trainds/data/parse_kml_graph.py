import xml.etree.ElementTree as ET
import math
import collections
import json
import os

def normalize_name(name):
    n = " ".join(name.replace("Junction", "").strip().split())
    if n == "CST": return "CSMT"
    if n == "Bombay Central": return "Mumbai Central"
    if n == "Ray Road": return "Reay Road"
    if n == "Chinchpokali": return "Chinchpokli"
    if n == "Chunna Bhatti": return "Chunabhatti"
    return n.title() if n != "CSMT" and n != "CBD Belapur" else n

ns = {'kml': 'http://www.opengis.net/kml/2.2'}

def parse_kml():
    data_dir = os.path.dirname(os.path.abspath(__file__))
    lines_file = os.path.join(data_dir, '46f53a20-aebb-4096-bf33-c6d9d87afaca.kml')
    stations_file = os.path.join(data_dir, '5baa7e83-2855-4d17-86a9-9954b044ec08.kml')
    out_file = os.path.join(data_dir, 'routes.json')

    tree_lines = ET.parse(lines_file)
    root_lines = tree_lines.getroot()

    lines_by_region = collections.defaultdict(list)
    for placemark in root_lines.findall('.//kml:Placemark', ns):
        region_data = placemark.find('.//kml:SimpleData[@name="L_REGION"]', ns)
        if region_data is None or not region_data.text: continue
        region = region_data.text.strip().replace(" RAILWAY", "").strip().title()
        
        for ls in placemark.findall('.//kml:LineString', ns):
            coords = ls.find('kml:coordinates', ns)
            if coords is not None:
                pts = []
                for pair in coords.text.strip().split():
                    c = pair.split(',')
                    pts.append((round(float(c[0]), 5), round(float(c[1]), 5)))
                lines_by_region[region].append(pts)

    tree_stations = ET.parse(stations_file)
    root_stations = tree_stations.getroot()
    
    stations = []
    for placemark in root_stations.findall('.//kml:Placemark', ns):
        name_node = placemark.find('kml:name', ns)
        region_node = placemark.find('.//kml:SimpleData[@name="N_REGION"]', ns)
        pt_node = placemark.find('.//kml:Point/kml:coordinates', ns)
        if name_node is None or pt_node is None or region_node is None: continue
        name = normalize_name(name_node.text.strip())
        region = region_node.text.strip().replace(" RAILWAY", "").strip().title()
        if region == "Trans Harbour": region = "Trans-Harbour"
        pts = pt_node.text.strip().split(',')
        lon, lat = float(pts[0]), float(pts[1])
        stations.append({'name': name, 'region': region, 'lon': lon, 'lat': lat, 'snapped_coord': None})

    # Hardcode connections for interchanges/stations not correctly mapped
    final_stations = {}
    for s in stations:
        if s['name'] not in final_stations:
            final_stations[s['name']] = {'name': s['name'], 'lines': set(), 'connections': [], 'lon': s['lon'], 'lat': s['lat']}
        final_stations[s['name']]['lines'].add(s['region'])

    def dist(c1, c2):
        return math.hypot(c1[0]-c2[0], c1[1]-c2[1])

    for region, polylines in lines_by_region.items():
        adj = collections.defaultdict(set)
        all_coords = set()
        for poly in polylines:
            for i in range(len(poly)):
                all_coords.add(poly[i])
                if i > 0:
                    adj[poly[i]].add(poly[i-1])
                    adj[poly[i-1]].add(poly[i])
        
        all_coords_list = list(all_coords)
        for i in range(len(all_coords_list)):
            for j in range(i+1, len(all_coords_list)):
                c1 = all_coords_list[i]
                c2 = all_coords_list[j]
                if dist(c1, c2) < 0.00005: 
                    adj[c1].add(c2)
                    adj[c2].add(c1)

        # robust threshold: ~200 meters
        THRESHOLD = 0.002 
        
        coord_to_station = collections.defaultdict(list)
        for s in stations:
            best_c = None
            best_d = float('inf')
            for c in all_coords:
                d = dist((s['lon'], s['lat']), c)
                if d < best_d:
                    best_d = d
                    best_c = c
            
            # Snap to this line ONLY if the station is geographically located near the physical track
            if best_d < THRESHOLD:
                s['snapped_coord'] = best_c
                coord_to_station[best_c].append(s['name'])
                final_stations[s['name']]['lines'].add(region)
        
        for start_coord, start_stat_list in coord_to_station.items():
            queue = collections.deque([(start_coord, 0)])
            visited = set([start_coord])
            min_found_cost = {}
            while queue:
                curr, cost = queue.popleft()
                if curr in coord_to_station and curr != start_coord:
                    # Register valid topology edge
                    for s1 in start_stat_list:
                        for s2 in coord_to_station[curr]:
                            if s1 != s2:
                                # maintain shortest traversal path cost
                                final_stations[s1]['connections'].append({'to': s2, 'time': max(2, int(cost/10)), 'line': region})
                                final_stations[s2]['connections'].append({'to': s1, 'time': max(2, int(cost/10)), 'line': region})
                    continue 

                for neighbor in adj[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, cost + 1))

    out_list = []
    for k, v in final_stations.items():
        v['lines'] = list(v['lines'])
        seen_conn = set()
        new_conns = []
        for c in v['connections']:
            key = (c['to'], c['line'])
            if key not in seen_conn:
                seen_conn.add(key)
                new_conns.append({'to': c['to'], 'time': 3, 'line': c['line']}) # Normalize 3 min
        v['connections'] = new_conns
        out_list.append(v)
    
    with open(out_file, 'w') as f:
        json.dump({'stations': out_list}, f, indent=2)

if __name__ == '__main__':
    parse_kml()
