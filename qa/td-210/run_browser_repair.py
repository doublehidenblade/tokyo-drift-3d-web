from pathlib import Path
import subprocess,time,shutil,json
root=Path('/workspace/tokyo-drift-3d');qa=root/'godot/qa/td-210';base=Path('/workspace/td210-baseline')
# Wait for the existing complete-but-superseded lane-offset baseline run to finish.
while not (qa/'browser-before/result.json').exists():time.sleep(2)
for phase,tree,pin in [('before',base,'0b2652bc86b6824444af277fdb34af5bdd981066'),('after',root,'f05048b1')]:
 old=qa/f'browser-{phase}';dest=qa/f'browser-{phase}-superseded-lane-offset';assert not dest.exists();old.rename(dest)
 shutil.copy(qa/'capture.gd',tree/'godot/qa/td-210/capture.gd') if tree!=root else None
 with (qa/f'export-{phase}-capture-road-width.log').open('w') as out:
  subprocess.run(['python',str(tree/'godot/qa/td-210/export_capture.py'),str(root/f'build/td210-{phase}-capture')],cwd=tree,stdout=out,stderr=subprocess.STDOUT,check=True)
 with (qa/f'browser-{phase}-road-width.log').open('w') as out:
  subprocess.run(['node',str(qa/'browser.mjs'),str(root/f'build/td210-{phase}-capture'),str(old),phase,pin],cwd=root,stdout=out,stderr=subprocess.STDOUT,check=True)
 print('browser routes',phase,'complete',flush=True)
for phase in ['before','after']:
 with (qa/f'ordinary-{phase}.log').open('w') as out:
  r=subprocess.run(['node',str(qa/'ordinary_entry.mjs'),str(root/f'build/td210-{phase}'),str(qa/f'ordinary-{phase}')],cwd=root,stdout=out,stderr=subprocess.STDOUT)
 print('ordinary',phase,'returncode',r.returncode,flush=True)
