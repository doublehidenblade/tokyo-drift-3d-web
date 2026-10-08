from pathlib import Path
import json
q=Path(__file__).resolve().parent
rows=json.loads((q/'regressions.json').read_text())
assert len(rows)==8,'Paired suites must all complete first'
by={(r['phase'],r['name']):r for r in rows}
def records(phase,name,prefix):
 lines=(q/f'regression-{phase}-{name}.log').read_text().splitlines()
 return [json.loads(l[len(prefix)+1:]) for l in lines if l.startswith(prefix+' {')]
result={'note':'Raw emitted assertions define outcomes; process returncode alone is insufficient. Original after-build failure is retained and separately corrected by the actual mesh eave audit. No all-green claim.','suites':{}}
for name,prefix,detail in [('ramps','TD185_RAMPS','TD185_RAMP'),('signs','TD185_SIGNS','TD185_TRIP'),('drive','TD185_DRIVE','TD185_LEG')]:
 a,b=records('before',name,prefix),records('after',name,prefix);da,db=records('before',name,detail),records('after',name,detail)
 assert a and b,(name,'missing final summary')
 errors={p:by[p,name]['fail_lines'] for p in ['before','after']}
 result['suites'][name]={'before_summary':a[-1],'after_summary':b[-1],'observed_process_returncodes':[by['before',name]['returncode'],by['after',name]['returncode']],'emitted_details_identical':da==db,'detail_differences':[{'index':i,'before':x,'after':y} for i,(x,y) in enumerate(zip(da,db)) if x!=y],'detail_counts':[len(da),len(db)],'raw_fail_lines':errors}
result['suites']['build']={'before_returncode':by['before','build']['returncode'],'original_after_returncode':by['after','build']['returncode'],'original_after_fail_lines':by['after','build']['fail_lines'],'corrected_failures':0 if 'TD185_BUILD failures=0' in (q/'build-corrected.log').read_text() else None,'correction':'Actual eave-area audit all345 plus missing-eave negative control; no production geometry change.'}
(q/'regression-comparison.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
