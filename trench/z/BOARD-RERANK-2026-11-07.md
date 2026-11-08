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
