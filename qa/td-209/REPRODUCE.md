# Reproduce td-209 evidence

Use the exact installed Godot 4.7.2 binary; system Godot 4.6.3 is incompatible with this task. Paths below describe the recorded workspace. Production source is 6f7818b45cd09ade3ca621354ce4eb116050a66b; the isolated baseline worktree is ad4f24229a7ba80e25e3d4ddc1e83a33f3db0c47. Use separate worktrees, never label a current modified tree as a baseline.

```bash
source /workspace/.setup/activate.sh
cd /workspace/tokyo-drift-3d
.tools/Godot_v4.7.2-stable_linux.x86_64 --version
```

The final native GLB importer recovery is reproducible without editing authored asset bytes. Use a fresh scratch directory; the script rejects a reused one. It preserves imported 3D mipmap settings and verifies existing decoded pixels before copying generated outputs. Editor scans in both worktrees follow recovery; 666 generated files were subsequently compared byte-for-byte. The exported common texture audit is an additional parity check.

```bash
python3 godot/qa/td-209/native_import_cache.py /workspace/tokyo-drift-3d/godot /tmp/fresh-td209-native-import /workspace/td209-baseline/godot
.tools/Godot_v4.7.2-stable_linux.x86_64 --headless --editor --path godot --quit
.tools/Godot_v4.7.2-stable_linux.x86_64 --headless --editor --path /workspace/td209-baseline/godot --quit
```

Focused geometry/material/clearance tests collect detailed placement evidence explicitly. The snapshot helper runs unchanged against both trees, preserving protected outside-Tenjin visual buffers and road/wall collision hashes. `benchmark.gd` runs sequentially in fresh processes on a quiet host; it does not measure rendering FPS. Raw commands and sampled RSS are retained in benchmark JSON. `run_checks.py` records exact source hashes and raw broad-regression logs.

```bash
.tools/Godot_v4.7.2-stable_linux.x86_64 --headless --path godot -s tools/test_tenjin_buildings.gd
.tools/Godot_v4.7.2-stable_linux.x86_64 --headless --path godot -s qa/td-209/snapshot.gd -- /tmp/td209-final-world.json
.tools/Godot_v4.7.2-stable_linux.x86_64 --headless --path /workspace/td209-baseline/godot -s /workspace/tokyo-drift-3d/godot/qa/td-209/snapshot.gd -- /tmp/td209-base-world.json
python3 godot/qa/td-209/run_checks.py /workspace/tokyo-drift-3d reproduced build ramps signs drive
```

For native capture use the existing root-managed Xorg dummy display `:99` with OpenGL3, Dummy audio and fixed 60 simulation FPS. The same `capture.gd` runs both phases; copy only the QA helper/scene to an isolated baseline. It loads the actual unmodified Lower City scene, parks the player and records every camera transform and seed. `--kind=all` is 77 front surveys plus 60 street frames. Results/screenshot paths are written directly by Godot. Use a fresh output path to retain existing evidence.

```bash
DISPLAY=:99 .tools/Godot_v4.7.2-stable_linux.x86_64 --path godot --rendering-driver opengl3 --audio-driver Dummy --fixed-fps 60 res://qa/td-209/capture.tscn -- --phase=after --kind=all --out=/tmp/td209-native-after --source=6f7818b45cd09ade3ca621354ce4eb116050a66b
```

Ordinary export and diagnostic export are separate. `export_capture.py` copies the QA script/scene into temporary exported locations and restores product config bytes in `finally`. Its output provenance records script/config/pack hashes. The baseline version of this helper runs inside the isolated baseline. No exported PCK is committed or published.

```bash
mkdir -p build/td209-reproduced-game
.tools/Godot_v4.7.2-stable_linux.x86_64 --headless --path godot --export-debug Web /workspace/tokyo-drift-3d/build/td209-reproduced-game/index.html
python3 godot/qa/td-209/export_capture.py build/td209-reproduced-capture
node godot/qa/td-209/browser.mjs build/td209-reproduced-capture /tmp/td209-browser-after after 6f7818b45cd09ade3ca621354ce4eb116050a66b
node godot/qa/td-209/ordinary_entry.mjs build/td209-reproduced-game /tmp/td209-ordinary-entry
```

Browser harness uses installed Chromium 151.0.7922.173, Playwright 1.62.1 and Node 24.19.0, SwiftShader, real WebGL2 game export and original canvas PNGs. Run software renderers sequentially on this 4-core host. The ordinary entry harness loads `/` without selftest flags, presses the menu's actual L shortcut, waits for the scene's existing readiness signal and uses ArrowUp input. It does not inject gameplay state or modify owner code.

Run `audit_pack.gd` from an empty project directory using `--main-pack` so source files cannot satisfy missing packed resources. The audit verifies exact selected kit presence/loadability, Fuel JSON, exclusions and semantic imported-mesh content.

```bash
mkdir -p /tmp/td209-pack-audit
.tools/Godot_v4.7.2-stable_linux.x86_64 --headless --path /tmp/td209-pack-audit --main-pack /workspace/tokyo-drift-3d/build/td209-final-released/index.pck -s /workspace/tokyo-drift-3d/godot/qa/td-209/audit_pack.gd -- after /tmp/td209-pack-after.json
python3 godot/qa/td-209/review_sheets.py
```

`review_sheets.py` only lays out scaled, labelled original screenshots. Final hashes, pins and original-to-sheet mappings are committed alongside this guide. No Actions were dispatched, no main branch was edited/merged, and no deployment was performed.
