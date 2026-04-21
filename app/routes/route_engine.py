from flask import Blueprint, request
from app.services.graph_service import get_graph
from app.services.decision_service import get_travel_decision
from app.utils.helpers import api_response, handle_errors

bp = Blueprint('route', __name__)


@bp.route('/route', methods=['POST'])
@handle_errors
def plan_route():
    body = request.get_json(force=True)
    from_s = body.get('from', '').strip()
    to_s   = body.get('to',   '').strip()

    if not from_s or not to_s:
        return api_response(error='from and to are required', status=400)

    graph  = get_graph()
    result = graph.dijkstra(from_s, to_s)

    if not result:
        return api_response({
            'error': f'No route found between "{from_s}" and "{to_s}". '
                     f'Check station spelling or ensure they are on connected lines.'
        })

    return api_response(result)


@bp.route('/route/what-if', methods=['POST'])
@handle_errors
def what_if():
    body  = request.get_json(force=True)
    from_s = body.get('from', '').strip()
    to_s   = body.get('to',   '').strip()

    if not from_s or not to_s:
        return api_response(error='from and to are required', status=400)

    graph   = get_graph()
    routes  = graph.get_alternate_routes(from_s, to_s, n=3)
    
    if not routes:
        return api_response(error='No routes found', status=404)

    # Use centralized decision engine with real-world weather integration
    best_route = min(routes, key=lambda x: x.get('total_time_min', float('inf')))
    decision = get_travel_decision(from_s, best_route.get('total_time_min', 0))

    return api_response({'routes': routes, 'decision': decision})


import itertools

@bp.route('/multi-route', methods=['POST'])
@handle_errors
def multi_route():
    body = request.get_json(force=True)
    source = body.get('source', '').strip()
    destinations = body.get('destinations', [])
    mode = body.get('mode', 'optimize')
    
    if not source or not destinations:
        return api_response(error='source and destinations are required', status=400)
    
    if len(destinations) > 4:
        return api_response(error='Maximum 4 destinations allowed', status=400)
        
    graph = get_graph()
    
    best_sequence = []
    best_time = float('inf')
    best_plan = []
    
    if mode == 'priority':
        sequences = [tuple(destinations)]
    else:
        sequences = list(itertools.permutations(destinations))
        
    for seq in sequences:
        current_node = source
        current_time = 0
        current_plan = []
        valid = True
        
        for dest in seq:
            result = graph.dijkstra(current_node, dest)
            if not result or 'route' not in result:
                valid = False
                break
                
            seg_time = result.get('total_time_min', 0)
            current_plan.append({
                'from': current_node,
                'to': dest,
                'route': result['route'],
                'time': seg_time
            })
            current_time += seg_time
            current_node = dest
            
        if valid and current_time < best_time:
            best_time = current_time
            best_sequence = list(seq)
            best_plan = current_plan
            
    if not best_plan:
        return api_response(error='No valid routes found mapping the destinations', status=404)
        
    # Use centralized decision engine for multi-stop journeys too
    decision = get_travel_decision(source, best_time)
    
    return api_response({
        "optimized_order": best_sequence,
        "journey_plan": best_plan,
        "total_time": decision['estimated_total_time'],
        "decision": decision
    })
