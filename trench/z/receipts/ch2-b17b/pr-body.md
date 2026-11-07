## CH2.B17b: `min-*`/`max-*` sizes clamp text inputs and textareas

Row CH2.B17b in `trench/z/PLAN-z.md` (hub `atlas/z`). Base develop 5b4371ec. Red: 5360348e. Fix: 6f3255fc.

### Before → after
- **Before:** `layout_form_control` resolved `width` and `height` but never read `min-width`, `max-width`, `min-height` or `max-height`. A `width:20px; min-width:60px` text input built 28 wide (Chromium 68). A 100px input with `max-width:40px` built 108 (Chromium 48). The flex-row path already clamped.
- **After:** the control's size is clamped max first, then min. A content-box text control adds its padding and border, as for `width`/`height` (CH2.B17). A percentage height against an indefinite base does not apply.

### Pins
- `crates/rustkit-engine/src/form_control_min_max_tests.rs` + `tools/parity_oracle/form_control_min_max_cases.json`: 11 Chromium 143 pages: input and textarea, content-box and border-box, min/max on both axes, a `%` max, and a flex row.
- 9/11 red on develop (the two flex-row cases already clamp), 11/11 green.

### Receipt (hand-written fields; receipt.py is Prometheus's step)
- base 5b4371ec / candidate 6f3255fc
- toolchain: rust-toolchain.toml; host: macOS seat (Darwin 25.5.0)
- parity binaries (`--profile parity`), sha256: candidate 64843720905ded4768c3e4d25f03e22c335bdc6985c1a31466dcf03b4d20c87e, base 773d66740c22c590c1d3797fd635804ae0aba5a6538c2645849e95b0c8a977bf
- Campaign at 6f3255fc: 26/26 pass, 0 cases moved.
- Chrome board: 16/42 green on both arms, all 42 rows identical.
- All-site A/B (`tools/ab5.py`, 5b4371ec vs 6f3255fc, 20 sites): **one mover, wikipedia: 0.17% on all four cross pairs, 0 within.** The search input grows from about 26 px to the 32 px of the Search button beside it, because the page's own `min-height` now applies. That is toward Chrome by inspection; no Chromium probe of the page was run. google and github vary inside arm A. cnn hits the capture limit 4/4 in both arms.
- Crate suites: rustkit-layout 906/0; headless engine `input|control|textarea|form` filter 221/0.
- **Headless engine suite (`rustkit-engine --lib --features headless`) at 6f3255fc: complete, all 2084 tests, 0 failures left.**
  - Exact-name 200-test chunks at default threads (load 2-22; the run was cut at its time limit inside chunk 9, and chunks 9-10 were rerun by name): 2040 ok, 11 FAILED, 33 ignored.
  - The 11 are the consent_click / console_log / container_query / computed_read group, GPU-guard waits ('waited 120s for ...'), the same group E20's suite showed.
  - **All 11 pass on one thread** (`rerun1t-6f32.log`, 11/11 in 23 s).

Receipts: hub `trench/z/receipts/ch2-b17b/`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
