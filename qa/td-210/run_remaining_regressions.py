"""Finish existing baseline child without interrupting it; run independent final suites in parallel.
The original coordinator is paused only to prevent duplicate after runs. No Godot test is paused.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import os,signal,subprocess,json,time
root=Path('/workspace/tokyo-drift-3d');qa=root/'godot/qa/td-210';exe=root/'.tools/Godot_v4.7.2-stable_linux.x86_64'
rows=json.loads((qa/'regressions.json').read_text());assert len(rows)==3
parent=24066;child=27414
assert Path(f'/proc/{parent}/cmdline').read_bytes().replace(b'\0',b' ').strip()==b'python godot/qa/td-210/run_regressions.py'
assert b'test_lower_city_drive.gd' in Path(f'/proc/{child}/cmdline').read_bytes()
os.kill(parent,signal.SIGSTOP)
started=time.monotonic();initial_age=float(subprocess.check_output(['ps','-o','etimes=','-p',str(child)],text=True))
(qa/'regression-orchestration.md').write_text('After baseline build/ramps/signs finished, the Python coordinator was paused while its already-running baseline drive Godot child continued unmodified. Independent final suites run with at most2 new Godot processes. The coordinator is terminated only after that child exits, preventing duplicate tests. No game/test process is paused or altered; fixed60Hz simulation and assertions remain unchanged. Baseline drive exit status is read directly from the terminated child proc status before reaping; elapsed time includes its preexisting age (1s precision). Final quiet profiles wait for every process to finish.\n')
def failures(path):return [l for l in path.read_text().splitlines() if 'FAIL' in l or 'SCRIPT ERROR' in l]
def before_drive():
 while True:
  fields=Path(f'/proc/{child}/stat').read_text().split(') ',1)[1].split()
  if fields[0]=='Z':
   status=int(fields[49]);code=os.waitstatus_to_exitcode(status);break
  time.sleep(1)
 elapsed=initial_age+time.monotonic()-started
 os.kill(parent,signal.SIGKILL)
 return {'phase':'before','name':'drive','command':[str(exe),'--headless','--path','/workspace/td210-baseline/godot','--fixed-fps','60','-s','tools/test_lower_city_drive.gd'],'returncode':code,'seconds':elapsed,'elapsed_precision_s':1,'exit_status_source':'Linux proc stat zombie exit_code','fail_lines':failures(qa/'regression-before-drive.log')}
def after(name):
 cmd=[str(exe),'--headless','--path',str(root/'godot'),'--fixed-fps','60','-s',f'tools/test_lower_city_{name}.gd'];start=time.monotonic();path=qa/f'regression-after-{name}.log'
 with path.open('w') as out:
  try:r=subprocess.run(cmd,stdout=out,stderr=subprocess.STDOUT,timeout=3600);code=r.returncode
  except subprocess.TimeoutExpired:code='timeout'
 return {'phase':'after','name':name,'command':cmd,'returncode':code,'seconds':time.monotonic()-start,'fail_lines':failures(path)}
with ThreadPoolExecutor(max_workers=3) as pool:
 # One thread monitors the inherited baseline; two run independent final suites.
 jobs=[pool.submit(before_drive)]+[pool.submit(after,n) for n in ['build','ramps','signs','drive']]
 for job in as_completed(jobs):
  record=job.result();rows.append(record);(qa/'regressions.json').write_text(json.dumps(rows,indent=2));print(record['phase'],record['name'],record['returncode'],flush=True)
