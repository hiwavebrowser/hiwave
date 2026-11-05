fix(layout): fixed form controls size against the viewport; vh/rem/calc control sizes (CH2.B13)

PR body, ready to open. Branch `atlas/z-ch2-b13-control-pct-height` @ 11709995, base develop c959570f. Held, not opened: 16 hiwave-macos PRs were open at 13:36 ET (cap 16).

## What was wrong

The E12 agent found this (a fixed `<input>` with `height:50%`: Chromium 348, RustKit 34.2) and Reduce narrowed it to form controls and replaced elements. `layout_form_control` (rustkit-layout lib.rs) read only px, % and em, and it resolved % against the box that laid the control out.

**(A) The containing block of a `position:fixed` control is the viewport** (CSS 2.1 §10.1). Measured at 400x600:
- `height: 50%` resolved against the parent's flow cursor, which is 0, so it fell back to the intrinsic size. input/textarea/button/select came out 19/32/19/19. Chromium: 300 for all four.
- `width: 50%` took half of its 100px parent: 50. Chromium: 200, half the viewport.
- Now % width, % height and margins use the viewport whenever one is set.

**(B) `vh`, `vw`, `rem`, `calc()` and the other length kinds fell through to the intrinsic size in any position.**
- `height: 50vh`: 19 (Chromium 300).
- `height: 2rem`: 19 (Chromium 32).
- `width: calc(25vw + 10px)`: 31 (Chromium 110).
- These now go through `length_to_px`, against the same base a percentage uses.

The two arms that differ from Chromium for other reasons are held fixed in every pin, so each case tests one axis:
- Intrinsic control size (control font metrics): the axis not under test gets an explicit size.
- Text input/textarea author sizes: RustKit applies them as border-box, Chromium's UA sheet as content-box (CH2.B17). Those pages carry `box-sizing: border-box`.

## Commits
- 3d630d84 test (red): `control_percent_height_tests` with 11 pages from `tools/parity_oracle/control_percent_height_cases.json`. develop fails 8, every one on the axis under test. 3 controls pass: a px-only calc height, % of a definite parent, and an abspos % height (already right).
- 11709995 fix: one function, `layout_form_control`.

## Receipt
- base c959570f, candidate 11709995
- binaries (`--profile parity`): develop sha256 c802c334…afda, branch sha256 99ee3872…f297
- rustc 1.91.0 (f8297e351 2025-10-28); macOS 26.5.2 arm64; Petes-MacBook-Pro
- oracle: Chromium 143.0.7499.4 (Playwright pin); case file sha256 99e7759e…acb
- `control_percent_height_tests`: develop 3/11, branch 11/11
- rustkit-layout: 896/0 (13 ignored)
- rustkit-engine `--lib` filtered to control|input|button|select|textarea|form: 275/0 (3 ignored)
- 26-case campaign: 26/26 on both arms, average 1.1%, 0 cases moved (form-controls and form-elements included)
- chrome board: 42/42 rows identical
- Not run: the all-site A/B (live-site freeze; the batch's). Pages that may move: fixed or overlay inputs with %/vh heights, and controls sized in rem/calc/vw.

## Not done
- Fixed or abspos `<img>` with a % height (Reduce: 40 vs 300). `reanchor_absolute` re-runs image sizing for `absolute` only. It is not pinned here, because the headless harness needs a decoded natural size.
- CH2.B17 (input/textarea author size as border-box) and CH2.B15 (abspos containing block = DOM parent) are separate rows.

R1 asked of Prometheus.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
