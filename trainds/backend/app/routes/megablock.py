"""
Megablock alerts endpoint.
Data sourced from data/megablocks.json; fallback to static sample.
"""

import json
import os
from flask import Blueprint, request
from app.utils.helpers import api_response, handle_errors

bp = Blueprint('megablock', __name__)

def _load_megablocks():
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.normpath(
        os.path.join(base, '..', '..', '..', 'data', 'megablocks.json')
    )
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f).get('megablocks', [])
    return _fallback_megablocks()


def _fallback_megablocks():
    return [
        {
            'title':            'Western Line Maintenance Block',
            'line':             'Western',
            'date':             'Every Sunday',
            'time_range':       '00:30 – 05:30',
            'affected_section': 'Churchgate – Virar',
            'description':      'Track maintenance. No services between Churchgate and Virar.',
            'alternative':      'BEST buses on WE Highway, Night auto services',
        },
        {
            'title':            'Central Line Power Block',
            'line':             'Central',
            'date':             'Every Sunday',
            'time_range':       '01:00 – 04:30',
            'affected_section': 'CST – Thane',
            'description':      'Overhead equipment maintenance. Reduced frequency.',
            'alternative':      'BEST buses, Metro Line 2A',
        },
        {
            'title':            'Harbour Line Block',
            'line':             'Harbour',
            'date':             'Second Sunday of each month',
            'time_range':       '00:30 – 06:00',
            'affected_section': 'CSMT – Panvel',
            'description':      'Track renewal work in progress.',
            'alternative':      'NMMT buses, Vashi–Panvel auto',
        },
    ]


@bp.route('/megablock', methods=['GET'])
@handle_errors
def megablock():
    line   = request.args.get('line')
    blocks = _load_megablocks()
    if line:
        blocks = [b for b in blocks if b.get('line', '').lower() == line.lower()]
    return api_response({'megablocks': blocks})
