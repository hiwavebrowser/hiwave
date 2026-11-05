fix(css): a bare 0 parses to Px(0.0); Length::Zero is only the unset default (CH2.B14)

## What was wrong

`rustkit_css::parse_length("0")` returned `Length::Zero`. That variant is also `#[default]`, the value an unset property holds. So any code that tells "not set" from "set to zero" by the variant read an author's bare `0` as unset, while `0px` (which parses to `Px(0.0)`) was right. Chromium gives `0` and `0px` the same result everywhere (css-values-4 §6.1.1).

#913 fixed width/height/min-*/max-* by storing their zero as `Px(0)` at the property. This row is the audit of every other property that takes a length.

## The audit

`tools/parity_oracle/unitless_zero_cases.json` has 36 property pages. Each is written twice, once with `0` and once with `0px`. Chromium 143.0.7499.4 gives identical boxes for all 36 pairs. Properties covered: margin (p, body, h1, `0 auto`), padding (ul, fieldset, button, td), border widths (div, input), insets (abs, fixed `inset`, relative, sticky), gap/column-gap/row-gap (flex, grid, multicol), flex-basis, `flex: 1 1 0`, line-height, text-indent, letter-spacing, word-spacing, border-spacing, outline-offset, a `0` grid track, min-width on a flex item, vertical-align, translate.

On develop c959570f, **only one pair differs between `0` and `0px`**:
- multicol `column-gap: 0` was read as `normal`, which is 1em (columns 95/105 vs Chromium 100/100). `multicol.rs` tells unset from authored by the `Zero` variant.

getComputedStyle has the same fault:
- `gap: 0` read back as `"0 normal 0"` (flex column-gap, row-gap, multicol column-gap). Chromium gives `"0px 0px 0px"`. `computed_read` treats `Zero` as `normal`.

The other suspect sites the row named (rustkit-layout lib.rs ~1666/5230/5527/6520) already treat `Zero` and `Px(0)` alike, or they only see width/max-width, which #913 covers. They are not misreads.

## Fix

`0` now parses to `Px(0.0)`, the same path `0px` takes, so the two cannot differ by construction. `Length::Zero` keeps one meaning: the unset default. That is already how the calc path treats it (`calc(10px - 10px)` → `Px(0.0)`, with a test saying why). The grid track parser matched `Zero` and `Rem` only after its own `px` suffix check, so it gains a `Px` arm. Three css tests that pinned the old representation (`outline` width/offset, `border-spacing`) move to `Px(0.0)`.

An authored `0` now lists in `computed_read::rows` where `0px` already did (word-spacing, radii, gaps). That makes the two the same.

## Commits
- 42f73337 test (red): `unitless_zero_tests`. Layout: 72 pages; each must match Chromium, and `0` must equal its `0px` twin. Six pairs that are wrong for `0px` as well are tagged `known`, with the separate defect named; they still must give `0` == `0px`. Computed: the gap read. develop: 0/2.
- 9d3a9398 fix.
- 47ce0e88 test: `computed_read_cases.json` had `gap: 0` marked as a known gap ('zero is the unset value: reads normal'). It now reads `0px`, so the mark is dropped.
- 180c56ed test: two more pins of an authored `0` move to `Px(0.0)`: td `padding:0` over `cellpadding`, and `translate: 10px 0`.

## Receipt
- base c959570f, candidate 180c56ed (merges clean with develop c986d89c)
- rustc 1.91.0; macOS 26.5.2 arm64; oracle Chromium 143.0.7499.4 (Playwright pin)
- `unitless_zero_tests`: develop 0/2, branch 2/2
- rustkit-css 119/0; rustkit-layout 896/0 (13 ignored)
- rustkit-engine `--lib` filters: column 22/0, gap 4/0, flex 81/0, computed 46/0 (13 hit timeouts at load ~9 in the parallel run; all passed when rerun single-threaded), outline 32/0, spacing 2/0, track 10/0, table 23/0, translate 15/0, transform 98/0, animation 45/0, zero_font 3/0
- 26-case campaign: 26/26 on both arms, average 1.1%, 0 cases moved (`--profile parity`; develop sha256 3ed8336c…1044, branch sha256 292f33f8…fd10)
- chrome board: 42/42 rows identical (pixel and geometry), 6/42 green on both arms (base c959570f, before batch 23)
- Not run: full engine suite and the all-site A/B; those are the batch's. Pages that may move: multicol with `column-gap:0`, and anything that reads a computed `0` gap.

## Found, not fixed (wrong for `0px` too; each is a row candidate)
1. With `border-style: solid`, an unset side width is 0 instead of `medium` (3px). Box 50x10 vs Chromium 56x13. Unset border widths read `Zero` as 0, the reverse of this row.
2. `line-height: 0` leaves a 5 px line box (Chromium 0).
3. `<button>` author `padding: 0` does not override the UA padding (32x23 vs 8x20).
4. A flex item with `min-width: 0; overflow: hidden` keeps half the row (50/50 vs Chromium 86/14). This was measured on c959570f, before #913 landed; re-check on develop.
5. `h1 { margin: 0 }` under `font: 16px/20px` is 21 tall (Chromium 20).
6. An `<input>` with `border: 0` sits 1 px high on its line.

R1 asked of Prometheus.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
