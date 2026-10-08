from pathlib import Path
import subprocess,json,hashlib,datetime
root=Path(__file__).resolve().parents[3];base='0b2652bc86b6824444af277fdb34af5bdd981066';qa=root/'godot/qa/td-210'
owned={'godot/scripts/lower_city/city_kamome_buildings.gd','godot/scripts/lower_city/city_kit_instances.gd','godot/scripts/lower_city/city_dressing.gd','godot/scripts/lower_city/lower_city_world.gd','godot/export_presets.cfg'}
tracked=subprocess.check_output(['git','ls-files','-z'],cwd=root).decode().split('\0');checked=[];bad=[]
for path in tracked:
 if not path or not (path.startswith('godot/scripts/') or path.startswith('godot/assets/') or path.startswith('godot/data/') or path.startswith('godot/scenes/') or path=='godot/project.godot'):continue
 if path in owned:continue
 current=(root/path).read_bytes();prior=subprocess.run(['git','show',base+':'+path],cwd=root,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
 match=prior.returncode==0 and current==prior.stdout
 checked.append({'path':path,'sha256':hashlib.sha256(current).hexdigest(),'matches_reviewed_base':match})
 if not match:bad.append(path)
result={'base':base,'runtime':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'allowed_product_paths':sorted(owned),'protected':checked,'unexpected_changes':bad,'passes':not bad}
(qa/'protected-source-audit.json').write_text(json.dumps(result,indent=2));print('protected',len(checked),'unexpected',bad)
