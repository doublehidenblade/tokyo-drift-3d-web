from pathlib import Path
import subprocess,time,json
root=Path('/workspace/tokyo-drift-3d');qa=root/'godot/qa/td-210';exe=root/'.tools/Godot_v4.7.2-stable_linux.x86_64'
# Wait without changing or pausing any absolute-time game tests.
while True:
 rows=json.loads((qa/'regressions.json').read_text())
 if len(rows)==8 and (qa/'ordinary-after/result.json').exists() and (qa/'native-after/overhead-result.json').exists():break
 time.sleep(5)
for repeat in range(1,4):
 for phase,tree in [('before',Path('/workspace/td210-baseline')),('after',root)]:
  path=qa/f'profile/final-{phase}-{repeat}'
  with path.with_suffix('.log').open('w') as out:
   subprocess.run([str(exe),'--headless','--path',str(tree/'godot'),'-s','qa/td-210/profile/final_world.gd','--',str(path.with_suffix('.json'))],stdout=out,stderr=subprocess.STDOUT,check=True)
  print(phase,repeat,'complete',flush=True)
