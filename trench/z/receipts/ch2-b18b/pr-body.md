## CH2.B18b: a border shorthand with no style keyword paints nothing; border-style revert; animated widths on unstyled sides

Row CH2.B18b in `trench/z/PLAN-z.md` (hub `atlas/z`). Base develop 478cee42. Red: e2d28eba (27 pins), e0a8955f (two pins narrowed to the border axis), b6d96c4c (4 animation pins). Fix: a5ec1dd1, then 18882673 (head).

### Before → after
- **Before:**
  - `border_style_keyword` fell back to RustKit's default `Solid`. So `border: 5px`, `border: thick`, `border-top: 5px` and `border: 5px red` all painted a frame. Chromium 143 paints none: the shorthand resets the style it leaves out to `none`.
  - The same fallback meant `border-style: solid; border: 5px` kept the frame. Chromium clears it.
  - `border-style: revert` / `revert-layer`, the side longhands and `border: revert` were dropped, so the author frame stayed.
  - A keyframe `border-width` on a side with no style painted. The cascade zeroed the width but left the style `Solid`, and the animation wrote the width back afterwards.
- **After:**
  - A shorthand with no style keyword sets `none`.
  - `revert` / `revert-layer` on border styles roll back to the UA. A side the UA styled keeps RustKit's `Solid`: controls, plus the UA arms that set a width (hr, fieldset, dialog, popover), snapshotted by `note_ua_border_sides` before the author rules (`UA_BORDER_STYLE_SIDES`). Every other side is `none`. `revert-layer` is read as `revert`, which is right while no lower cascade layer sets the property.
  - A side that no origin styled is now `none` in style as well as width, and `on_style` zeroes `none` sides again after the animation and transition overlay.
- **Also changes:** a control with `border: 0` now has style `none` and no longer paints the 1px UA stand-in frame. This is the source of both A/B movers below, and it overlaps B18c's `border:0` fix (`atlas/z-ch2-b18c-input-border-width`). The two branches merge cleanly, and so do B17b and E20.

### Pins
- `border_shorthand_no_style_tests::a_border_shorthand_without_a_style_paints_nothing_as_in_chrome` checks 31 cases in `tools/parity_oracle/border_shorthand_no_style_cases.json`, against Chromium 143.0.7499.4 (`grid_flexible_row_log.mjs --file border_shorthand_no_style_cases.json --write`, xywh).
  - It covers the shorthand and side-shorthand forms, stylesheet versus inline order, `revert` / `revert-layer` / side `revert` / `border: revert`, an input (`border:5px`, `border:5px solid`, `revert` back to the UA frame), hr, `::after`, a script style set after layout, keyframes on all sides and on one side, and a transition.
  - Wrong cases: **22 of 27 at the red head e2d28eba (develop code), 2 of 31 at a5ec1dd1 (the two keyframe cases), 0 of 31 at 18882673.**
- Two first-draft pins failed with `border:0` as well, on a path this change does not touch, so they were narrowed to the border axis (e0a8955f). Both are separate gaps; rows wanted:
  - an empty inline `<input>` sits 2px low: y 7 against Chromium's 5;
  - a 0-height `<hr>` reports width 0 from `getBoundingClientRect`, where Chromium reports 400.

### Receipt (hand-written fields; receipt.py is Prometheus's step)
- base 478cee42 / candidate 18882673
- toolchain 1.91.0 (rust-toolchain.toml); host: macOS seat (Darwin 25.5.0); Chrome: campaign baselines chrome-148, pins from the oracle Chromium 143.0.7499.4 (`tools/parity_oracle`)
- parity binaries (`--profile parity`), sha256: candidate 07d8429b46f2c835b8d31545ad4ea05c04f6ae265dc0cdf418ce7c29a2624c8a, base 1854d92af0ef84ed36ef9e63388d43edddfa22351f669d6c3b3670d8b0903ecc
- fixture sha256: `border_shorthand_no_style_cases.json` 91662152259bd270dac58d2e0f53179cc175659580088ea4655111609be87407
- **Campaign at 18882673:** 26/26 pass, 0 cases moved against develop (every diff count is identical).
- **All-site A/B (`ab5.py`, 478cee42 vs 18882673, 20 sites, A,B,A,B): two movers.** Each is 0.00% within each arm, the same on every cross pair, and toward Chrome:
  - **bing 0.12%** (x 200-413, y 174-195): the search box loses the 1px rectangle drawn inside its rounded frame.
  - **wikipedia 0.02%** (y 164-185): the "hide" buttons lose their frame. Chromium's computed style on the live page is `0px none` (probed for B18c).
  - These are the same pixels and values as B18c's A/B movers: both branches remove the stand-in frame from a `border:0` control.
- A/B noise:
  - yahoo (36% / 34%), netflix (4.26%) and squarespace (2.21% in arm B) vary inside one arm.
  - cnn hits the 30 s limit in all four runs (failed 4).
- Engine tests at 18882673 (named filter): `border|anim|transition|computed_read` 131/0 (one thread).
- Headless engine suite at 18882673: **partial: 1099 of 2090 ran before the session cap (1063 ok, 13 ignored, 23 FAILED at default threads, load 14-23 from other seats).** All 23 are GPU-guard waits (backdrop_filter, background_image_fetch, consent_click, computed_read, error_page_script) and **all 23 pass by exact name on one thread** (`rerun-1t.log`, 23/23 in 49 s). The other 991 (`rest.txt`) are owed.

Receipts: hub `trench/z/receipts/ch2-b18b/`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
