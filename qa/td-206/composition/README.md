# td-206: restored-main FuelHud composition repair

Review for [draft PR457](https://github.com/doublehidenblade/tokyo-drift-3d/pull/457). Fuel-owned runtime changes are `fuel_hud.gd` and `fuel_hud_reservations.gd`. Other owners’ HUD sources are unchanged by this correction. Task remains in review; no acceptance or physical-phone verdict is implied.

## Exact sources

- Fuel runtime: `a8d28f00236a5bf5ad229b897b89425cbd01f75b`.
- Restored main: `9d4a88490c41f86e8d34e1c2c6f142838de20c73`, reconciled into the existing fuel branch in `6657b15c82b2d02ce913e13bfd4b19fd63c5e1c5`.
- Unmerged dot446: `64ccf666847499c076edaffcebf2ca303f462a8f`.
- Local-only after combination: `56c2958b06a842b53061dcbef76b6744ab607590`, tree `20ce38798ff625f87e9287dba2516d96e9ebf5c3`.
- Local before combination: `71d8047682361a079c6c506bbc0529ab0b59ed28`, tree `e336694423b8de188864bb8cd441e8eae6964218` (old Fuel on the same restored main and dot).

The reviewer’s separate-executor tree `289ebc2eef5d7bf64c8bb92da7461cf6ee170a1e` was not assumed available. These local combinations are explicitly pinned and never pushed. Later source commits add QA tooling, evidence and documentation only; the two runtime file hashes are recorded in the manifest.

## Change and verification

Fuel discovers sibling canvas layers through its own read-only adapter and reads actual visible/clipped bounds. Placement clears live GigMenu, health, minimap, Wanted/arrest, map/pause and driving controls. When necessary, only Fuel’s range card and service action move apart. An unavailable placement hides that Fuel control instead of overlapping another owner. All normal tested driving states retain both range and service action.

Decorative Fuel containers ignore pointers. The service button accepts only its own rectangle and declines a tap inside another owner’s current bounds, including a control created before the next layout pass. Fuel yields during arrest and an existing map/menu/pause. Closing Fuel cannot release an independently opened GigMenu pause. Explicit payment/game-over modals retain their existing exclusive input/pause behavior.

| Check | Result | Evidence |
|---|---|---|
| Final fixture on old Fuel | 52 failures / 836 checks | [before log](before-final-native.log), [result](before-final/result.json) |
| Actual LowerCity native composition | 772 passed, 0 failed; 76 same-coordinate A/B taps | [after log](after-native.log), [result](after/result.json) |
| Same native camera and viewport | 36/36 pairs match | [camera comparison](same-camera.json) |
| Fuel/economy/physics regression | 62 passed, 0 failed; 8 settlements | [log](fuel-regression.log) |
| Modal ownership regression | 31 passed, 0 failed | [log](modal-native.log) |
| Actual browser composition | 772 assertions passed, 0 failed; 76 A/B taps; raw runner failed on 2 baseline renderer errors | [result](web-after/result.json), [classification](renderer-error-classification.json) |
| Ordinary browser modal/economy | 35 + 10 passed; 0 LowerCity errors | [modal](modal-web/result.json), [economy/reload](economy-web/result.json) |
| Current two-gig road loop | 6.045 km + 0.264 km station leg; 1.191 km reserve, one ¥1200 fill, 0 stuck/failures | [log](two-gig-route.log) |
| Both exported packs | Fuel JSON has 2 stations; Forge source and 119 checked imports absent | [fixture audit](fixture-pack-audit.json), [ordinary-game audit](game-pack-audit.json) |

A/B taps cover Dispatch, offer detail/TAKE THIS GIG, Tracking/Close, failure Retry/New/Close, success TAKE IT/All/Close, minimap collapse/expand/sheet, map/close, pause/Resume and pickup LOAD in both orientations. Native checks additionally include two new controls created directly over Fuel before layout, three modal cycles per orientation, health 45/10/100, minimap and Wanted changes, actual arrest/release and external menu pause ownership. The browser fixture uses real CDP touch events for menu, modal and late-control taps. Its key and held-pedal probes use Godot InputEvents; those are not claimed as independent browser pedal hardware evidence.

The before fixture has more checks because old Fuel remains visible during arrest/modal states; the final fixture checks visibility appropriately and skips bounds for hidden controls. No pass threshold was weakened.

## Pixels

All captures are real LowerCity gameplay with a fixed camera at East Quay. Traffic is disabled and the car frozen only for this UI fixture. World actors can animate between captures. The economy export retains ordinary game entry and traffic.

| State | Old Fuel | Repaired Fuel | Browser |
|---|---|---|---|
| Landscape Retry | [before](before-final/landscape-retry-fuel.png) | [after](after/landscape-retry-fuel.png) | [after](web-after/landscape-retry-fuel.png) |
| Landscape TAKE IT | [before](before-final/landscape-take_next-fuel.png) | [after](after/landscape-take_next-fuel.png) | [after](web-after/landscape-take_next-fuel.png) |
| Landscape health/Dispatch | [before](before-final/landscape-health-10.png) | [after](after/landscape-health-10.png) | [after](web-after/landscape-health-10.png) |
| Portrait Dispatch | [before](before-final/portrait-dispatch-fuel.png) | [after](after/portrait-dispatch-fuel.png) | [after](web-after/portrait-dispatch-fuel.png) |
| Landscape payment | [before](before-final/landscape-fuel-quote.png) | [after](after/landscape-fuel-quote.png) | [after](web-after/landscape-fuel-quote.png) |
| Portrait payment | [before](before-final/portrait-fuel-quote.png) | [after](after/portrait-fuel-quote.png) | [after](web-after/portrait-fuel-quote.png) |

## Retained attempts and limits

- `before/` (28 failures) and `iteration1/` (3 failures) precede final fixture fixes: Resume was still tweening and pedal A/B inherited the previous map state. The final fixture waits for the real tween and resets each pass; `before-final/` still reproduces 52 failures. `iteration2/` has 772 passing candidate checks; `after/` repeats them on the pinned commit.
- `web-launcher-failure/`: QA export helper recognized only a multiline SceneTree entrypoint, so the one-line fixture never ran. Its timeout/zero captures are preserved. The helper now asserts exactly one conversion to a Node entrypoint.
- `web-time-limit/`: the first working browser run reached 25 captures before its six-minute budget, without a final verdict. The final driver allows twenty minutes overall and fails after two minutes without progress. This accommodates software rendering and is not a performance threshold or phone claim.
- **Baseline GAS issue:** landscape GAS held values match with Fuel hidden/shown, but release opens the existing minimap/PaperMap and pauses in both passes. Minimap covers GAS in the same pixels. This is outside Fuel scope and remains unfixed; portrait behaves normally. The A/B evidence records this explicitly instead of counting it as Fuel success.
- Full-source editor import with inherited valid import cache exited 0 with no errors ([log](full-import.log)); both ordinary and fixture exports also completed. This does not establish cold-source import reliability or fix the previously observed Godot CSV translation importer failure. No asset exclusions were invented to obtain this result.
- The composition browser runner retains **failed** status for two triangulation renderer errors despite all 772 assertions passing. [An isolated reproduction](polygon-baseline.log) instantiates only the unchanged DamageBar, with no Fuel or LowerCity, and produces the same error at `damage_bar.gd:171`: a tiny clipped stripe cannot triangulate. That owner code last changed in `090a107` (td178) and is untouched here. [Classification](renderer-error-classification.json) records the limit; no error-free combined browser claim. The probe’s initial compile error is preserved separately.
- Native GLES shutdown reports its existing per-scene texture leaks. Ordinary-menu Web boot has 28 errors for the modal run and 56 across two economy boots, matching the unchanged historical baseline exactly by message multiset ([comparison](boot-error-comparison.json)); both have zero LowerCity errors. No unrelated asset fixes.
- Natural chassis wreck remains an interface dependency. The td204 informational BODY counter is not vehicle-health authority and does not emit `report_chassis_wreck(event_id)`. Cargo failure does not wreck the car. Tests exercise the documented wreck interface.
- Godot 4.7.2 `ed1daf0bf`, Chromium 151 / SwiftShader, 844×390 and 390×844 browser emulation. No physical-phone or real-device FPS acceptance.

## Reproduction and boundaries

Use the pinned local combination, the repository’s Godot 4.7.2 binary, and `tools/test_td206_composition.gd`; native captures take an output path after `--`. `tools/export_td206_wanted_qa.py --fixture tools/test_td206_composition.gd` produces the local fixture export and restores the normal project entry in `finally`. Run `harness/webgl/td206-composition.mjs` against that folder via `WEB_ROOT`. The ordinary Web export uses the unmodified main-menu entry with the local QA wrapper removed. Export hashes are in [fixture manifest](qa-export.json) and [game manifest](game-export.json).

For the pack audit, run `tools/audit_td206_export.gd` from an empty project directory with `--main-pack <index.pck>`, passing [Forge import paths](forge-import-paths.json) and an output JSON after `--`. This prevents source files from satisfying a missing packed resource. All four export presets preserve main’s Forge exclusion; LowerCity Android/Web/macOS also include Fuel JSON. Web Shuto keeps its existing scope.

Muse map/marker/guide/health sources and tasks remain owned by Muse; range/distance integration remains a deferred read-only interface. Claude foundations and assets are preserved. No source on main, Actions, PR merge, game publishing/deployment, external-agent contact or NEON changes. Independent review remains the next acceptance step.
