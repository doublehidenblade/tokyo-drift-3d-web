"""Read-only independent audit of the frozen td-209 evidence; output only in review/."""
from pathlib import Path
import json, hashlib, subprocess, collections, math

REPO = Path(__file__).resolve().parents[4]
QA = REPO / 'godot/qa/td-209'
OUT = QA / 'review'
BASE = '2227f71e784f581d11ace8f90e7201fbb59b1f63'
RUNTIME = '6f7818b45cd09ade3ca621354ce4eb116050a66b'
EVIDENCE = 'bcaf46b86702848f4ae2259af6ca107592f7dcb9'
def read(name): return json.loads((QA/name).read_text())
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def git(*args): return subprocess.check_output(['git','-C',str(REPO),*args],text=True).strip()
report = {'head':git('rev-parse','HEAD'), 'runtime':RUNTIME,'base':BASE,'evidence':EVIDENCE}
manifest = read('evidence-manifest.json')
report['manifest_files_checked'] = len(manifest['files'])
report['manifest_errors'] = []
for name, row in manifest['files'].items():
    path=QA/name
    if not path.exists() or path.stat().st_size != row['bytes'] or sha(path) != row['sha256']:
        report['manifest_errors'].append(name)
pins = read('final-source-pins.json')
report['source_pin_count']=len(pins['sha256'])
report['source_pin_errors']=[name for name,h in pins['sha256'].items() if sha(REPO/name)!=h]
report['tool_pin_errors']=[name for name,h in pins['tool_sha256'].items() if sha(QA/name)!=h]
report['runtime_to_evidence_product_diff']=git('diff','--name-only',RUNTIME,EVIDENCE,'--','godot/scripts','godot/assets','godot/models','godot/scenes','godot/data','godot/project.godot','godot/export_presets.cfg').splitlines()
report['base_to_runtime_product_changes']=git('diff','--name-status',BASE,RUNTIME,'--','godot/scripts','godot/assets','godot/models','godot/scenes','godot/data','godot/project.godot','godot/export_presets.cfg').splitlines()
guards=read('protected-comparison.json')['guards']
report['protected_guard_count']=len(guards)
report['protected_guard_errors']=[]
for name,row in guards.items():
    before=subprocess.check_output(['git','-C',str(REPO),'show',BASE+':'+name])
    if hashlib.sha256(before).hexdigest()!=row['before'] or sha(REPO/name)!=row['after'] or row['before']!=row['after']:
        report['protected_guard_errors'].append(name)
city=json.loads((REPO/'godot/data/lower_city/city.json').read_text())
wanted=[i for i,lot in enumerate(city['lots']) if lot['d']=='tenjin' and lot['s']=='slab']
coverage=read('coverage.json')['coverage']
actual=[r['lot'] for r in coverage]
report['coverage']={'source_lots':wanted,'manifest_lots':actual,'exact_unique_ids':actual==wanted and len(actual)==len(set(actual)),
    'statuses':dict(collections.Counter(r['status'] for r in coverage)), 'edge_count':sum(len(r['edges']) for r in coverage),
    'source_edge_count':sum(len(city['lots'][i]['p']) for i in wanted), 'bad_edge_coverage':[]}
for row in coverage:
    lot=city['lots'][row['lot']]
    if sorted(e['edge'] for e in row['edges'])!=list(range(len(lot['p']))) or any(e['floors']<5 for e in row['edges']):
        report['coverage']['bad_edge_coverage'].append(row['lot'])
report['captures']={}
for engine in ['native','browser']:
    a,b=read(engine+'-before/result.json'),read(engine+'-after/result.json')
    if engine=='browser': a,b=a['capture'],b['capture']
    identity=lambda row:row['file'].replace('-before.png','.png').replace('-after.png','.png')
    af,bf={identity(x):x for x in a['frames']},{identity(x):x for x in b['frames']}
    fields=['camera','car','viewport','hud','ortho_size','height_m','lot','street','view']
    differences=[];same_pngs=[];missing=[]
    for name,x in af.items():
        y=bf.get(name,{})
        for key in fields:
            if x.get(key)!=y.get(key): differences.append([name,key])
        pa,pb=QA/(engine+'-before')/x['file'],QA/(engine+'-after')/y.get('file','MISSING')
        if not pa.exists() or not pb.exists():missing.append(name)
        elif sha(pa)==sha(pb):same_pngs.append(name)
    report['captures'][engine]={'before_count':len(af),'after_count':len(bf),'identity_sets_equal':set(af)==set(bf),
      'before_source':a['source'],'after_source':b['source'],'seed':[a['seed'],b['seed']],
      'camera_car_projection_viewport_hud_differences':differences,'identical_before_after_pngs':same_pngs,'missing':missing}
    # HUD-hidden and HUD views must have matching cameras within each phase too.
    hud_differences=[]
    for phase,frames in [('before',af),('after',bf)]:
        for name,x in frames.items():
            if '/routes/' in '/'+name and '-hud-' in name:
                y=frames.get(name.replace('-hud-','-world-'),{})
                if any(x.get(k)!=y.get(k) for k in ['camera','car','viewport']):hud_differences.append([phase,name])
    report['captures'][engine]['hud_world_pose_differences']=hud_differences
sheet_map=read('review-sheets/manifest.json')
report['sheets']={'count':len(sheet_map),'pairs':sum(len(x['pairs']) for x in sheet_map),
    'lot_pair_ids':[int(x['label'].split()[-1]) for s in sheet_map if 'criterion-1' in s['file'] for x in s['pairs']]}
native_import=read('native-import-provenance.json')
report['native_import']={'generated_files_checked':len(native_import['files']),'source_glbs_checked':len(native_import['source_glbs']),'errors':[]}
for row in native_import['files']:
    for project in [REPO/'godot',Path('/workspace/td209-baseline/godot')]:
        p=project/row['path']
        if not p.exists() or p.stat().st_size!=row['bytes'] or sha(p)!=row['sha256']:report['native_import']['errors'].append(str(p))
for name,h in native_import['source_glbs'].items():
    for project in [REPO/'godot',Path('/workspace/td209-baseline/godot')]:
        if sha(project/name)!=h: report['native_import']['errors'].append(str(project/name))
report['packs']={}
pack_summary=read('package-summary.json')
for phase in ['before','after']:
    row=pack_summary[phase];p=REPO/row['path']
    report['packs'][phase]={'path':row['path'],'bytes':p.stat().st_size,'sha256':sha(p),
        'matches_record':p.stat().st_size==row['bytes'] and sha(p)==row['sha256']}
report['packs']['delta_bytes']=report['packs']['after']['bytes']-report['packs']['before']['bytes']
report['packs']['over_100mib_bytes']=report['packs']['after']['bytes']-100*1024*1024
(OUT/'frozen-evidence-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
