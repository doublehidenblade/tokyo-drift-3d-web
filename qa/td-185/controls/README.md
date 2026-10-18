# td-185 round 2 follow-up evidence: touch NITRO, pads clear of the HUD, English controls, the keyboard lesson

Why:
- **NITRO:** the Codex review on the merged #407 found the touch NITRO button and meter gone.
- **Two breakages found on main:**
  - td-203's minimap sat over GAS on any phone held sideways, and a GAS release opened the big map;
  - td-205 removed the board the touch test and Web harness tapped.
- **Craig, 2026-10-07 19:41 UTC:** *"always-on UI should be on the edge of the screen. Actions when
  visiting somewhere should be a more visible button/text centered on screen. What is 配车3 ffod? And still
  seeing 地图 Map. I said only english for UI. Japanese only in environment."*
- **The central HUD design (game-dev-central PR346)** asked the controls owner for no pads on a desktop, a
  first-use keyboard lesson, and safe touch, rotation and release.
- **Craig, on a staged HUD stress screenshot:** *"is this the real screenshot? I can barely see the actual
  game!"* So ordinary driving comes first here, ahead of the stress cases.

**Before** = main 9d4a884; **after** = this branch. Same tool (`tools/capture_lower_city_controls.gd`),
same window, same moment. Composed by `tools/lower_city/compose_controls.py`. Every image was opened and
checked before being listed.

## Sheets

- `gameplay.jpg`: **ordinary driving**, the frame a player sees most. A gig is on, the car is moving and
  nothing is open, on a phone held sideways (844×390) and on a computer (1280×720).
  - **Main:** a big umber card, the touch pads on the computer, and GAS under the minimap on the phone.
  - **This branch:** the card is a compact corner block of outlined text; the pads appear only on the
    phone, in its bottom corners; the street is in view. On a phone the card is drawn ×1.15 sideways and
    ×1.4 upright, because the 1280-wide canvas is shown on a narrow screen.
- `gameplay-upright.jpg`: the same, upright (390×844) and at 1920×1080.
- `touch-sideways.jpg` — a phone held sideways (844×390).
  - **Main:**
    - GAS sits under the minimap; only BRAKE shows;
    - no NITRO;
    - bilingual labels;
    - 積込 LOAD sits at the bottom edge between the pads.
  - **This branch:**
    - BRAKE (a wide pad) and GAS (a long ribbed pedal) side by side below the minimap;
    - NITRO above the left arrow;
    - English labels;
    - LOAD CARGO across the middle of the screen.
  - **Second row:** main's settle panel, and GAS + NITRO held by touch (the boost fires and the meter drains
    with the car's own bar).
- `touch-upright.jpg` — the same phone upright (390×844): taller pedals, LOAD CARGO in the middle of the
  road, NITRO, and the settle panel with the pads clear.
- `desktop.jpg` — a computer at 1280×720 and 1920×1080.
  - **Main:** the touch pads and a MAP pad on a desktop. The project emulates touch from the mouse, so the
    old touch-screen test is true on every computer.
  - **This branch:**
    - the keyboard lesson before the first drive (paused);
    - no pads and no space kept for them;
    - LOAD CARGO / Press E.
- `web.jpg` — the real Web export (`harness/webgl/lower-city-entry.mjs`).
  - **A phone:** Android Chrome's user agent, touch events, 390×844, then turned to 844×390.
  - **Computers:** 1280×720 and 1920×1080, driven by keys.
  - Every step asserts the game's state (`window.__lowerCityState`); the step list is in `tests/web/lower-city-entry.json`.

Japanese left on the HUD in these frames is not this branch's to change. The owners have been told:
- td-205 (Muse): the 配車 / 配送中 tab and the gig menu panels;
- td-203 (Muse): the minimap's `－` (U+FF0D, drawn as a missing-glyph box reading "FF0D", Craig's "ffod")
  and `地図＋`; the big map's title bar `下町 道路地図`, `北` and the legend (`凡例 LEGEND`, `大通り avenue`, …) in
  `map_sheet.gd`;
- td-204 (Muse): the meter captions and states.

## Tests — `tests/`

| suite | result |
|---|---|
| `tools/test_lower_city_touch.gd` | 31/31. The gig menu by tap: 配車, an offer, TAKE (scrolled into view; it sits below the fold). MAP / × CLOSE. Two thumbs. NITRO fires, and its meter follows the bar. A pause releases pedals and NITRO. LOAD by tap. Fonts. Seven screen shapes: every pad's touch area clear of every HUD control, and a GAS hold and release opens nothing. Negative controls at round 2's GAS spot: it is under the minimap, and with the guard off its release opens the big map. A rotation lets go of a held GAS, and that finger then does nothing. |
| `tools/test_lower_city_lesson.gd` (new) | 28/28. On the first visit the lesson is up and the city paused, with no pads. Any key puts it away and does nothing else. It is remembered. Every listed key is pressed and checked against its owner: W/Up, S/Down, A/D/Left/Right, Space, G, Tab, M, C, Esc, E, H. Negative control: T, which is not listed, does none of them. A second visit does not show it, and H brings it back. A touch device never gets it. |
| `tools/test_lower_city_gig.gd` / `gigmenu` / `build` | **PENDING** at c351562: running now, and their results are added when they finish. Earlier, at 405df0d, they passed: 4/4 deliveries (¥16,130, the same as round 2) / 0 failures / 0 failures (`tests/at-405df0d/`). |
| `tools/capture_lower_city_controls.gd` | `tests/captures.txt`: each frame's moment (phase, pads shown, speed, NITRO and its bar). Main's sideways run logs "the GAS release opened the big map", and main's computer runs show the pads (`pads=true`). This branch's runs log neither. |
| CI repro, clean worktree at the head | Import 0 errors; Web and Web Shuto exports 0 error lines; `entry.mjs`, `shuto-entry.mjs` and `lower-city-entry.mjs` pass (45 steps, 0 errors, 0 warnings). See `tests/ci-repro-status.txt` and `tests/web/lower-city-entry.json`. |

Every frame, the touch and lesson logs and the CI repro are from c351562, the last code commit (the gig, gigmenu
and build runs there are PENDING); the commits after it change
docs and evidence only. The "before" frames are main 9d4a884, shot by the same tool.
