fix(layout): center and flex-end place an overflowing flex line unsafely, as Chrome does (CH2.B19)
Branch: atlas/z-ch2-b19-justify-unsafe @ 3e1af58c (red 1e3c0881, fix 6a041846, pins 3e1af58c), base develop 5b38cc5c (develop 70cd68c5 differs only by #933/#934, scratch/ + .gitignore)

---

## What

`distribute_main_axis` clamped the free space at 0 before `justify-content` read it, so a line that overflows its flex container always started at the main-start edge. Chromium 143 (Box Alignment §4.4, the `justify-content` default with no `safe`/`unsafe`) places an overflowing line unsafely for `center` and `flex-end`: a 300 px item centred in a 100 px row starts at −100 and overflows both sides equally. `space-between`, `space-around` and `space-evenly` fall back to the start, as in Chromium.

The fix keeps the signed free space. `center` and `flex-end` (and `end`) place it. Auto margins still take only positive free space (§9.5.12): on an overflowing line they are 0 and `justify-content` applies. The space-* values keep the clamp. Sibling of CH2.B9(3) (`align-items: center` overflow on the cross axis, #922).

Pre-existing and not changed: `justify-content: safe center` and `unsafe center` both parse to `flex-start` (the keyword match in `apply_style_property` has no `safe`/`unsafe` arm). That is right for `safe center` on an overflowing line and wrong in every other case. Follow-up row candidate.

## Red → green (rustkit-engine, headless, Chromium 143 pins)

`flex_justify_overflow_tests` runs 16 pages from `tools/parity_oracle/flex_justify_overflow_cases.json` (`grid_flexible_row_log.mjs --file … --write`, `id:x:y:w:h`):
- center, flex-end, end, flex-start, space-between, space-around and space-evenly with one 300 px item in a 100 px row
- center, flex-end and space-around with two overflowing items
- `flex-direction: column` center and flex-end
- `row-reverse` center
- an auto-margin item in an overflowing centred row (Chromium: starts at −100). Added at 3e1af58c.
- `safe center` (Chromium: start). Added at 3e1af58c.
- a fitting centred item (control)

The 14 original pages: 8 wrong at 1e3c0881, 0 at 6a041846. The two pins added at 3e1af58c pass on the branch. They were not run on develop. By the code, the auto-margin page is red there (develop clamps, so x = 200 against Chromium's 100) and `safe center` is green.

## Tests (targeted; the full suite is the batch's)

- `flex_justify_overflow` 1/0 (16 pages) at 3e1af58c
- rustkit-layout --lib 896/0, headless `flex` 91/0 at `--test-threads=4` (previous session, at 6a041846; the default-thread run at load ~15 had 10 unrelated timeouts that pass alone)

## Campaign / board (--profile parity; develop 70cd68c5 sha256 47241851bff16e5b…, branch 6a041846 sha256 c13c7db1c9b987f6…; 3e1af58c is test-data only)

- 26-case campaign: 26/26 on both arms, 0 cases moved.
- Chrome board: 42 rows. In the first pass 3 rows differed, all `chrome/focus_mode`: geometry 189/177/194 → 187/175/192 at the three sizes, and pixels 0.285 → 0.449 % at 1024 and 0.128 → 0.201 % at 1600. Two more `--only chrome` runs per arm show that **develop flips between the same two states**: run 0 gave develop 187/175/192 with 0.449 %, and run 1 gave both arms 189/177/194 with 0.285 %. That is the known focus_mode cursor-timer artifact. No move is attributable to this PR. The one box that differed is a span in a collapsed-sidebar button: x 21.0 on develop, 15.94 on the branch, −14.4 in Chrome.

Not run: the all-site A/B (layout change; that is the batch's job).

Toolchain rustc 1.91.0, aarch64-apple-darwin, macOS arm64, z-cargo lease + sccache. Oracle: Chromium 143.0.7499.4 (Playwright, DPR 1).

Needs R1 (Prometheus), then a batch.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
