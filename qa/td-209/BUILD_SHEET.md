# Tenjin module and placement build sheet

The original `tenjin_slab` triptych, storefront/prop triptychs and artbook `mock-tenjin.png` / `impl-tenjin.png` were opened before production. Canon: public artbook commit `77c86fed8b8ea21f1a8eebc8fe84cb2bfb7c14bc`, Lower City chapter sections 4 and 11. The source kit's research notes are inspected as provenance, not treated as independently verified architectural history. No external art is imported.

The target is a bronze-edged corporate slot canyon: board-formed concrete, recessed bronze ribbon windows, hard cornices, sealed warm amber lobbies and sparse Showa retail at ground level. No new global lighting or palette work, no cool blue cyberpunk, no fire-escape clutter on these slabs. At 30 m the driver should see entrance depth, columns, mounted Japanese lettering and warm shop displays; at 100 m the original building heights and street trench carry the district.

## Measured source and modular translation

`godot/assets/td-186/source/bld_tenjin.py` authors the unchanged 28 × 20 m source building: 7 m podium, 3.5 m floor pitch, 1.35 m concrete spandrels, 0.45 m window recesses, 2.2 m cornice. Lobby is recessed 4 m; four 1.3 m wide pilotis are at x = -10.5, -3.5, 3.5, 10.5. Main cornice top is 58.2 m; the complete GLB bounds include 9 m flag masts above it. Count is 1,314 triangles including the baked inverted-hull ink.

The original lot polygons are larger than the source wing. Do not scale a complete GLB to each polygon. Derive reusable ribbon-floor, lobby/pilotis, solid podium, cornice and roof-detail portions from the source mesh and its existing atlas, preserving UVs and metre-scale window pitch. Repeat measured lengths; crop residual end bays rather than stretching windows or signage. Keep all 77 original lot indices, footprints and top heights; regular top closures handle fractional final floors. Source GLBs/atlases remain byte-identical.

Use `CityDressing.frontage()` for the primary street. Every exposed perimeter side also receives architectural treatment; corner lots must not show a completed front attached to a blank side. Deterministic choices by lot/edge select window bands, roof details and retail modules. All-lot coverage includes any unhandled geometry as an explicit gap, never silently skipped.

Selected ready storefronts: `kissaten`, `tabako_kiosk`, `yakkyoku`, `sakaya`, `ramen_window`. Preserve authored scale, opaque shop interiors and physically mounted Japanese signage. Selected props: `beacon_pylon`, `curve_mirror`, `tube_pedestal`; place in entrance/forecourt pockets within the lot, never in the through-sidewalk, road, gig stop or Fuel forecourt. No T2/Paper Exchange bespoke work.

## Collision and rendering

The baseline's full-height solid footprint walls do not match an open pilotis arcade. Explicitly use simple upper-wall, inset lobby-wall and column-box proxies there; closed side/service facades remain sealed. Check the opening with negative-controlled horizontal rays, and compare road/drivable collision byte-for-byte. No detailed imported-mesh triangle collision.

Reuse `CityBatch` for merged vertices/UVs, partition imported material families into bounded 200 m cells, keep source materials shared, preserve baked ink surfaces with no extra hull. Building range stays 420 m, detail range 170 m, landmark range 2400 m. No global uncullable MultiMesh, no per-window lights. Maximum 15k triangles per building including ink; building/storefront texture maximum 2048, prop maximum 1024.

## Evidence plan and observed setup issues

All 77 lot instances receive same-camera before/after native diagnostic front surveys; ordinary actual ChaseCam captures across the district's streets are separate, each paired with HUD-hidden world frames. Both native and actual Web export are required. The first perspective survey cropped the ground floor on a narrow street and is retained as a failed smoke; the final survey uses an orthographic front camera fitted to the lot width/height. It is explicitly diagnostic and does not substitute for the perspective driving views.

Initial runtime exposed stale local importer output: cached Tripo and td-119 scenes referenced absent ignored extracted PNGs. Byte-only image extraction first restored pixels, but generic image import disabled mipmaps and made the package spuriously smaller. Those attempts are explicitly retained as partial-import or mipmaps-disabled evidence. The final recovery used native Godot GLB import in a clean scratch project for 29 unchanged GLBs, restored 666 generated files identically to the isolated base and implementation, verified decoded pixel identity, and verified parity again after both editor scans. Final comparisons use these native 3D import settings. Authored asset bytes remain unchanged; see native-import-provenance.json and native_import_cache.py. Native uses Mesa llvmpipe and browser uses SwiftShader; neither is physical-phone performance evidence. Actual Node is 24.19.0, Playwright 1.62.1, Chromium 151.0.7922.173, Godot 4.7.2 ed1daf0bf, Blender 4.3.2.

## Runtime memory lifetime

`CityKitBatch.flush()` releases all source-array, donor, derived-module and merged staging caches after the bounded ArrayMeshes are created. Detailed placement footprint dictionaries are opt-in test evidence; the ordinary game keeps the 77-lot coverage summary but no per-module evidence. A measured 35.5 MB of retained allocation was removed by this change at runtime commit `6f7818b4`. All 62 rendered mesh buffers and cell transforms remain identical to the first frozen architecture commit `847270a4`.

The remaining cost is material: quiet median world construction is 3.866 s versus 0.930 s baseline, and measured static allocation is 294.6 MB versus 133.0 MB. The 758,474 architecture triangles, source textures, render buffers and coverage/collision resources account for the remaining bounded-district cost. This implementation establishes a reusable path; it does not establish physical-phone performance or suitability for indiscriminate whole-city replication.
