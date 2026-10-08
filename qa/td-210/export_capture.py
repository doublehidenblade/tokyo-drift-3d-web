"""Export the actual Lower City with a diagnostic entry; restore all product config bytes.

Usage: python3 godot/qa/td-210/export_capture.py build/td210-before-capture
The ordinary Web build is exported separately to measure the shipping package.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
config = root / "project.godot"
original = config.read_bytes()
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
script = root / "scripts/qa/td210_capture.gd"
scene = root / "scenes/qa/td210_capture.tscn"
script.parent.mkdir(parents=True, exist_ok=True)
scene.parent.mkdir(parents=True, exist_ok=True)
assert not script.exists() and not scene.exists(), "Refuse to replace existing QA runtime files"
script.write_bytes((root / "qa/td-210/capture.gd").read_bytes())
scene.write_text((root / "qa/td-210/capture.tscn").read_text().replace("res://qa/td-210/capture.gd", "res://scripts/qa/td210_capture.gd"))
source_files = [p for p in (root / "scripts").rglob("*.gd")]
source_files += [root / "data/lower_city/city.json", root / "export_presets.cfg", script]
source_hashes = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files}
try:
    config.write_bytes(re.sub(rb"^run/main_scene=.*$", b'run/main_scene="res://scenes/qa/td210_capture.tscn"', original, flags=re.M))
    subprocess.run([str(root.parent / ".tools/Godot_v4.7.2-stable_linux.x86_64"), "--headless", "--path", str(root), "--export-debug", "Web", str(out / "index.html")], check=True)
finally:
    config.write_bytes(original)
    script.unlink(missing_ok=True)
    scene.unlink(missing_ok=True)
html = (out / "index.html").read_text()
html = html.replace("if(new URLSearchParams(location.search).has('selftest'))window.tdGamePrepared();", "window.tdGamePrepared();")
(out / "capture.html").write_text(html)
(out / "provenance.json").write_text(json.dumps({
    "source": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
    "source_sha256": source_hashes,
    "config_restored": config.read_bytes() == original,
    "entry": "Diagnostic Node loads unchanged res://scenes/lower_city/lower_city.tscn",
    "sha256": {f: hashlib.sha256((out / f).read_bytes()).hexdigest() for f in ["index.pck", "index.wasm", "capture.html"]},
}, indent=2) + "\n")
