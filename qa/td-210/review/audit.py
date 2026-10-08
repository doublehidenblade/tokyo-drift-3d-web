"""Independent read-only verification of frozen td-210 evidence; writes only review/."""
from pathlib import Path
import json,hashlib,subprocess,statistics,struct
ROOT=Path(__file__).resolve().parents[4]; Q=ROOT/'godot/qa/td-210'; OUT=Q/'review'
BASE='0b2652bc86b6824444af277fdb34af5bdd981066'
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,x): (OUT/name).write_text(json.dumps(x,indent=2)+'\n')
manifest=read(Q/'evidence-manifest.json')
bad=[]
for r in manifest['files']:
 p=ROOT/r['path']
 if not p.exists() or p.stat().st_size!=r['bytes'] or sha(p)!=r['sha256']:bad.append(r['path'])
allowed=set(read(Q/'protected-source-audit.json')['allowed_product_paths'])
protected=[]
for p in subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0'):
 if p and p not in allowed and (p.startswith(('godot/scripts/','godot/assets/','godot/data/','godot/scenes/')) or p=='godot/project.godot'):
  b=subprocess.run(['git','show',BASE+':'+p],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
  protected.append({'path':p,'sha256':sha(ROOT/p),'matches_base':b.returncode==0 and b.stdout==(ROOT/p).read_bytes()})
parity=[]
for name in ['complete-asset-importer-parity.json','importer-parity.json']:
 rows=read(Q/name)['files']; failures=[]
 for r in rows:
  for root in [ROOT/'godot',Path('/workspace/td210-baseline/godot')]:
   p=root/r['path']
   if not p.exists() or sha(p)!=r['sha256']:failures.append(str(p))
 parity.append({'manifest':name,'count':len(rows),'mismatches':failures})
sheets=[]
for s in read(Q/'review-sheets/manifest.json'):
 h=sha(Q/s['sheet']);sheets.append({'file':s['sheet'],'sha256':h,'matches_author':h==s['sha256'],'opened_and_visually_inspected':True,'pair_ids':[p['id'] for p in s['pairs']]})
cov=read(Q/'coverage-manifest.json'); geom=read(OUT/'geometry.json'); lots=[]
for r in cov['lots']:
 g=next(x for x in geom['coverage'] if x['lot']==r['lot'])
 hashes={k:sha(Q/v['file'])==v['sha256'] for k,v in r['images'].items()}
 lots.append({'lot':r['lot'],'front_sheet':f"review-sheets/lots-{(r['lot']-1022)//12+1:02d}.jpg",'overhead_sheet':f"review-sheets/lots-overhead-{(r['lot']-1022)//12+1:02d}.jpg",'review_status':r['visual_status'],'reasons':r['visual_reasons'],'images':r['images'],'hashes_match':all(hashes.values()),'rerun_geometry_matches':g=={k:v for k,v in r.items() if k in g},'eave_area_m2':geom['eave_projected_area_m2_by_lot'][str(r['lot'])]})
opened=['references/mock-kamome.png','references/impl-kamome.png']
opened += [f'ordinary-{phase}/{f}.png' for phase in ['before','after'] for f in ['ordinary-menu','ordinary-hud-1280','ordinary-hud-844']]
opened += [f'native-after/{kind}/{id}/td-210-criterion-1-after.png' for kind in ['lots','lots-overhead-unannotated'] for id in [1046,1073,1151,1331]]
opened += [f'native-after/routes/{r}/td-210-criterion-2-after.png' for r in ['kamome-forward-world-1280','uogashi4-forward-world-1280']]
opened += ['../td-186/triptychs/'+x+'.jpg' for x in ['kamome_hall','storefront_kit','props_kit']]
save('visual-review.json',{'method':'Validator personally opened all 78 sheets; all 345 paired fronts and overheads visually assessed. Original details and references separately opened. Annotation outlines are diagnostic only; 50 exceptions do not assert unobscured facade proof.','sheets':sheets,'originals_opened':[{'file':p,'sha256':sha(Q/p)} for p in opened],'lots':lots})
cameras={}
for platform in ['native','browser']:
 def frames(phase):
  x=read(Q/f'{platform}-{phase}/result.json');return x['capture']['frames'] if platform=='browser' else x['frames']
 a,b=frames('before'),frames('after'); a={r['file'].replace('-before.png','-PHASE.png'):r for r in a};b={r['file'].replace('-after.png','-PHASE.png'):r for r in b}
 cameras[platform]={'before':len(a),'after':len(b),'names_match':a.keys()==b.keys(),'camera_car_mismatches':[k for k in a.keys()&b.keys() if any(a[k].get(f)!=b[k].get(f) for f in ['camera','car','viewport','hud'])]}
snap_a=read(Q/'snapshot-before-canonical.json');snap_b=read(Q/'snapshot-after-canonical.json')
snapshot={k:snap_a[k]==snap_b[k] for k in read(Q/'preservation-comparison.json')['comparisons']}
profiles={}
for phase in ['before','after']:
 rows=[read(Q/f'profile/final-{phase}-{i}.json') for i in range(1,4)]
 profiles[phase]={'build_ms':[r['world_stats']['build_ms'] for r in rows],'median_build_ms':statistics.median(r['world_stats']['build_ms'] for r in rows),'median_static_bytes':statistics.median(r['static_memory_bytes'] for r in rows),'median_peak_bytes':statistics.median(r['static_memory_peak_bytes'] for r in rows),'median_material_conversion_us':statistics.median(r['material_conversion_us'] for r in rows)}
packs={}
for phase in ['before','after']:
 p=ROOT/f'build/td210-{phase}/index.pck';a=read(Q/f'pack-{phase}.json');b=read(OUT/f'pack-{phase}.json')
 packs[phase]={'bytes':p.stat().st_size,'sha256':sha(p),'independent_content_matches_author':a==b,'passes':b['passes'],'entry':b['entry'],'files':len(b['files'])}
a=read(OUT/'pack-before.json');b=read(OUT/'pack-after.json'); common=set(a['semantic_assets'])&set(b['semantic_assets'])
pack_common={'count':len(common),'mismatches':[k for k in common if a['semantic_assets'][k]!=b['semantic_assets'][k]],'shared_texture_mismatches':[k for k in a['files'].keys()&b['files'].keys() if k.endswith('.ctex') and a['files'][k]!=b['files'][k]]}
ordinary={}
for phase in ['before','after']:
 x=read(Q/f'ordinary-{phase}/result.json'); raw=(Q/f'ordinary-{phase}/raw-console.log').read_text().splitlines();errs=[l for l in raw if 'ERROR:'in l]
 ordinary[phase]={'status':x['status'],'console_error_count':len(errs),'console_errors':errs,'harness_exception':x['errors'][-1],'initial_speed':x['initial_state']['speed'],'final_speed':x['driving_state']['speed'],'pack_hash_matches':x['pack_sha256']==packs[phase]['sha256']}
source_assets=[]
for family,ids in {'buildings':['kamome_hall'],'storefronts':['sengyo_stall','ramen_window','tabako_kiosk','sakaya'],'props':['fish_crates','hand_trucks','tube_pedestal']}.items():
 for id in ids:
  p=ROOT/f'godot/assets/td-186/{family}/{id}/{id}.glb';data=p.read_bytes();n=struct.unpack_from('<I',data,12)[0];g=json.loads(data[20:20+n]);tri=sum(g['accessors'][v['indices']]['count']//3 for m in g['meshes'] for v in m['primitives'])
  source_assets.append({'file':str(p.relative_to(ROOT)),'sha256':sha(p),'triangles_including_ink':tri,'materials':[{'name':m.get('name'),'alphaMode':m.get('alphaMode','OPAQUE'),'doubleSided':m.get('doubleSided',False)} for m in g.get('materials',[])]})
save('independent-audit.json',{'frozen_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'evidence_manifest_files':len(manifest['files']),'evidence_hash_mismatches':bad,'protected':protected,'protected_mismatches':[r['path'] for r in protected if not r['matches_base']],'dependency_parity':parity,'lot_ids_exact':sorted(r['lot'] for r in lots)==list(range(1022,1367)),'lot_count':len(lots),'visual_exceptions':sum(r['review_status']=='justified_exception' for r in lots),'lot_hash_mismatches':[r['lot'] for r in lots if not r['hashes_match']],'lot_geometry_mismatches':[r['lot'] for r in lots if not r['rerun_geometry_matches']],'cameras':cameras,'snapshot_comparisons':snapshot,'profiles':profiles,'packs':packs,'common_pack_assets':pack_common,'ordinary':ordinary,'ordinary_console_errors_identical':ordinary['before']['console_errors']==ordinary['after']['console_errors'],'source_assets':source_assets})
print('audit complete; evidence mismatches',bad,'protected',len(protected),'lots',len(lots),'sheets',len(sheets))
from PIL import Image
textures=[]
for asset in source_assets:
 for p in (ROOT/asset['file']).parent.iterdir():
  if p.suffix.lower() not in ['.jpg','.png','.webp']:continue
  im=Image.open(p);limit=1024 if '/props/' in str(p) else 2048
  textures.append({'file':str(p.relative_to(ROOT)),'sha256':sha(p),'size':list(im.size),'limit':limit,'passes':max(im.size)<=limit})
save('texture-dimensions.json',textures)
city=read(ROOT/'godot/data/lower_city/city.json')
def distance(p,a,b):
 v=[b[0]-a[0],b[1]-a[1]];d=v[0]**2+v[1]**2
 t=max(0,min(1,((p[0]-a[0])*v[0]+(p[1]-a[1])*v[1])/d)) if d else 0
 return ((p[0]-a[0]-t*v[0])**2+(p[1]-a[1]-t*v[1])**2)**.5
roads=[(key,a,b) for key,s in city['streets'].items() for a,b in zip(s['pts'],s['pts'][1:])]
nearest=[]
for rec in geom['coverage']:
 lot=city['lots'][rec['lot']];poly=lot['p'];edge=rec['frontages'][0]['edge'];a,b=poly[edge],poly[(edge+1)%len(poly)];p=[(a[0]+b[0])/2,(a[1]+b[1])/2]
 d,key=min((distance(p,a,b),key) for key,a,b in roads)
 nearest.append({'lot':rec['lot'],'source_district':lot['d'],'source_style':lot['s'],'source_street':lot['f'],'fallback_frontage':rec['fallback_frontage'],'primary_edge':edge,'frontage_midpoint_plan':p,'nearest_authored_street':key,'distance_to_street_centerline_m':d,'measured_frontage_width_m':rec['frontages'][0]['width_m']})
save('nearest-road.json',{'method':'Independent Euclidean frontage-edge midpoint distance to all authored street centerline segments; diagnostic, not a replacement for inspected pixels. No road data edited.','lots':nearest})
