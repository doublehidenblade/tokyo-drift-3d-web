from pathlib import Path
import subprocess,time,json,os
root=Path('/workspace/tokyo-drift-3d');qa=root/'godot/qa/td-210';exe=root/'.tools/Godot_v4.7.2-stable_linux.x86_64';base=Path('/workspace/td210-baseline')
# Current after routes must finish before overwriting result.json with supplements.
while 'TD210_CAPTURE_DONE' not in (qa/'native-after-routes.log').read_text():time.sleep(2)
(qa/'native-after/result.json').rename(qa/'native-after/routes-result.json')
for phase,tree,pin in [('before',base,'0b2652bc86b6824444af277fdb34af5bdd981066'),('after',root,'f05048b1')]:
 for kind in (['routes','overhead'] if phase=='before' else ['overhead']):
  cmd=[str(exe),'--path',str(tree/'godot'),'--audio-driver','Dummy','--rendering-method','gl_compatibility','--rendering-driver','opengl3','res://qa/td-210/capture.tscn','--',f'--out={qa}/native-{phase}',f'--phase={phase}',f'--kind={kind}',f'--source={pin}']
  with (qa/f'native-{phase}-{kind}.log').open('w') as out:subprocess.run(cmd,cwd=tree,env=dict(os.environ,DISPLAY=':99'),stdout=out,stderr=subprocess.STDOUT,check=True)
  (qa/f'native-{phase}/result.json').rename(qa/f'native-{phase}/{kind}-result.json')
  print(phase,kind,'complete',flush=True)
for phase in ['before','after']:
 old=json.loads((qa/f'native-{phase}-superseded-lane-offset/result.json').read_text());old['frames']=[f for f in old['frames'] if f['file'].startswith('lots/')]
 for kind in ['routes','overhead']:old['frames']+=json.loads((qa/f'native-{phase}/{kind}-result.json').read_text())['frames']
 (qa/f'native-{phase}/result.json').write_text(json.dumps(old,indent=2))
