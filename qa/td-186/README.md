# td-186 Asset Forge — evidence

Everything here is produced by the scripts in `godot/assets/td-186/source/` and `godot/tools/td186/` (see
`godot/assets/td-186/ASSET_INDEX.md` for the assets themselves and their specs). Mirrored to the public web repo
(`tokyo-drift-3d-web`, branch `ccr-4570dae0-xgbjgu`, `qa/td-186/`) so the PR can show the images.

## Triptychs — reference → mock → render (`triptychs/`)

One per asset type, each three panels: (1) the real Showa reference, cited by name, place and year with the
grounded research bullets and sources, plus the art book's canon plate; (2) the two AI-generated mock layers,
[REFERENCE] and [IMPLEMENTATION], labelled as Gemini output; (3) the shipped GLB rendered in Godot 4.7.2 under
AnimeLook + the Trench palette + the district's dust at the chase camera's 70° FOV, with the GLB's stats.
Phase B and C triptychs also state what the model was built to (`vehicle_spec.json` / `pedestrian_spec.json`) and
what the GLB or the validator measured. Composed by `source/triptychs.py` (`python3 triptychs.py [id ...]`).

| Phase | triptychs |
|---|---|
| A — buildings | [A1 chidori_terrace](triptychs/chidori_terrace.jpg), [A2 kamome_hall](triptychs/kamome_hall.jpg), [A3 tenjin_slab](triptychs/tenjin_slab.jpg), [A4 kotobuki_bay](triptychs/kotobuki_bay.jpg), [A5 daikoku_tally_office](triptychs/daikoku_tally_office.jpg), [A6 depots_goods_shed](triptychs/depots_goods_shed.jpg) |
| A — storefronts, props | [A7 storefront_kit](triptychs/storefront_kit.jpg) (8 shops), [A8 props_kit](triptychs/props_kit.jpg) (16 props) |
| B — vehicles | [B1 sedan](triptychs/vehicle_sedan.jpg), [B2 taxi](triptychs/vehicle_taxi.jpg), [B3 kei_van](triptychs/vehicle_kei_van.jpg), [B4 kei_truck](triptychs/vehicle_kei_truck.jpg), [B5 kei_trike](triptychs/vehicle_kei_trike.jpg), [B6 box_truck](triptychs/vehicle_box_truck.jpg), [B7 bus](triptychs/vehicle_bus.jpg) |
| C — pedestrians | [C1 peds_kit](triptychs/peds_kit.jpg) (4 variants, 6 clips) |

## The rest

- `renders/<id>/` — every in-engine view (1280×720 PNG) and `capture_<layout>.json` (camera, look stats).
  Layouts: `godot/tools/td186/layouts/`; vehicles framed by projection (`source/vehicle_layouts.py`), the
  pedestrian kit posed by each GLB's own AnimationPlayer (`source/ped_layouts.py`). Render one:
  `godot/tools/td186/render.sh <layout> [id]`.
- `mocks/` — the accepted [REFERENCE] / [IMPLEMENTATION] mocks with their provenance JSON (model, prompt,
  style references by art-book path). **`mocks/rejected/`** keeps every rejected mock with the reason in its
  file name (26: unmasked or partly visible faces, English or Latin lettering, garbled kanji, a rayed sun badge
  that reads as the Rising Sun flag, a brand badge, a bonneted truck where the canon is cab-over, ...). Review
  is by eye against the canon; the fixes that held are in `godot/docs/lessons/LESSONS.md`.
- `research/` — grounded research notes (Gemini + Google Search grounding) with the questions, the answer
  and every source; the triptychs quote them. Photos could not be fetched here (the network policy denies
  every photo host tried), so each reference is cited, not shown.
- `reports/` — per-GLB reports (triangles, materials, opacity, bounds, atlas use, animations).
- `atlases/` — the painted poster-colour atlases (albedo), for inspecting signage and texel density.

## Validator

`.tools/Godot_v4.7.2-stable_linux.x86_64 --headless --path godot -s tools/td186/test_td186_assets.gd [-- --verbose]`
→ `TD186_RESULT checks=900 failures=0 glbs=44`: budgets, opacity, culling, ink shells; every vehicle against
its spec (nodes, hubs, dimensions, every lamp lens outside the body); every pedestrian against its spec
(skeleton, clips, loops, height, foot slide 0.017 m/s walking / 0.032 m/s running); the Mixamo pipeline on its
fixture (clips crossing a T-pose and an A-pose rig both ways, measured against each clip on its own rig).
