from pathlib import Path
import subprocess,shutil,json,os
root=Path('/workspace/tokyo-drift-3d');qa=root/'godot/qa/td-210';exe=root/'.tools/Godot_v4.7.2-stable_linux.x86_64'
for name in ['clip','oblique','annotated']:
 src=Path('/tmp/td210-'+name)
 if src.exists():shutil.copytree(src,qa/('diagnostic-study-'+name),dirs_exist_ok=True)
 log=Path('/tmp/td210-'+name+'.log')
 if log.exists():shutil.copy(log,qa/('diagnostic-study-'+name+'.log'))
for phase,tree,pin in [('before',Path('/workspace/td210-baseline'),'0b2652bc86b6824444af277fdb34af5bdd981066'),('after',root,'f05048b1')]:
 out=qa/f'native-{phase}';(out/'lots-overhead').rename(out/'lots-overhead-unannotated');(out/'overhead-result.json').rename(out/'overhead-unannotated-result.json')
 if tree!=root:shutil.copy(qa/'capture.gd',tree/'godot/qa/td-210/capture.gd')
 cmd=[str(exe),'--path',str(tree/'godot'),'--audio-driver','Dummy','--rendering-method','gl_compatibility','--rendering-driver','opengl3','res://qa/td-210/capture.tscn','--',f'--out={out}',f'--phase={phase}','--kind=overhead',f'--source={pin}']
 with (qa/f'native-{phase}-overhead-annotated.log').open('w') as log:subprocess.run(cmd,cwd=tree,env=dict(os.environ,DISPLAY=':99'),stdout=log,stderr=subprocess.STDOUT,check=True)
 (out/'result.json').rename(out/'overhead-result.json')
 old=json.loads((qa/f'native-{phase}-superseded-lane-offset/result.json').read_text());old['frames']=[f for f in old['frames'] if f['file'].startswith('lots/')]
 for kind in ['routes','overhead']:old['frames']+=json.loads((out/f'{kind}-result.json').read_text())['frames']
 (out/'result.json').write_text(json.dumps(old,indent=2));print(phase,'annotated overhead complete',flush=True)
