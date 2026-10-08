# Reproduce td-210

Use the existing workspace and pinned Godot4.7.2 ed1daf0bf. Activate `/workspace/.setup/activate.sh`. Main checkout is `/workspace/tokyo-drift-3d`; isolated baseline `/workspace/td210-baseline` is reviewed0b2652bc. Never use the pre-Tenjin td209 baseline for this comparison. No Actions/deployment required.

Keep `.glb.import` maps and native dependency caches. `complete-asset-importer-parity.json` inventories1331 unchanged source/importer dependencies; `importer-parity.json` retains the exact666 historical native cache hashes. Baseline needs extracted ignored PNG sources as well as cached `.ctex` files for a valid fresh export. See `importer-setup-postmortem.md`. Preserve source import settings, especially mipmaps; do not repeat the rejected byte-only/default-import recovery.

Run commands from game root, writing new outputs to an isolated directory rather than overwriting frozen evidence. Replace the output arguments below. Native/browser access to the retained Xorg/socket requires the tool’s network-enabled sandbox permission.

```bash
source /workspace/.setup/activate.sh
DISPLAY=:99 .tools/Godot_v4.7.2-stable_linux.x86_64 --path godot --audio-driver Dummy --rendering-method gl_compatibility --rendering-driver opengl3 -s tools/test_kamome_buildings.gd -- /tmp/kamome-geometry.json
.tools/Godot_v4.7.2-stable_linux.x86_64 --headless --path godot --fixed-fps 60 -s tools/test_lower_city_build.gd
.tools/Godot_v4.7.2-stable_linux.x86_64 --headless --path godot --fixed-fps 60 -s tools/test_lower_city_ramps.gd
.tools/Godot_v4.7.2-stable_linux.x86_64 --headless --path godot --fixed-fps 60 -s tools/test_lower_city_signs.gd
.tools/Godot_v4.7.2-stable_linux.x86_64 --headless --path godot --fixed-fps 60 -s tools/test_lower_city_drive.gd
```

Run unchanged broad suites in the reviewed baseline too; retain emitted assertions, not just exit status. Their long physics simulations need more than600s on this host. `run_regressions.py`/`run_remaining_regressions.py` record exact run commands, timeouts and observed process results; the latter is historical orchestration with fixed process IDs and is **not** a reusable launch script. `regression-orchestration.md` explains the coordinator transition; no Godot test was paused or altered. Native focused geometry is required because the headless dummy renderer reports identity MultiMesh transforms.

```bash
DISPLAY=:99 .tools/Godot_v4.7.2-stable_linux.x86_64 --path godot --audio-driver Dummy --rendering-method gl_compatibility --rendering-driver opengl3 res://qa/td-210/capture.tscn -- --out=/tmp/kamome-capture --phase=after --kind=all --source=f05048b12c176f9443cfc77e3a1bfb1ec19f62cf
```

The final `capture.gd` supports `--kind=lots`, `routes`, and `overhead`; use separate destinations and combine records by filename if splitting runs. Seed185, original lot indices and street stations are in the script. Routes assert the parked car lies on the authored road and outside lot interiors; offset is bounded by actual width. The overhead mode adds labeled diagnostic target outlines. Original final evidence was assembled from the preserved front sweep, corrected route sweep and annotated overhead sweep. Failed/superseded directories are never final evidence. `make_sheets.py` and `coverage_manifest.py` regenerate the visual index and meaningful lot manifest from originals and geometry-final.

```bash
python godot/qa/td-210/export_capture.py /tmp/kamome-web-capture
node godot/qa/td-210/browser.mjs /tmp/kamome-web-capture /tmp/kamome-browser after f05048b12c176f9443cfc77e3a1bfb1ec19f62cf
.tools/Godot_v4.7.2-stable_linux.x86_64 --headless --path godot --export-release Web /tmp/kamome-shipping/index.html
node godot/qa/td-210/ordinary_entry.mjs /tmp/kamome-shipping /tmp/kamome-ordinary
```

Create export destination directories first. `export_capture.py` copies the QA entry temporarily, records script/config hashes and restores original project bytes in `finally`; it is separate from the ordinary shipping export. Ordinary input uses real keyboard L and ArrowUp, no injected production state. Its strict failures remain explicit. The automatic-review-denied recheck was never executed; do not treat its quoted payload as a reproduction step.

Run `audit_pack.gd` from an **empty working directory** with `--main-pack /absolute/index.pck -s /absolute/godot/qa/td-210/audit_pack.gd -- after /tmp/kamome-pack.json` (use before for baseline). This prevents source files masking missing pack contents. Semantic signatures include imported node transforms, surface arrays, generated LODs, listed material fields and texture paths; the common texture bytes are also compared. This is not a claim that complete packs are byte-identical.

For quiet measurement, run fresh sequential processes with `--headless --path <baseline-or-final>/godot -s qa/td-210/profile/final_world.gd -- /tmp/profile.json`, three alternating pairs after all tests/captures finish. The helper records existing phase boundaries, static/peak allocation before audit serialization, material conversion time and resource counts. Headless static memory excludes GPU memory. The native24-module prototype uses `profile/prototype.gd` with legacy/shared modes; its expanded geometry hash is the equivalence oracle. `source_audit.py`, canonical `snapshot.gd`, and focused Tenjin regression supply preservation evidence.
