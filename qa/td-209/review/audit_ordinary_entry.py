"""Compare validator ordinary shipping-entry runs, retaining the strict failures."""
from pathlib import Path
from collections import Counter
import json
import hashlib

REVIEW = Path(__file__).resolve().parent
QA = REVIEW.parent

def load(base, phase):
    return json.loads((base / f'ordinary-entry-{phase}' / 'result.json').read_text())

def engine_errors(record):
    return Counter((e['phase'], e['message']) for e in record['errors']
                   if not e['message'].startswith('Error: Console errors were recorded;'))

before, after = load(REVIEW, 'before'), load(REVIEW, 'after')
old_before = json.loads((QA / 'ordinary-entry-before/result.json').read_text())
old_after = json.loads((QA / 'ordinary-entry/result.json').read_text())
result = {
    'strict_harness_status': [before['status'], after['status']],
    'pack_sha256': [before['pack_sha256'], after['pack_sha256']],
    'pack_hashes_match_author': before['pack_sha256'] == old_before['pack_sha256']
        and after['pack_sha256'] == old_after['pack_sha256'],
    'menu_and_live_city_reached': all('initial_state' in x and len(x['screenshots']) == 3 for x in [before, after]),
    'real_keyboard_first_observed_speed_above_3_kmh': [before['driving_state']['speed'], after['driving_state']['speed']],
    'initial_probe_state_equal': before['initial_state'] == after['initial_state'],
    'engine_error_counts': [sum(engine_errors(before).values()), sum(engine_errors(after).values())],
    'engine_error_multisets_equal': engine_errors(before) == engine_errors(after),
    'engine_errors_match_author_before': engine_errors(before) == engine_errors(old_before),
    'engine_errors_match_author_after': engine_errors(after) == engine_errors(old_after),
    'errors': [{'phase': p, 'message': m, 'count_each': n} for (p,m),n in sorted(engine_errors(before).items())],
    'per_phase_counts': dict(Counter(e['phase'] for e in before['errors'] if e['message'].startswith('ERROR:'))),
    'scope': 'Unmodified actual shipping pack at /, menu -> KeyL -> ordinary Lower City; no diagnostic scene, game-state injection or production edits. Chromium151/SwiftShader. The intentional 49th error record is the harness failure explaining the 48 engine errors. Keyboard observations establish input response, not comparable acceleration. No phone FPS or touch test claim.',
}
(REVIEW / 'independent-ordinary-comparison.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k:v for k,v in result.items() if k != 'errors'}, indent=2))
