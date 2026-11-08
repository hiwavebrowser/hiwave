<!-- gh pr create -R hiwavebrowser/hiwave-macos --base develop --head atlas/z-ch2-b25b-inline-abspos --draft --title "fix(layout): inline-level abspos static position follows text-align, floats and inline parents (CH2.B25b)" --body-file trench/z/receipts/ch2-b25b/pr-body.md -->
## CH2.B25b: where an abspos box that was inline-level sits on its line

**Before (develop 8ebc1b79):** #983 put an abspos box that was inline-level on the current line, after the content before it. Three faults remained:
1. Its x ignored `text-align`. In a centred 400px block, the box after a 40px inline-block was at x 40 (Chromium: 220). Alone on the line it was at x 0 (Chromium: 200).
2. Its x ignored floats. After a 50px left float plus a 40px inline-block it was at x 40 (Chromium: 90).
3. Inside an `<a>` or `<span>` it widened the inline, so the link was 70px wide instead of 40. It also moved down with the baseline shift: y 6 instead of 0.

**After:**
- The static x starts past the floats that narrow the line (`floats.line_band`).
- `text-align` moves the box with its line. If no recorded line holds it (it is alone, or a block or break follows it), it is aligned as an empty line.
- An out-of-flow child takes no width in `layout_inline`.
- An inline-level abspos box inside a non-atomic inline stays at the top of the line. The half-leading shift (`shift_inline_content_area`) skips it, and the baseline shift in `apply_vertical_align` is undone for it (`keep_inline_oof_at_line_top`).
- The same changes are made in both block-layout loops (the plain one and the margin-collapse one).

**Oracle:** Chrome for Testing 148.0.7778.216. The pages and Chromium's boxes are in `tools/parity_oracle/abspos_inline_line_cases.json` (`grid_flexible_row_log.mjs --file … --write`). The set has 12 pages: centre and right alignment, a box before or after an inline-block, a box alone, left and right floats, a block-level abspos control, and a box inside `<a>`/`<span>`.
- develop: **10 of 12 wrong**
- this branch: **12/12**

**Commits:** red `59cb7c84` (test + case file; 10 of 12 FAIL on develop, log `receipts/ch2-b25b/red-develop.log`), then fix `50641591`.

**Gates (host: macOS seat, toolchain from rust-toolchain.toml, debug test profile)**
- rustkit-layout: 924/0, the same count as develop.
- abspos family (`abspos_static*`, `abspos_inline_line_tests`): all pass. One `flex_abspos_static_position_tests` case hit a GPU-guard 120 s timeout under load ~10, the known shape.
- rustkit-engine headless lib: the full run (2116 tests) could not finish inside the session at load 30–35 (~6 tests/min). It was stopped at 64 tests; its 11 failures were all early GPU-backed tests. Instead, a filtered run of the layout-relevant modules (`abspos inline float text_align vertical_align line_ static_position baseline`) gave 154 tests: 121 pass, plus 33 GPU-guard 120 s timeouts (every one panicking at lib.rs:134) that pass **33/33 rerun alone on one thread** (`rerun33.log`). The remaining ~1960 tests are owed to the batch suite.
- Campaign / chrome board / all-site A/B: 26-case campaign at 50641591 with the parity profile (binary sha256 6f660b7cc2aa1366d2fe768fc70c45f07f7a80a0c67423edc323654f17737cc7): **26/26, mean 1.0721 %**, versus develop 8ebc1b79 at 1.072 % (the figure from the batch-39 gate, not re-run here). Chrome board and all-site A/B were **not run**. The change is layout-only and limited to abspos boxes that were inline-level, so the batch board and A/B are the check.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
