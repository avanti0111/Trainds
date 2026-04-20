import xml.etree.ElementTree as ET
import collections, math, json

ns = {'kml': 'http://www.opengis.net/kml/2.2'}
tree_stations = ET.parse('5baa7e83-2855-4d17-86a9-9954b044ec08.kml')
root = tree_stations.getroot()

stations = []
import os
for placemark in root.findall('.//kml:Placemark', ns):
    name = placemark.find('kml:name', ns).text.strip()
    region_node = placemark.find('.//kml:SimpleData[@name="N_REGION"]', ns)
    region = region_node.text.strip().replace(' RAILWAY', '').title()
    if region == 'Trans Harbour': region = 'Trans-Harbour'
    pts = placemark.find('.//kml:Point/kml:coordinates', ns).text.strip().split(',')
    lon, lat = float(pts[0]), float(pts[1])
    stations.append({'name': name, 'region': region, 'lon': lon, 'lat': lat})

def dist(s1, s2):
    return math.hypot(s1['lon']-s2['lon'], s1['lat']-s2['lat'])

out_graph = collections.defaultdict(list)
for region in set(s['region'] for s in stations):
    reg_stats = [s for s in stations if s['region'] == region]
    n = len(reg_stats)
    edges = []
    for i in range(n):
        for j in range(i+1, n):
            edges.append((dist(reg_stats[i], reg_stats[j]), i, j))
    edges.sort()
    parent = list(range(n))
    def find(i):
        if parent[i] == i: return i
        parent[i] = find(parent[i])
        return parent[i]
    for d, u, v in edges:
        pu, pv = find(u), find(v)
        if pu != pv:
            parent[pu] = pv
            out_graph[reg_stats[u]['name']].append(reg_stats[v]['name'])
            out_graph[reg_stats[v]['name']].append(reg_stats[u]['name'])

print('Juinagar:', out_graph.get('Juinagar'))
print('Sanpada:', out_graph.get('Sanpada'))
print('Thane:', out_graph.get('Thane'))
print('Diva:', out_graph.get('Diva'))
print('Kalyan:', out_graph.get('Kalyan'))
