Title: fix(text): system-font weights set the wght axis, as Chrome does (CH2.B6c)
Branch: atlas/z-ch2-b6c-wght-axis @ 7b0d55b3 (red e6b160f5), base develop 232fca86
PR: pending the open-PR cap (16 open at 18:35 ET); open as a draft with this body when a slot frees.

---

## What

`create_system_font_with_weight` built every non-400 system-font weight from a `kCTFontWeightTrait` descriptor. Core Text answers that with the variable font's nearest NAMED instance (Light, Medium, Semibold, Heavy). Chrome instead sets the `wght` axis to the CSS weight. So 300/500/600/800 system text measured differently from Chrome; the largest gap was 1.58 px at weight 800 on a 20-character chrome label (Reduce, 11-05).

Fix: `apply_wght_axis` copies the base UI font's descriptor with `kCTFontVariationAttribute {wght: css_weight}`, clamped to the face's own axis range, and only when the face has a `wght` axis. The trait path remains as the fallback. Italic system text goes through a separate path and is unchanged. Weight 400 is unchanged.

## Red → green (rustkit-text, macOS)

`system_font_weights_between_the_named_faces_measure_like_chrome`: 'Downloads and Tabs 1' at 13px, measured the way layout measures a run (kerned CTLine, ligatures off).

| weight | develop | Chromium 143 | branch |
|---|---|---|---|
| 300 | 132.84 | 133.19 | within 0.05 |
| 500 | 137.42 | 137.17 | within 0.05 |
| 600 | 139.51 | 139.78 | within 0.05 |
| 800 | 146.56 | 144.98 | within 0.05 |

Red at e6b160f5 (300: 132.84 vs 133.19), green at 7b0d55b3.

Two older tests pinned the named-instance PostScript names (`…Bold`, `…Light`). The face is now `.SFNS-Regular_…_wght2BC0000`, so those tests read the face's weight trait instead (700 ≥ 0.3; 300 lighter than 400). Every face is still distinct per CSS weight.

## Tests (targeted; the full suite is the batch's)

- rustkit-text --lib 99/0
- rustkit-layout --lib 896/0 (13 ignored)
- rustkit-engine --lib 709/0 (6 ignored, filter-free)
- rustkit-engine --features headless --lib `font` 37/0, `text` 90/0

## Campaign (26 cases, --profile parity, develop 232fca86 vs branch 7b0d55b3)

26/26 pass on both arms. 7 cases moved:
- toward Chrome: about 3.703 → 3.330 % (a weight-300 tagline), sticky-scroll 0.658 → 0.632, new_tab 1.075 → 1.051, form-elements 0.954 → 0.944, shelf 0.727 → 0.721, settings 2.092 → 2.091
- away: chrome_rustkit 1.069 → 1.076 (+0.007 pp, stable over 3 runs). The page has two `font-weight: 600` labels (`.workspace-name` 13px, `.sidebar-title` 11px). The wght-600 face is slightly heavier than the Semibold instance (≈590). The baseline PNG is chrome-148, while the width pins above are Chromium 143's.

## Chrome board (scripts/chrome_board.py, 42 rows)

develop and branch are both 10/42 green. Geometry diffs 5470 → 5470. Mean pixel diff 1.418 → 1.418 %. Every row moves by ≤ 0.002 %. This is expected: the advance changes are sub-pixel and fall under the board's 0.5 px geometry join.

## Receipt (`scripts/receipt.py`)

base 232fca86b130cc3541de3bf4f8ba0648e65581e3, candidate 7b0d55b33db2c4fcb0f8967ff9fb9380b597ec10, binary sha256 ffde943cb853332ce2746a95072476a01e78420f5211ad1849a77a9f8214a9ea (develop arm 51370e2436714f17ed046b595a5a76c46655542c3d50cfd5bf7c5df82ade0253), profile parity, rustc 1.91.0 (f8297e351 2025-10-28), aarch64-apple-darwin, macOS 26.5.2 arm64, sccache, clean tree, Cargo.lock 36360f8f. Raw runs: board.json develop f80caf83…, branch 83620825…. Not run: all-site A/B (this is a font change, not paint/fetch/script; the batch runs it).

Needs R1 (Prometheus), then a batch.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
