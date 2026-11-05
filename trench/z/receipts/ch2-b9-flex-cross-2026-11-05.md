fix(layout): nested flex container cross size + unsafe center/end overflow (CH2.B9 items 2 and 3)

PR body, ready to open. Branch `atlas/z-ch2-b9-flex-cross` @ 992fd3bd, base develop a0395604. Held, not opened: 16 hiwave-macos PRs were open at 12:58 ET (cap 16).

## What was wrong

Reduce's chrome tab-bar page (renders-private reduce/ch2-b9) has the close button 3 px low on develop. Chromium 143 puts the tab at 68x29, y 8, and the button at (53,15). RustKit put the tab at 31 tall, y 10, and the button at y 18. Two flex bugs cause this. Item (1) of the row, `gap` applied to a `display:none` item, is #916's fix and is not repeated here.

**(2) A flex or grid container that is a flex item got a one-line minimum cross size.** `get_intrinsic_cross_size` (rustkit-layout flex.rs) floors every item that has children at `resolve_line_height`, which is 18.4 px at 16px Arial, and that value becomes the item's `min_cross_size`. A flex or grid container has no line box, so it has no strut to set a floor. Its height comes from its items.
- Tab: a flex row holding a 12px title and a 16px button came out 30 tall. Chromium: 28.
- A flex item holding one 6px child came out 18. Chromium: 6.

**(3) `align_cross_axis` clamped negative free space to 0.** That made `center` and `flex-end` "safe": an item taller than its line stayed at the start. CSS Box Alignment 3 §4.4 makes both unsafe unless `safe` is written.
- A 40px item centred in a 20px row: Chromium -10, RustKit 0.
- `flex-end` in the same row: Chromium -20, RustKit 0.
- The same happens across a column: a 300px item centred in a 100px column, Chromium x -100.

The abspos static-position path already let free space go negative. `safe` is still not parsed: `safe center` falls back to `stretch`, and a control case pins that this gives Chromium's answer on that page.

## Commits
- 9c1d16c1 test (red): `flex_cross_size_tests` with 11 pages from `tools/parity_oracle/flex_cross_size_cases.json` (Chromium 143.0.7499.4, `grid_flexible_row_log.mjs --write`). Red on develop in 8 of 11; the 3 controls pass.
- d7349541 fix: two hunks in `crates/rustkit-layout/src/flex.rs`.
- 992fd3bd test: Reduce's tab-bar page added as a 12th case. It is red on develop: I ran it against develop's flex.rs and got `t:12:10:68:31 ... x:53:18` vs Chromium `t:12:8:68:29 ... x:53:15`. It is green at the head.

## Receipt
- base a0395604, candidate 992fd3bd (engine code is the same as d7349541)
- binaries (`--profile parity`): develop sha256 75ab452c…e4ce, branch sha256 85815661…863e
- rustc 1.91.0 (f8297e351 2025-10-28); macOS 26.5.2 arm64; Petes-MacBook-Pro; load 7–13 during the runs
- oracle: Chromium 143.0.7499.4 (Playwright pin); case file sha256 1aefd05b…27f7
- `flex_cross_size_tests`: develop 3/11 cases match, branch 12/12
- rustkit-layout: 896 passed / 0 failed / 13 ignored, the same as develop (#913's count)
- rustkit-engine `--lib flex`: 82/0 (5 ignored). `nested`: 17/0. `grid`: 59/0. That last figure covers two runs: the first run had 11 GPU-guard timeouts queued behind `aspect_ratio_in_flex_and_grid_matches_chromium` at load 13, and all 11 passed when rerun alone.
- 26-case campaign: 26/26 on both arms, average 1.1%. One case moved: chrome_rustkit, 1368 → 1250 diff pixels (better).
- chrome board (`scripts/chrome_board.py`, 42 rows): green rows 6 → 8. All 21 `chrome` rows improve, each with 22 fewer geometry diffs (e.g. default/1280x800 3.118 → 2.946 %, 205 → 183). focus_mode at 1280 and 1600 is now under 0.5 %. inspector, report, settings and shelf rows are byte-identical. None is worse.
- Not run: the all-site A/B. Live-site work is frozen (11-04 22:20), and the batch A/B is Atlas's. Pages most likely to move are ones with an `align-items:center` item taller than its row (it now overflows upward, as in Chromium) and flex/grid items whose content is shorter than one line.

## Not done
- `safe` / `unsafe` keywords for align-items/align-self (safe center → stretch today).
- The original row premise (× click reaching the activate handler) still needs re-testing in the real window once #916 and this branch are both on develop.
- `justify-content: center` overflow (main axis) is clamped by `distribute_main_axis` (`free_space.max(0.0)`, flex.rs ~2789). Chromium overflows both sides there too. It is not pinned and not in this row.

R1 asked of Prometheus.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
