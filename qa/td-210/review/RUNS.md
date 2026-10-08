# Independent reviewer run record

Executed in the existing workspace against frozen author head dd0fe14672a92990193194741b5fc5580040fafc. Official executable: `/workspace/tokyo-drift-3d/.tools/Godot_v4.7.2-stable_linux.x86_64`. Native runs used Xorg :99, OpenGL compatibility / llvmpipe; no hardware-phone claim. The commands below reproduce these bounded checks; choose a new output directory to retain this review unchanged.

From `/workspace/tokyo-drift-3d`, after `source /workspace/.setup/activate.sh`:

```bash
DISPLAY=:99 .tools/Godot_v4.7.2-stable_linux.x86_64 --path godot --audio-driver Dummy --rendering-method gl_compatibility --rendering-driver opengl3 -s tools/test_kamome_buildings.gd -- /workspace/tokyo-drift-3d/godot/qa/td-210/review/geometry.json
.tools/Godot_v4.7.2-stable_linux.x86_64 --headless --path godot --fixed-fps 60 -s tools/test_lower_city_build.gd
.tools/Godot_v4.7.2-stable_linux.x86_64 --headless --path godot --fixed-fps 60 -s tools/test_lower_city_ramps.gd
.tools/Godot_v4.7.2-stable_linux.x86_64 --headless --path godot -s tools/test_tenjin_buildings.gd -- /workspace/tokyo-drift-3d/godot/qa/td-210/review/tenjin.json
DISPLAY=:99 .tools/Godot_v4.7.2-stable_linux.x86_64 --path godot --audio-driver Dummy --rendering-method gl_compatibility --rendering-driver opengl3 -s qa/td-210/profile/prototype.gd -- legacy /workspace/tokyo-drift-3d/godot/qa/td-210/review/prototype-legacy.json
DISPLAY=:99 .tools/Godot_v4.7.2-stable_linux.x86_64 --path godot --audio-driver Dummy --rendering-method gl_compatibility --rendering-driver opengl3 -s qa/td-210/profile/prototype.gd -- shared /workspace/tokyo-drift-3d/godot/qa/td-210/review/prototype-shared.json
```

Each had stdout/stderr redirected to its corresponding `.log`. Geometry exited0 with20/20; build exited0 with failures0; ramps exited0 with25checks/failures0 but9 script errors and cleanup errors; Tenjin exited0 with82/82; both prototype processes completed with equal native geometry signatures. VSync unsupported warning in native logs is retained. No blanket pass is inferred from exit0.

From empty `/tmp/td210-review-empty`, after the same activation:

```bash
/workspace/tokyo-drift-3d/.tools/Godot_v4.7.2-stable_linux.x86_64 --headless --main-pack /workspace/tokyo-drift-3d/build/td210-before/index.pck -s /workspace/tokyo-drift-3d/godot/qa/td-210/audit_pack.gd -- before /workspace/tokyo-drift-3d/godot/qa/td-210/review/pack-before.json
/workspace/tokyo-drift-3d/.tools/Godot_v4.7.2-stable_linux.x86_64 --headless --main-pack /workspace/tokyo-drift-3d/build/td210-after/index.pck -s /workspace/tokyo-drift-3d/godot/qa/td-210/audit_pack.gd -- after /workspace/tokyo-drift-3d/godot/qa/td-210/review/pack-after.json
```

Both final pack logs report passes=true with1300/1324files and no errors. The first reviewer after-pack invocation used `/tmp` rather than the dedicated empty directory; both initial pack invocations omitted activation and reported unwritable user/font caches. Their JSON/logs are preserved as `pack-*-initial.*`. The changed hypothesis was to activate the existing writable runtime environment and use the documented empty working directory. Final content inventories equal both initial inventories and author inventories; initial environment errors are not erased or mislabeled.

`python godot/qa/td-210/review/audit.py` independently reads the frozen manifests, source/base contents, native caches, all sheet/image hashes, every lot geometry record, cameras, profile values, isolated pack results, original ordinary errors, source GLBs and texture dimensions. It writes reviewer JSONs only. Its `opened_and_visually_inspected` field records actual prior human-facing tool image inspections; running the script alone does not perform visual review or confer a verdict. `raw-regression-audit.json` separately extracts original assertion failures and emitted rows; full signs/drive simulations were not repeated because the matched raw evidence established stable failure identities.

`coordinator-remote-preflight.json` is an attributed copy of parent/root's read-only gh checks at2026-10-08T03:16:48.472545+00:00; reviewer did not perform those remote queries. Review scripts did not change imports, source, runtime presets, author evidence or denied harness logic. No new ordinary smoke or browser capture was fabricated; original ordinary failures were inspected as failures.
