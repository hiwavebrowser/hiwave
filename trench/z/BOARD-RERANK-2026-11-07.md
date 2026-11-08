# Chrome board re-rank, 2026-11-07 (CH2.B29 follow-up)

Board: batch38 `cb-cand2` (cand38 = develop `c7209173`), 16/42 green, 26 red.
Method (scripts in the impl-b29 scratchpad: `geo.py`, `rerank.py`, `cf.py`, `freeze.py`):

1. **Geometry**: `layout_oracle_gate.compare_case` on each red row. Every failing box is either
   **carried** (its delta equals what its parent or previous in-flow sibling already moves by:
   same-axis parent delta, parent edge, centring, or previous sibling's end) or a **root**.
   Each root is classified from Chromium's computed style (an extra headless probe of the same composed pages:
   tag, own text, emoji/symbol code points, font family, display).
2. **Pixels**: the red pixels of the board's `diff.png`. A pixel inside a box (Chrome rect or RustKit box) that has
   a geometry delta counts as **geometry**, and it follows the carried chain back to its root's class. Every other
   pixel counts as **raster**, tagged with the techniques of the innermost element that paints it
   (box-shadow, gradient, background-clip:text, z-index on the chain, letter-spacing, system font, form control, …).
3. **Counterfactuals** (what decides the ranking): attribution only estimates. For each candidate we inject CSS that
   pins the value Chromium already computes (so the Chromium arm doesn't change), re-run only RustKit on the batch38
   composed page and actions, and re-score against the batch38 Chromium captures with the board's own
   `compare_pixels`/`compare_geometry`. The baseline re-run matched the board (report/default/1280: 1.120 %, 69 geometry).

## The headline

- **Rule 2 (0 geometry, ≤1.5 %) can't flip any red row with one fix.** Every red row has 10–44 geometry roots
  spread across at least 2 cause classes, and 20 of 26 also have join failures (chrome: 8–11, inspector: 28,
  report: 1). Rule 1 (≤0.5 %) is the only rule a single technique can move.
- **The CH2.B29 catalog techniques are raster-small.** On every red row, inset box-shadow, gradients,
  background-clip:text, z-index, letter-spacing, background-size/position, appearance/accent-color and filter
  account for ≤0.06 % of the viewport each. **None of them flips a row by itself under either rule.**
- **Geometry owns most of the red.** On the 20 chrome/settings/report rows, 85–99 % of the differing pixels sit in
  boxes with a geometry delta. On the inspector rows, raster owns most of it (selection highlight, monospace text).
- **Top single fix: UA `em` margins.** Chromium resolves the UA sheet's `p`/`h1-h6`/list/`blockquote`/`figure`/`pre`/`hr`
  em margins against the element's own font-size. RustKit hard-codes them as px at 16px. `<p class=subtitle>`
  (font-size 0.9rem) under each page's `h1` is 1.6 px low on settings and report, and that shift carries every
  box below it: 256 → 168 geometry diffs on settings and 69/94 → 21 on report. It is the only measured fix that
  flips rows by itself.

## Technique → rows → share → flips alone

The share is the % of viewport pixels on the rows it touches (mean / max). The flip columns come from counterfactuals
where they were measured (**M**). Otherwise they are the attribution estimate (pct − share ≤ 0.5), marked **E**.

| technique / cause | kind | red rows touched | share of viewport % (mean / max) | flips alone, rule 1 | flips alone, rule 2 |
|---|---|---:|---|---|---|
| **UA em margins resolved at 16px** (`p.subtitle` under h1; settings + report) | geometry | 9 | settings 1.66→0.86, 2.06→1.06, 1.44→0.73; report 1.12→0.52, 1.60→0.73, 0.77→**0.34**, 1.21→0.52, 1.73→0.74, 0.83→**0.34** | **2 (M)**: report default + weekly 1600; report 1280 ×2 land at 0.517/0.519 | 0 (M: 21 geometry diffs + 1 join remain on report) |
| emoji / symbol glyph metrics (sidebar action icons ⚙🛡🚫📈, lock buttons 🔓, ⌘⇧↵ kbd, ⬇ 🕑) | geometry | 15 | 0.10 / 0.38 (attribution); chrome/default/1280 2.09→1.28 (M) | 0 (M: downloads_open 0.546→0.539, 0.780→0.722) | 0 |
| form control intrinsic size (select width −22px, checkbox margin, text input height, button UA size) | geometry | 17 | 0.18 / 0.39 | 0 (M: settings selects+inputs 0.864→0.818; downloads_open 0.546→0.528) | 0 |
| "container layout" (sidebar section/entry heights with no leaf root: workspace entry +3, shelf list) | geometry | 12 | 1.06 / 1.39 | 0 (E) | 0 |
| text metrics (label/inline widths ±7px; mostly carried shifts) | geometry | 23 | 0.58 / 1.90 | E says 4, M says 0 (the settings share is the em-margin shift above) | 0 |
| inline text box baseline (`span.time-format` y +0.9 on report) | geometry | 9 | — (attribution mixes it with the em shift) | 0 | 0 |
| Chart.js canvas size (`#activityChart` −1150×−300) | geometry | 6 | 0 in viewport (below the fold) | 0 | blocks rule 2 on all 6 report rows |
| monospace text metrics (inspector style values y +0.6) | geometry | 3 | 0.14 / 0.19 | 0 | 0 |
| join: className with two spaces (`workspace-tab  locked` selector key), svg `<path>` boxes, inspector `dom-node-line selected` missing in RustKit, empty `#error-container` | join | 20 | — | — | blocks rule 2 on every chrome, inspector and report row |
| selection highlight / plain bg box (inspector) | raster | 3 | 1.55 / 1.62 | 0 (E) | 0 |
| monospace glyph raster (inspector) | raster | 3 | 1.33 / 1.85 | 0 (E) | 0 |
| system font text raster (CoreText vs Skia AA) | raster | 26 | 0.08 / 0.21 (+ "text" 0.25 / 1.89) | 0 (E) | 0 |
| border-radius edges | raster | 17 | 0.09 / 0.16 | 0 | 0 |
| inset/outer box-shadow (B29 #1) | raster | ≤2 | <0.01 | 0 | 0 |
| gradients (B29 #2) | raster | 21 | 0.018 / 0.059 | 0 | 0 |
| background-clip:text (B29 #3) | raster | 21 | 0.018 / 0.059 | 0 | 0 |
| z-index incl. negative (B29 #4) | raster | 0 measurable | 0 | 0 | 0 |
| letter-spacing / text-transform (B29 #5) | raster | 12 | 0.007 / 0.024 | 0 | 0 |
| appearance / accent-color (B29 #7) | raster | 17 | 0.030 / 0.059 | 0 | 0 |
| svg | raster | 16 | 0.010 / 0.039 | 0 | 0 |

Per page:

- **chrome** (14 red): 35–44 roots each. The biggest geometry share is sidebar vertical rhythm: action items differ
  by ±6px with emoji icons, and ⚙ (U+2699, text presentation in Chromium) is drawn as a colour emoji 10.6px wider.
  Then form controls (`#modeSelector`, lock buttons, `#urlInput`) and the right-sidebar collapsed panel widths.
  Joins: the `workspace-tab  locked` double-space className and the two logo `<path>`s.
- **settings** (3 red): after the em-margin fix and pinned select/input sizes, the viewport has **0 geometry diffs**
  and is still 0.82 % raster. The remainder is text AA, plus centred text in `<input type=number>` that RustKit
  left-aligns.
- **report** (6 red): after the em-margin fix, 21 geometry diffs remain. The viewport ones are `span.time-format` +0.9
  and export-button heights −7; the canvas sizes are below the fold. 1600-wide rows flip under rule 1. 1280 rows end at 0.517/0.519.
- **inspector** (3 red): raster-dominated. The selected DOM line (`dom-node-line selected`) is missing in RustKit
  (a join failure and ~1.5 % of the viewport), then monospace glyphs.

## Pick

**CH2.B30: UA em margins** (no architecture dependency; not B15/LAT11). It flips 2 rows by itself (measured), takes
settings from 256 to 168 geometry diffs and report from 69/94 to 21, and it is a general engine defect: any page that
restyles a `p`, a heading or a list's font-size and keeps the UA margins is affected. Next by measured share:
emoji/symbol glyph metrics on the chrome rows (2.09→1.28 on chrome/default/1280, 0 flips alone). Then the join
failures, which block rule 2 everywhere.

## Result (CH2.B30, branch `atlas/z-board-ua-em-margins` @ `44b69341`, red `8828d284`)

The full board was re-run with `parity-capture` built from the branch (cand38 + 2 commits). Rows flipped and none worse:

| row | pixel % | geometry | gate |
|---|---|---|---|
| report/default/1600x1000 | 0.773 → **0.337** | 69 → 21 | red → **pixel** |
| report/weekly/1600x1000 | 0.829 → **0.339** | 94 → 21 | red → **pixel** |
| report/default/1280x800 | 1.120 → 0.517 | 69 → 21 | red |
| report/weekly/1280x800 | 1.207 → 0.519 | 94 → 21 | red |
| report/default/1024x700 | 1.598 → 0.731 | 69 → 21 | red |
| report/weekly/1024x700 | 1.730 → 0.744 | 94 → 21 | red |
| settings/default/1280x800 | 1.660 → 0.864 | 256 → 168 | red |
| settings/default/1024x700 | 2.064 → 1.056 | 256 → 168 | red |
| settings/default/1600x1000 | 1.440 → 0.730 | 256 → 168 | red |

**Board 16/42 → 18/42.** The other 33 rows are byte-identical in pixel % and geometry count. The 26-case campaign
stays 26/26: settings 2.091 → 1.089, no case worse, mean 1.073 → 1.034. Engine headless lib: 2069 passed; 11
GPU-guard timeouts under load, and all 11 pass on a rerun by module (computed_read without r1 22/22, `r1_cases` alone
1/1, consent_click 10/10, computed_pseudo 7/7). Invariants frame_commit 7, render_on_change 1, scroll_paints 4,
load_cancel 11: all ok.

Next on these two pages: report 1280 ×2 sits at 0.517/0.519. The remainder is text AA plus `span.time-format` +0.9 and
the export buttons' height −7. Settings needs select intrinsic width (−22px), checkbox margins, and centred text in
`input[type=number]` (counterfactual 0.818 with geometry clean in the viewport, so raster-bound after that).

## Round 2 (CH2.B31–B34, branch `atlas/z-board-r2` @ `921526e7`, on round 1's `44b69341`)

Full board re-run with `parity-capture` built from the branch. Cells are pixel % / geometry diffs / join failures, then the rule that greens the row.
Base columns: cand38 = batch38 `cb-cand2`, r1 = round 1 `cb-b30`.

| row | cand38 | r1 | r2 |
|---|---|---|---|
| chrome/default/1280x800 | 2.089/159/8 - | 2.089/159/8 - | 2.125/156/0 - |
| chrome/default/1024x700 | 2.711/157/8 - | 2.711/157/8 - | 2.747/154/0 - |
| chrome/default/1600x1000 | 1.497/159/8 - | 1.497/159/8 - | 1.522/156/0 - |
| chrome/hover_tab2/1280x800 | 2.081/159/8 - | 2.081/159/8 - | 2.116/156/0 - |
| chrome/hover_tab2/1024x700 | 2.698/157/8 - | 2.698/157/8 - | 2.735/154/0 - |
| chrome/hover_tab2/1600x1000 | 1.491/159/8 - | 1.491/159/8 - | 1.517/156/0 - |
| chrome/address_focused/1280x800 | 2.312/159/8 - | 2.312/159/8 - | 2.348/156/0 - |
| chrome/address_focused/1024x700 | 2.886/157/8 - | 2.886/157/8 - | 2.923/154/0 - |
| chrome/address_focused/1600x1000 | 1.720/159/8 - | 1.720/159/8 - | 1.745/156/0 - |
| chrome/sidebar_collapsed/1280x800 | 0.313/189/11 pixel | 0.313/189/11 pixel | 0.313/188/3 pixel |
| chrome/sidebar_collapsed/1024x700 | 0.448/177/11 pixel | 0.448/177/11 pixel | 0.448/176/3 pixel |
| chrome/sidebar_collapsed/1600x1000 | 0.201/194/10 pixel | 0.201/194/10 pixel | 0.200/193/2 pixel |
| chrome/find_open/1280x800 | 1.973/178/8 - | 1.973/178/8 - | 2.007/175/0 - |
| chrome/find_open/1024x700 | 2.576/176/8 - | 2.576/176/8 - | 2.611/173/0 - |
| chrome/find_open/1600x1000 | 1.421/178/8 - | 1.421/178/8 - | 1.446/175/0 - |
| chrome/downloads_open/1280x800 | 0.546/177/11 - | 0.546/177/11 - | 0.546/176/3 - |
| chrome/downloads_open/1024x700 | 0.780/165/11 - | 0.780/165/11 - | 0.780/164/3 - |
| chrome/downloads_open/1600x1000 | 0.350/182/10 pixel | 0.350/182/10 pixel | 0.349/181/2 pixel |
| chrome/focus_mode/1280x800 | 0.202/189/13 pixel | 0.202/189/13 pixel | 0.202/188/3 pixel |
| chrome/focus_mode/1024x700 | 0.288/177/13 pixel | 0.288/177/13 pixel | 0.288/176/3 pixel |
| chrome/focus_mode/1600x1000 | 0.129/194/12 pixel | 0.129/194/12 pixel | 0.129/193/2 pixel |
| inspector/default/1280x800 | 3.121/50/28 - | 3.121/50/28 - | 3.121/50/27 - |
| inspector/default/1024x700 | 3.708/50/28 - | 3.708/50/28 - | 3.708/50/27 - |
| inspector/default/1600x1000 | 2.417/50/28 - | 2.417/50/28 - | 2.417/50/27 - |
| inspector/console_tab/1280x800 | 0.346/0/1 pixel | 0.346/0/1 pixel | 0.346/0/0 pixel |
| inspector/console_tab/1024x700 | 0.495/0/1 pixel | 0.495/0/1 pixel | 0.495/0/0 pixel |
| inspector/console_tab/1600x1000 | 0.222/0/1 pixel | 0.222/0/1 pixel | 0.222/0/0 pixel |
| settings/default/1280x800 | 1.660/256/0 - | 0.864/168/0 - | 0.818/128/0 - |
| settings/default/1024x700 | 2.064/256/0 - | 1.056/168/0 - | 0.990/128/0 - |
| settings/default/1600x1000 | 1.440/256/0 - | 0.730/168/0 - | 0.701/128/0 - |
| report/default/1280x800 | 1.120/69/1 - | 0.517/21/1 - | 0.517/13/1 - |
| report/default/1024x700 | 1.598/69/1 - | 0.731/21/1 - | 0.731/13/1 - |
| report/default/1600x1000 | 0.773/69/1 - | 0.337/21/1 pixel | 0.337/13/1 pixel |
| report/weekly/1280x800 | 1.207/94/1 - | 0.519/21/1 - | 0.519/13/1 - |
| report/weekly/1024x700 | 1.730/94/1 - | 0.744/21/1 - | 0.745/13/1 - |
| report/weekly/1600x1000 | 0.829/94/1 - | 0.339/21/1 pixel | 0.339/13/1 pixel |

**Board 18/42 under the pixel rule and under either rule (r1: 18/42, cand38: 16/42). No row flipped this round.**
Six shelf rows are byte-identical and are left out of the table.

What moved:
- **Joins (tooling, B32).** Chrome rows: 8 → 0 join failures, or 10–13 → 2–3 where the collapsed sidebar is involved. Inspector console 1 → 0.
  The remaining joins are real engine differences, not scorer bugs:
  - the inspector's `dom-node-line selected` (RustKit never applies `selected`);
  - empty boxes the engine drops from its tree (`#error-container`, empty `span.unit`);
  - three collapsed-sidebar phantoms (`#shelfContent`, `shelf-item-url`).
  The geometry rule still can't green any red row: every one of them has 13–156 geometry diffs.
- **Settings (B34):** 0.864/1.056/0.730 → 0.818/0.990/0.701, geometry 168 → 128. Changes: select width with the arrow well, checkbox margins.
- **Report (B33):** geometry 21 → 13. Export buttons now match: the emoji line is 39 tall. Pixels are unchanged and the 1280 rows stay 0.517/0.519.
- **Chrome rows got worse, and it's disclosed.** 13 rows are 0.025–0.037 % worse (e.g. 2.089 → 2.125), with 3 fewer geometry diffs.
  The cause is a correct fix: `workspace-expander` (▾ symbol in a padded button) is now Chrome's 23px, not 22px.
  That adds 1px to the sidebar's existing ~+11px downward drift for every box below it. No row changes gate.

Tried and reverted (both moved rows the wrong way):
- **Rounded inline content area.** It fixed `span.time-format`'s rect, but the glyphs sat 1px further from Chrome (report 0.517 → 0.524).
  It also took inspector geometry 50 → 27, so it's worth redoing with the text seat moved too.
- **Menulist +2 inner height.** It's right for `appearance: auto` (#theme 35). It's wrong for chrome's `appearance: none` `#modeSelector` (31).
  RustKit carries no `appearance` (12 chrome rows +0.25 %).

Gates:
- Campaign 26/26, mean 1.034 → 1.032, settings 1.089 → 1.019, none worse.
- rustkit-layout 920 + 4 + 1 ok.
- Python: test_chrome_board 20/20, test_layout_oracle_gate PASS, test_paint_oracle_gate 36 passed.
- Engine headless lib: 2073 passed; 11 failed, all GPU-guard timeouts in computed_read_tests while r1_cases held the GPU under load (round 1 had the same 11); rerun by module: computed_read without r1 22/22, r1_cases alone 1/1.
- Invariants: frame_commit 7, render_on_change 1, scroll_paints 4, load_cancel 11, all ok.

## Round 3 (CH2.B35–B37, branch `atlas/z-board-r3` @ `cc20b1d5`, round 2 `921526e7` merged into develop `8ebc1b79`)

Atlas's decision on round 2 stood: the emoji button line stays, and this round removed the chrome sidebar's pre-existing shift it had compounded.
Full board re-run with `parity-capture` built from the branch; cells are pixel % / geometry diffs / join failures, then the rule that greens the row.
Base columns: cand39 = batch39 `cb-cand2` (develop), r2 = round 2 `cb-r2b`. Rows byte-identical across all three are left out.

| row | cand39 (develop `8ebc1b79`) | r2 | r3 |
|---|---|---|---|
| chrome/default/1280x800 | 2.099/159/8 - | 2.125/156/0 - | 0.770/68/0 - |
| chrome/default/1024x700 | 2.711/157/8 - | 2.747/154/0 - | 1.022/68/0 - |
| chrome/default/1600x1000 | 1.506/159/8 - | 1.522/156/0 - | 0.599/69/0 - |
| chrome/hover_tab2/1280x800 | 2.091/159/8 - | 2.116/156/0 - | 0.757/68/0 - |
| chrome/hover_tab2/1024x700 | 2.698/157/8 - | 2.735/154/0 - | 1.004/68/0 - |
| chrome/hover_tab2/1600x1000 | 1.500/159/8 - | 1.517/156/0 - | 0.591/69/0 - |
| chrome/address_focused/1280x800 | 2.322/159/8 - | 2.348/156/0 - | 0.994/68/0 - |
| chrome/address_focused/1024x700 | 2.886/157/8 - | 2.923/154/0 - | 1.199/68/0 - |
| chrome/address_focused/1600x1000 | 1.729/159/8 - | 1.745/156/0 - | 0.823/69/0 - |
| chrome/sidebar_collapsed/1280x800 | 0.313/189/11 pixel | 0.313/188/3 pixel | 0.284/106/3 pixel |
| chrome/sidebar_collapsed/1024x700 | 0.448/177/11 pixel | 0.448/176/3 pixel | 0.406/106/3 pixel |
| chrome/sidebar_collapsed/1600x1000 | 0.201/194/10 pixel | 0.200/193/2 pixel | 0.182/107/2 pixel |
| chrome/find_open/1280x800 | 1.983/178/8 - | 2.007/175/0 - | 0.668/87/0 - |
| chrome/find_open/1024x700 | 2.576/176/8 - | 2.611/173/0 - | 0.906/87/0 - |
| chrome/find_open/1600x1000 | 1.430/178/8 - | 1.446/175/0 - | 0.536/88/0 - |
| chrome/downloads_open/1280x800 | 0.546/177/11 - | 0.546/176/3 - | 0.469/96/3 pixel **FLIP** |
| chrome/downloads_open/1024x700 | 0.780/165/11 - | 0.780/164/3 - | 0.669/96/3 - |
| chrome/downloads_open/1600x1000 | 0.350/182/10 pixel | 0.349/181/2 pixel | 0.300/97/2 pixel |
| chrome/focus_mode/1280x800 | 0.202/189/13 pixel | 0.202/188/3 pixel | 0.202/104/7 pixel |
| chrome/focus_mode/1024x700 | 0.288/177/13 pixel | 0.288/176/3 pixel | 0.288/106/3 pixel |
| chrome/focus_mode/1600x1000 | 0.129/194/12 pixel | 0.129/193/2 pixel | 0.129/107/2 pixel |
| inspector/default/1280x800 | 3.121/50/28 - | 3.121/50/27 - | 1.254/31/7 - |
| inspector/default/1024x700 | 3.708/50/28 - | 3.708/50/27 - | 1.791/31/7 - |
| inspector/default/1600x1000 | 2.417/50/28 - | 2.417/50/27 - | 0.802/31/7 - |
| inspector/console_tab/1280x800 | 0.346/0/1 pixel | 0.346/0/0 pixel | 0.346/0/0 pixel |
| inspector/console_tab/1024x700 | 0.495/0/1 pixel | 0.495/0/0 pixel | 0.495/0/0 pixel |
| inspector/console_tab/1600x1000 | 0.222/0/1 pixel | 0.222/0/0 pixel | 0.222/0/0 pixel |
| settings/default/1280x800 | 1.660/256/0 - | 0.818/128/0 - | 0.818/128/0 - |
| settings/default/1024x700 | 2.064/256/0 - | 0.990/128/0 - | 0.990/128/0 - |
| settings/default/1600x1000 | 1.440/256/0 - | 0.701/128/0 - | 0.701/128/0 - |
| report/default/1280x800 | 1.120/69/1 - | 0.517/13/1 - | 0.498/7/1 pixel **FLIP** |
| report/default/1024x700 | 1.598/69/1 - | 0.731/13/1 - | 0.704/7/1 - |
| report/default/1600x1000 | 0.773/69/1 - | 0.337/13/1 pixel | 0.326/7/1 pixel |
| report/weekly/1280x800 | 1.207/94/1 - | 0.519/13/1 - | 0.500/7/1 pixel **FLIP** |
| report/weekly/1024x700 | 1.730/94/1 - | 0.745/13/1 - | 0.719/7/1 - |
| report/weekly/1600x1000 | 0.829/94/1 - | 0.339/13/1 pixel | 0.327/7/1 pixel |

**Board 16 → 18 → 21/42, under the pixel rule and under either rule (the geometry rule still greens nothing: every red row keeps 7–96 geometry diffs). Three rows flipped; no row's pixel % got worse than r2 or cand39.**

What moved, by step (the steps were measured as step 1 alone, then steps 1–3 together):
- **Step 1, the sidebar shift (B35).** The first box whose y diverges from Chrome 148 was never below the actions section: `#sidebarShieldStatus` and `#sidebarSettingsBtn` were 39 tall for Chrome's 33 (+6 each), because their `🛡` and `⚙` icons were measured and drawn from Apple Color Emoji where Chrome uses the system font's `.AppleColorEmojiUI` and Menlo (the characters lack Emoji_Presentation). Everything below sat 12 px low (11 from this, 1 from B33's correct expander). Fixing it alone: chrome/default/1280 2.125 → 0.770 with geometry 156 → 68, every chrome row 0.03–1.7 points better, and chrome/downloads_open/1280 flips (0.546 → 0.469). Under the pixel rule that is 1 flip; under the geometry rule 0 (68–107 diffs remain: `#urlInput` height, `#modeSelector`, the collapsed right-sidebar panel widths, `.focus-hint kbd`, shelf items +2).
- **Step 2, the Inspector's `selected` (B36).** Not an event or restyle problem: the row is found with `[data-path="\30 \.1\.1"]` (CSS.escape) and the matcher never resolved escapes in an attribute value. Inspector joins 27 → 7 (the rest are empty `span.unit` boxes the engine drops); the inspector rows fall from 3.121/3.708/2.417 to 1.254/1.791/0.802 (with step 3) but stay red.
- **Step 3, `span.time-format` (B37).** The box rounding and the text seat now move together: the shift for a NEGATIVE half-leading was never applied while the align pass assumed it was, so the line's baseline sat 1 px high; round 2's rounding alone widened that to 2. Report geometry 13 → 7, and the two 1280 rows flip at 0.498 / 0.500. Inspector geometry 50 → 31.
- **One Chrome-arm note.** chrome/focus_mode/1280 shows 7 joins (r2: 3) with an unchanged 0.202 %: the Chromium capture of that one row caught `body.cursor-hidden` after `.focus-hint` had faded (the page's own idle timer); the other two sizes and the step-1 run have the hint visible, and RustKit's tree is identical in both runs. It is the composed page's timing, not the engine.

Gates:
- Campaign 26/26, mean 1.032 → 1.030, none worse than r2 (chrome_rustkit 0.984 → 0.957, css-selectors 1.330 → 1.308 = develop).
- rustkit-text 100 (incl. the presentation pin), rustkit-layout 927 + 4 + 1 filter-free, rustkit-renderer 150, rustkit-css 122; engine attr 33 / selector 51 / escape 11 filters.
- engine headless lib 2081 passed, 11 failed = all GPU test guard waits on `computed_read_tests::r1_cases` (same class as rounds 1-2); by module: r1_cases alone 1/1, computed_read_tests --skip r1_cases 22/22, color_shorthand_keep_tests 2/2, computed_display_tests 6/6; invariants frame_commit 7, render_on_change 1, scroll_paints 4, load_cancel 11, all ok

Next by measured remainder: chrome rows need the form-control heights (`#urlInput` 16 → 18.5, `#modeSelector` with no `appearance`) and the collapsed right-sidebar panel widths before any flips under rule 1 at 1280 (0.77 → ≤ 0.5 needs about a third of the remaining pixels); inspector rows are now 0.80–1.79 and mostly the `dom-toggle` glyph box (5×2.5 vs 2.5×5: a rotated ▶) plus monospace raster; report's 1024 rows (0.704/0.719) are raster-bound after the export-button widths.
