The independent review uses the frozen runtime and evidence pins recorded in [report.md](report.md). Source `/workspace/.setup/activate.sh`; use the checkout's official Godot 4.7.2 binary. The validator did not rebuild or change the author exports. Exact shipping PCK hashes are in [frozen-evidence-audit.json](frozen-evidence-audit.json).

The executed commands, return codes and output locations are retained in:

- [Focused check run](independent-focused-run.json).
- [Base/final/repeated-final snapshot runs](snapshot-runs.json).
- [Base/final build regression runs](independent-build-runs.json).
- [PCK audit runs using an empty project](pack-runs.json).
- [Independent actual shipping-entry browser runs](independent-ordinary-runs.json). Both exit 1 intentionally because the strict console test remains failed; see the retained raw logs.

The additional production-default inventory command was:

```sh
source /workspace/.setup/activate.sh
/workspace/tokyo-drift-3d/.tools/Godot_v4.7.2-stable_linux.x86_64 --headless --path /workspace/tokyo-drift-3d/godot -s qa/td-209/review/runtime_inventory.gd -- /workspace/tokyo-drift-3d/godot/qa/td-209/review/runtime-inventory.json
```

It returned 0. Its [raw log](runtime-inventory.log) records 62 meshes, 124 surfaces, 18 shared materials, 758,474 actual array triangles, zero retained placement records and zero unsafe materials.

Independent read-only evidence analyses are reproducible with:

```sh
python /workspace/tokyo-drift-3d/godot/qa/td-209/review/audit_frozen_evidence.py
python /workspace/tokyo-drift-3d/godot/qa/td-209/review/audit_raw_results.py
python /workspace/tokyo-drift-3d/godot/qa/td-209/review/audit_ordinary_entry.py
```

These scripts write review JSON only. They do not rerun the author drive/sign/ramp suites. Those suites were source/read/log reviewed with their inherited failures intact. Matched screenshots were personally inspected through `view_image`, at original detail, with the complete list and SHA-256 values in [opened-images.json](opened-images.json). This review makes no physical-device timing claim.
