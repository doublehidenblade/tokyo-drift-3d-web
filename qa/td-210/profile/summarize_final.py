from pathlib import Path
import json,statistics
q=Path(__file__).resolve().parent
runs={phase:[json.loads((q/f'final-{phase}-{i}.json').read_text()) for i in range(1,4)] for phase in ['before','after']}
result={'scope':'Three alternating fresh sequential headless processes per phase after all capture/regression Godot processes exited. Same final_world helper and seed185. Static memory excludes GPU; this is not physical-device acceptance.','phases':{}}
for phase,rows in runs.items():
 vals={'build_ms':[r['world_stats']['build_ms'] for r in rows]}
 for key in ['static_memory_bytes','static_memory_peak_bytes','material_conversion_us','after_material_conversion_static_bytes','after_material_conversion_peak_bytes','unique_mesh_resources','unique_material_resources','unique_mesh_surface_materials_after_conversion']:vals[key]=[r[key] for r in rows]
 result['phases'][phase]={k:{'runs':v,'median':statistics.median(v),'min':min(v),'max':max(v)} for k,v in vals.items()}
 result['phases'][phase]['stage_median_us']={s['stage']:statistics.median(r['stages'][i]['duration_us'] for r in rows) for i,s in enumerate(rows[0]['stages'])}
result['delta']={k:result['phases']['after'][k]['median']-result['phases']['before'][k]['median'] for k in ['build_ms','static_memory_bytes','static_memory_peak_bytes','material_conversion_us']}
result['kamome_module_timings_median_us']={k:statistics.median(r['world_stats']['kamome']['module_timings_us'][k] for r in runs['after']) for k in ['slice_us','place_us','flush_us']}
result['note']='Earlier profile/reviewed-base-1 used the historical td209 snapshot helper. Final_world also references AnimeLook for conversion instrumentation; the absolute offset against the earlier294.6MB helper has not been independently attributed. Its absolute allocation is not treated as interchangeable. Compare the matched final helper pair309.1→377.1MB. Raw initial/final records retained.'
(q/'final-summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
