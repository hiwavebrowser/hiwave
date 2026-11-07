# CH2.B17b: min/max sizes on text inputs and textareas (branch `atlas/z-ch2-b17b-control-min-max`)

- Base: develop 5b4371ec. Red: 5360348e. Fix: 6f3255fc.
- No PR: 9 hiwave-macos PRs are open against the cap of 8.

## Before → after
- **Before:** `layout_form_control` resolved width and height but never read `min-*`/`max-*`.
  - `min-width:60px` on a `width:20px` input built 28 (Chromium 68).
  - `max-width:40px` on a 100px input built 108 (Chromium 48).
  - The flex-row path already clamped.
- **After:** the clamp is max first, then min. A content-box text control adds its padding and border, as for width/height (CH2.B17). A percentage height against an indefinite base does not apply.

## Pins
- `form_control_min_max_tests.rs` + `tools/parity_oracle/form_control_min_max_cases.json`: 11 Chromium 143 pages covering input and textarea, content-box and border-box, min/max on both axes, `%` max, and a flex row.
- 9/11 red on develop, 11/11 green.

## Gates at 6f3255fc
- rustkit-layout: 906/0.
- Headless engine `input|control|textarea|form` filter: 221/0.
- Campaign: 26/26, 0 cases moved (diff pixels identical to the b9fa9836 table banked in ch2-e20; batch 33 left the campaign unmoved).
- Chrome board: 16/42 green on both arms, 42/42 rows identical (develop 5b4371ec vs candidate).
- All-site A/B (ab5.py, develop 5b4371ec vs 6f3255fc):
  - **One mover, wikipedia: 0.17% on all four cross pairs, 0 within.** The search input grows from ~26 to the 32 px of the Search button beside it (`wikipedia-*.png`). This is the page's own min-height now applying, toward Chrome by inspection. No Chromium probe of the page was run.
  - google and github vary inside arm A. cnn hits the capture limit 4/4 in both arms.
- Parity binaries sha256: candidate 64843720905ded4768c3e4d25f03e22c335bdc6985c1a31466dcf03b4d20c87e, base 773d66740c22c590c1d3797fd635804ae0aba5a6538c2645849e95b0c8a977bf.
- Headless suite at 6f3255fc (07:20 11-07): all 2084 run; 2040 ok, 33 ignored, 11 FAILED at default threads (GPU-guard waits), 11/11 pass on one thread. Logs: suite-6f32.log, suite-6f32-rest9.log, rerun1t-6f32.log.
- **OWED:** only the PR, once fewer than 8 are open. Body: `pr-body.md` (complete).
