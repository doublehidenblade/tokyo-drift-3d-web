# td-293 — cash-only starter upgrades: evidence index

Three money-only upgrades for the starter coupe, bought through a
self-contained mechanic dialog, fitted visibly on the spot:

| Upgrade | Fitting kind | Price |
|---|---|---|
| Roof Light Bar | `roof_light_bar` | ¥1,800 |
| Driving Lamps | `driving_lamps` | ¥2,500 |
| Alloy Wheels | `alloy_wheels` | ¥3,200 |

## Criterion 1 — price grounding

Fare data (`gig_dispatch.gd` + `game_config.gd`): fare =
round((¥900 base + ¥1,400/km × route) × fragility^0.35 / 10) × 10,
routes 900–3,800 m. Cheapest starting gig (sealed documents,
fragility 0.5, shortest route): (900 + 1,260) × 0.7846 = **¥1,690**.
Personal/race fare on the same route: ¥2,160. Two cheapest starting
gigs take ¥3,380 in fares, so the first upgrade (¥1,800) is affordable
after 1–2 starting gigs. The arithmetic is also in
`workshop_catalog.gd` (td-293 section) and is asserted by
`test_td293_cash_upgrades.gd` (`cheapest_starting_fare_yen`,
`first_price_le_two_cheapest_gigs`).

## Criterion 2 — interaction log

`td293-interaction-log.json` (from `tools/test_td293_cash_upgrades.gd`,
production `lower_city.tscn`, attempt-2): money arrives only through
the gig-settlement forward; each upgrade is bought through the dialog's
confirm path; exactly one debit at the listed price per purchase;
balances verified after every step (2000 → 200 → 5200 → 2700 → 3700 →
500). **43 checks, 0 failures.**

## Criterion 3 — before/after capture pairs (same camera, garage)

- `td-293-criterion-3-roof-light-bar-{before,after}.png`
- `td-293-criterion-3-driving-lamps-{before,after}.png`
- `td-293-criterion-3-alloy-wheels-{before,after}.png`

From `tools/capture_td293.gd` on the production scene (attempt-1);
each pair differs only by the one purchased fitment. All personally
inspected by the worker: bar absent → mounted over the roof; bumper
plain → two lit lamp lenses; grey rim → gold alloy with black hub.

## Criterion 4 — dialog captures

- `td-293-criterion-4-dialog-offer.png` — portrait (Gen, mechanic),
  "Roof Light Bar — ¥1,800", his line with price + balance, Buy/Not now.
- `td-293-criterion-4-dialog-insufficient.png` — same panel at ¥0:
  "you're ¥1,800 short. Nothing charged." with Buy disabled.

## Criterion 5 — persistence

`td293-interaction-log.json`: after the three buys, a second
WorkshopService opened on the same store loads balance ¥500 (exact)
and all three fitting kinds. `td-293-criterion-5-persistence.png`
shows all three fitments on the car together.

## Criterion 6 — no regression

Attempt-1 (`attempt-1/runner-summary.txt` + logs): td-200 foundation
95 asserts 0 failures; td-201 reveal matrix 78 checks 0 failures;
td-292 visual panel ALL PASS; the parts-based rack project still
installs after the cash buys (in the td-293 interaction log) and the
cash fittings survive the module install.
Attempt-2 (`attempt-2/runner-summary.txt` + logs): web export rc=0;
`test_lower_city_gig` hit its 900 s bound (rc=124) without completing
a gig — the crawl the task file records for this suite on this VM,
banked as `attempt-2/test_lower_city_gig.log`, stated plainly rather
than retried for hours; `test_td277_vehicles` fails with a parse error in the test
file itself (`test_td277_vehicles.gd:145`) — the control run on the
unmodified golden tree (`attempt-2/test_td277-control-golden.log`)
fails byte-identically, so the failure pre-exists on main and is not
caused by this branch.

Attempt dirs keep the raw per-attempt logs; failed attempt-1's
`test_td293.log` (parse errors in the first draft of the test script,
fixed before attempt-2) is banked there, not hidden.
