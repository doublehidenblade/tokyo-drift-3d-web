# td-185 round 2 evidence — Craig's v42 phone test (Android Chrome, 2026-10-06)

Craig: taps on the offer board, MAP and BRAKE did nothing, so no delivery could be made; he asked for ◀ ▶ on
the left and accelerate / decelerate on the right, and tap-to-interact at a pickup / drop-off. On the Ring:
street lights clipping the ramp, no leeway to merge and no rail at the ramp's end ("I flew off the other
end"), and a U-shaped trap at ground level. His two screenshots: `todos/td-185-round2-v42/reference/`.

**Before** = the v42 world (the build at d787160, whose Lower City geometry is v42's 5358e64; round 2's
touch input already in). **After** = this PR. Same tool, same camera, same moment in both. Every image was
opened and checked before being listed. Composed by `godot/tools/lower_city/compose_round2.py`.

## Taps and the touch layout

- `touch-web.jpg` — the real Web export (`harness/webgl/lower-city-entry.mjs`, headless Chromium + SwiftShader,
  720×1280 phone viewport) driven by touch events, the path Craig's taps took: the city pads (◀ ▶ bottom-left,
  ▲ アクセル / ▼ ブレーキ bottom-right); a tap on offer 1 takes the run (the job card); a tap on MAP opens the
  paper map, × 閉じる closes it; ▲ and ▶ held with two thumbs drive the car. Each step asserts the game's
  state (`window.__lowerCityState`: gig phase, map, pause, pedals), not just a picture —
  `tests/web-lower-city-entry.json`.
- `gig-touch.jpg` — a whole delivery with the touch layout (Starlight Lounge → Gate 2, fresh fish, 2.51 km,
  2:23 of 4:15, cargo 100%, ¥4,900): the amber 積込 LOAD button appears when the car is stopped in the pickup
  bay, 荷降ろし UNLOAD at the drop-off (E on a keyboard).
- The in-engine proof is `tools/test_lower_city_touch.gd` (15/15): real InputEventScreenTouch through the
  viewport, with a negative control (round 1's shape — a full-screen touch layer on top of the HUD's layer —
  swallows the tap).

## The highway

- `craig-lamp-in-lane.jpg` — Craig's screenshot 1 beside the v42 build and this PR from the same spot
  (portrait chase camera): Tenjin Odori's street lamp stood where the Tenjin-kita outer on-ramp flies over
  the avenue — a solid post in the ramp's lane. Now no street lamp or junction beacon stands within
  `city_lamp_clear` (2.5 m) of a raised deck: 36 left out, among them the trench lamps that pierced the
  Ring's lid.
- `craig-ramp-top.jpg` — Craig's screenshot 2: the same ramp's top. v42: the ramp just ends, 7 m of air past it.
  Now a 70 m merge lane (`city_merge_lane`): full width for 40 %, then a taper into the Ring's parapet,
  decked, with a rail on its outer edge; the 河岸 420m sign's post stands outside it.
- `blind-run.jpg` — the run Craig made, done blind: full throttle, wheel straight, the same run in both
  builds. v42: the car hits the lamp post at 108 km/h, drifts off the ramp's deck side where the ramp ran
  below the Ring's edge with no rail, and drops 7 m to the boulevard. Now: up the ramp, along the merge
  lane, the taper's rail steers it onto the Ring at 108 km/h.
- `ramp-mouth.jpg` — the U-shaped trap: each solid ramp's tall end stood open to the boulevard's slot (a
  hollow channel between the ramp's side walls). Now closed by a wall with a yellow-and-black board (12).
- `merge-lane.jpg` — the merge lane (left) and the diverge lane before the inner off-ramp (right) from above,
  with the edge lines broken where a ramp joins; and the Ring's curves: the deck was built from 2 m quads with
  per-segment edge normals, which left a crack up to 0.22 m wide every 2 m round each curve, in the collider
  and the parapets too. The deck edges are mitred now.

## Tests — `tests/`

| suite | result |
|---|---|
| `tools/test_lower_city_ramps.gd` (new) | 25/25 — blind full-throttle runs up all 6 diamond on-ramps (none drops below the deck) and into all 12 ramp ends (none gets in); an edge sweep of the Ring, the merge lanes and every raised ramp (no unguarded drop of 0.6 m or more); lamp clearance (600 lamps clear, the 36 left out all stood by a raised deck). Negative controls on round 1's shapes: with no merge lane the blind car flies off Craig's ramp; with the ends open it drives 114 m into one; the edge sweep finds 36 unguarded drops |
| `tools/test_lower_city_touch.gd` | 15/15 |
| `tools/test_lower_city_build.gd` | 0 failures |
| `tools/test_lower_city_drive.gd` | 21 legs, 19.54 km, 0 failures (the Ring's ramps and merges included) |
| `tools/test_lower_city_signs.gd` | 12 trips, 0 failures; signs-only table unchanged from round 1 |
| `tools/test_lower_city_gig.gd` | 4/4 deliveries |
| CI repro, clean worktree at ea3b075 | import 0 errors; Web and Web Shuto exports; `entry.mjs`, `shuto-entry.mjs`, `lower-city-entry.mjs` all pass (`ci-repro-status.txt`) |
