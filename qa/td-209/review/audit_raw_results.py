"""Validator's independent parsing of frozen raw regression and capture results.

Run with the activated environment's Python. Reads frozen evidence; writes only review/.
"""
from pathlib import Path
from collections import Counter
import json
import statistics

REVIEW = Path(__file__).resolve().parent
QA = REVIEW.parent

def parse_log(name):
    lines = (QA / name).read_text().splitlines()
    events = {}
    for line in lines:
        if line.startswith('TD185_') and ' {' in line:
            key, payload = line.split(' ', 1)
            events.setdefault(key, []).append(json.loads(payload))
    return {
        'path': name,
        'events': events,
        'failures': [x for x in lines if x.startswith('FAIL:')],
        'build_summary': [x for x in lines if x.startswith('TD185_BUILD')],
        'error_counts': dict(Counter(x for x in lines if x.startswith(('ERROR:', 'SCRIPT ERROR:')))),
    }

regressions = {}
for test, before in [
    ('build', 'base-lower-city-build-restored.log'),
    ('ramps', 'base-lower-city-ramps.log'),
    ('drive', 'base-lower-city-drive-isolated.log'),
    ('signs', 'base-lower-city-signs.log'),
]:
    a = parse_log('logs/' + before)
    b = parse_log('logs/released-lower-city-' + test + '.log')
    differences = []
    for name in sorted(set(a['events']) | set(b['events'])):
        left, right = a['events'].get(name, []), b['events'].get(name, [])
        if len(left) != len(right):
            differences.append({'event': name, 'count': [len(left), len(right)]})
        for index, (x, y) in enumerate(zip(left, right)):
            if x != y:
                differences.append({'event': name, 'index': index, 'fields': {
                    k: [x.get(k), y.get(k)] for k in sorted(set(x) | set(y))
                    if x.get(k) != y.get(k)
                }})
    regressions[test] = {
        'before': a, 'after': b,
        'failure_lines_equal': a['failures'] == b['failures'],
        'event_differences': differences,
    }

telemetry = {}
for kind in ['native', 'browser']:
    telemetry[kind] = {}
    for phase in ['before', 'after']:
        record = json.loads((QA / f'{kind}-{phase}/result.json').read_text())
        frames = record['frames'] if kind == 'native' else record['capture']['frames']
        telemetry[kind][phase] = {}
        for group, hud in [('world', False), ('hud', True)]:
            rows = [r for r in frames if 'lot' not in r and r['hud'] == hud]
            telemetry[kind][phase][group] = {
                'frames': len(rows),
                'median_draw_calls': statistics.median(r['draw_calls'] for r in rows),
                'max_draw_calls': max(r['draw_calls'] for r in rows),
                'median_triangles': statistics.median(r['triangles'] for r in rows),
                'max_triangles': max(r['triangles'] for r in rows),
            }

focused = json.loads((REVIEW / 'independent-focused.json').read_text())
rows = focused['coverage']
summary = {
    'checks': len(focused['checks']),
    'passed': sum(x['ok'] for x in focused['checks']),
    'failures': focused['failures'],
    'lots': len(rows),
    'edges': sum(len(r['edges']) for r in rows),
    'exposed_edges': sum(e['exposed'] for r in rows for e in r['edges']),
    'arcades': sum(e['arcade'] for r in rows for e in r['edges']),
    'storefront_counts': dict(Counter(s['id'] for r in rows for s in r['storefronts'])),
    'prop_count': sum(len(r['props']) for r in rows),
    'max_complete_building': max([
        {'lot': r['lot'], 'triangles': r['triangles_including_existing_lip']}
        for r in rows
    ], key=lambda r: r['triangles']),
    'module_placements': focused['module_placements'],
    'negative_controls': [r for r in focused['checks'] if r['check'].startswith('Negative control')],
}

result = {
    'regressions': regressions,
    'render_telemetry': telemetry,
    'telemetry_matches_author': telemetry == json.loads((QA / 'render-telemetry-summary.json').read_text())['telemetry'],
    'focused_summary': summary,
    'limits': [
        'Regressions are independently parsed author runs, not new validator drive/sign/ramp runs.',
        'Standalone ramp/drive/sign logs contain CrimeBus compile and Nil traffic/cop spawn errors; ramp baseline also predates importer restoration and includes missing car textures.',
        'Identical failure sets establish no new observed regression, not complete successful driving coverage.',
        'Capture telemetry is software-rendered parked-scene evidence; traffic and HUD vary with elapsed simulation time. No phone FPS claim.',
    ],
}
(REVIEW / 'independent-raw-results.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({
    'focused': summary,
    'telemetry_matches_author': result['telemetry_matches_author'],
    'regression_summary': {k: {
        'failures_before': v['before']['failures'],
        'failures_after': v['after']['failures'],
        'failure_lines_equal': v['failure_lines_equal'],
        'event_differences': v['event_differences'],
    } for k, v in regressions.items()},
}, indent=2))
