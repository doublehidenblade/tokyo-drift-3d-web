import subprocess, json, time
from pathlib import Path
root=Path('/workspace/tokyo-drift-3d');qa=root/'godot/qa/td-210';exe=root/'.tools/Godot_v4.7.2-stable_linux.x86_64';results=[]
for phase,tree in [('before',Path('/workspace/td210-baseline')),('after',root)]:
 for name in ['build','ramps','signs','drive']:
  cmd=[str(exe),'--headless','--path',str(tree/'godot'),'--fixed-fps','60','-s',f'tools/test_lower_city_{name}.gd'];start=time.monotonic()
  path=qa/f'regression-{phase}-{name}.log'
  with path.open('w') as out:
   try:r=subprocess.run(cmd,stdout=out,stderr=subprocess.STDOUT,timeout=3600);code=r.returncode
   except subprocess.TimeoutExpired:code='timeout'
  text=path.read_text();results.append({'phase':phase,'name':name,'command':cmd,'returncode':code,'seconds':time.monotonic()-start,'fail_lines':[l for l in text.splitlines() if 'FAIL' in l or 'SCRIPT ERROR' in l]})
  (qa/'regressions.json').write_text(json.dumps(results,indent=2));print(phase,name,code,flush=True)
