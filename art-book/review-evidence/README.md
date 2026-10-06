# Worker verification — 2026-10-06

Design documentation only; **in review, not independent acceptance**. No gameplay/economy prototype, performance measurement or player study was run. The future playtest targets in the research spread are not reported results.

- Baseline main: `2e8c63e3030247fc90e0eea273867181bd5d1098`.
- Verified candidate HTML Git blob: `3ae6b97abbf130e92fa76bb0ff150882231fb972` (`git hash-object art-book/index.html`). The PR commit identifies the complete candidate; this blob pins the actual rendered file without a self-referential commit hash.
- Local server: `python3 -m http.server 8765 --bind 127.0.0.1 --directory /workspace/tokyo-drift-3d-web`.
- Chromium `151.0.7922.173`, Playwright `1.62.1`, Node `v24.19.0`. Viewports: 1440×1000 desktop and 390×844 phone emulation. This is browser layout evidence, not a physical-phone verdict.
- Reproduce from repo root: `PLAYWRIGHT_MODULE=/path/to/playwright node art-book/review-evidence/verify.cjs` with the local server running. Override `CHROMIUM_PATH` or `ARTBOOK_URL` if needed. The script uses the pinned baseline HTML for before captures and the local candidate for after captures.

## Results

`browser-results.json`: zero browser page errors, broken in-page anchors, duplicate IDs or missing local files; all 47 existing gallery images respond successfully. Document width equals viewport width at both sizes. New wide tables scroll within their containers rather than widening the page. The TOC research link was clicked successfully; ArrowRight scrolled the focused comparison table on the phone viewport.

Personal visual inspection covered both before cover images and all 16 after images (`cover`, `loop`, `economy`, `ticks`, `garage`, `research`, `roadmap`, `tests` × desktop/phone). Text and headers are legible, the warm original style is retained, and new tables have room for words. The initial candidate squeezed reference/chain names; minimum table width, first-column space, themed links, keyboard focus and a mobile scroll hint corrected that before these retained captures. Phone table screenshots intentionally show a partial table with a visible horizontal-scroll instruction.

`git diff --check` passes. Upper City/Outskirts chapter files, existing image binaries, root export/deployment files, game code, worker branches and central coordination state are unchanged. GitHub Pages was read-only checked: publication source is `main` at `/`; the new draft branch is not that source. No Actions workflow was dispatched, no merge or live publication performed, no paid/provider generation used.

## Handoff

Review the four chapter diffs and `../design-review.md` together. Craig's unresolved decisions are listed there: pressure level, trading timing, material rewards, clock/recovery policy and fleet scope. The upstream `~/workspace/game-design/` bible files are unavailable here and require reconciliation before regenerating this book elsewhere. The draft remains open for design review; no task was marked accepted or reassigned.
