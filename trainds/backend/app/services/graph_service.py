"""
Graph-based routing engine for Mumbai Local Trains.
Implements Dijkstra's shortest-path algorithm.

Nodes  = stations
Edges  = (station_a, station_b, travel_time_minutes, line_name)
"""

import copy
import heapq
import json
import os
from typing import Optional

import logging

# ---------------------------------------------------------------------------
# Graph data – derived from data/routes.json at startup
# ---------------------------------------------------------------------------

logger = logging.getLogger('trainds')

class TrainGraph:
    def __init__(self):
        self.graph: dict[str, list[tuple]] = {}   # station -> [(neighbor, time, line)]
        self.stations: list[str] = []

    def add_edge(self, a: str, b: str, time_min: int, line: str):
        """Add bidirectional edge between two stations."""
        for x, y in [(a, b), (b, a)]:
            edges = self.graph.setdefault(x, [])
            # Prevent duplicate bidirectional edges being parsed twice from symmetric JSON
            if not any(e[0] == y and e[2] == line for e in edges):
                edges.append((y, time_min, line))
        if a not in self.stations:
            self.stations.append(a)
        if b not in self.stations:
            self.stations.append(b)

    def dijkstra(self, source: str, target: str) -> Optional[dict]:
        """
        Returns shortest path dict:
        { 'route': [...], 'total_time_min': int, 'segments': [...], 'changes': int }
        """
        if source not in self.graph or target not in self.graph:
            logger.warning(f"Dijkstra failed: Station '{source}' or '{target}' not in graph")
            return None

        dist  = {s: float('inf') for s in self.graph}
        prev  = {}
        dist[source] = 0
        heap = [(0, source, None)]   # (cost, node, line_used)

        while heap:
            cost, node, cur_line = heapq.heappop(heap)
            if cost > dist[node]:
                continue
            if node == target:
                break
            for neighbor, edge_time, edge_line in self.graph.get(node, []):
                new_cost = cost + edge_time
                # Add 5-minute transfer penalty for line change
                if cur_line and cur_line != edge_line:
                    new_cost += 5
                if new_cost < dist.get(neighbor, float('inf')):
                    dist[neighbor] = new_cost
                    prev[neighbor] = (node, edge_line)
                    heapq.heappush(heap, (new_cost, neighbor, edge_line))

        if dist.get(target, float('inf')) == float('inf'):
            logger.info(f"No path found between {source} and {target}")
            return None

        # Reconstruct path
        path, changes = [], 0
        node = target
        while node in prev:
            path.append(node)
            node = prev[node][0]
        path.append(source)
        path.reverse()

        # Build segments
        segments = []
        i = 0
        while i < len(path) - 1:
            seg_from = path[i]
            seg_line = prev.get(path[i + 1], (None, 'Unknown'))[1]
            seg_time = 0
            j = i
            while j < len(path) - 1:
                cur_seg_line = prev.get(path[j + 1], (None, None))[1]
                if cur_seg_line != seg_line:
                    break
                # find edge time
                for neighbor, t, l in self.graph.get(path[j], []):
                    if neighbor == path[j + 1]:
                        seg_time += t
                        break
                j += 1
            change = len(segments) > 0
            if change:
                changes += 1
            segments.append({
                'from':     seg_from,
                'to':       path[j],
                'line':     seg_line,
                'time_min': seg_time,
                'change':   change,
            })
            i = j

        return {
            'route':          path,
            'total_time_min': round(dist[target]),
            'segments':       segments,
            'changes':        changes,
        }

    def get_alternate_routes(self, source: str, target: str, n: int = 3) -> list:
        """
        Returns up to n alternative routes using an edge-blocking method
        to ensure paths have different station sequences.
        """
        results = []
        base_result = self.dijkstra(source, target)
        
        if not base_result:
            return results

        hour = __import__('datetime').datetime.now().hour
        is_peak = 7 <= hour <= 10 or 17 <= hour <= 21

        base_result['delay_risk'] = 'High' if is_peak else 'Low'
        base_result['note'] = 'Fastest route by travel time'
        results.append(base_result)

        path = base_result['route']
        seen_paths = {tuple(path)}

        for k in range(len(path) - 1):
            if len(results) >= n:
                break
                
            u, v = path[k], path[k + 1]
            
            # Temporarily remove all edges between u and v
            edges_u = [e for e in self.graph.get(u, []) if e[0] == v]
            edges_v = [e for e in self.graph.get(v, []) if e[0] == u]
            
            self.graph[u] = [e for e in self.graph.get(u, []) if e[0] != v]
            self.graph[v] = [e for e in self.graph.get(v, []) if e[0] != u]
            
            alt_result = self.dijkstra(source, target)
            
            # Restore edges
            self.graph[u].extend(edges_u)
            self.graph[v].extend(edges_v)
            
            if alt_result:
                alt_path = alt_result['route']
                if tuple(alt_path) not in seen_paths:
                    seen_paths.add(tuple(alt_path))
                    
                    alt_idx = len(results)
                    alt_result['delay_risk'] = 'Medium' if is_peak else 'Low'
                    if alt_idx == 1:
                        alt_result['note'] = 'Alternative – avoids main interchange'
                    else:
                        alt_result['note'] = 'Scenic/backup route via different line'
                    results.append(alt_result)

        # Fallback if no alternate routes found
        if len(results) == 1:
            fallback = copy.deepcopy(base_result)
            fallback['note'] = 'No alternate route available'
            results.append(fallback)
            
        return results


# ---------------------------------------------------------------------------
# Singleton instance + loader
# ---------------------------------------------------------------------------

_graph_instance: Optional[TrainGraph] = None

def _load_routes_file() -> list:
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, '..', '..', '..', 'data', 'routes.json')
    path = os.path.normpath(path)
    if os.path.exists(path):
        try:
            with open(path) as f:
                data = json.load(f).get('stations', [])
                logger.info(f"Successfully loaded {len(data)} stations from routes.json")
                return data
        except Exception as e:
            logger.error(f"Failed to parse routes.json: {e}")
            return []
    else:
        logger.error(f"routes.json not found at {path}")
    return []

def get_graph() -> TrainGraph:
    global _graph_instance
    if _graph_instance is None:
        logger.info("Initializing global TrainGraph instance...")
        _graph_instance = TrainGraph()
        stations_data = _load_routes_file()
        if not stations_data:
            logger.warning("No station data found to load into graph.")
        for station in stations_data:
            source = station.get('name')
            if not source: continue
            for conn in station.get('connections', []):
                _graph_instance.add_edge(
                    source, conn['to'], conn['time'], conn['line']
                )
        logger.info(f"Graph initialized with {len(_graph_instance.stations)} unique stations.")
    return _graph_instance

