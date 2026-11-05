fix(layout): a float's percentage height resolves against its containing block, not the viewport (CH2.B16)

## What was wrong

Reduce's case was a float with `height: 50%` in a 200px parent that has only float children. RustKit gave 300 at a 600px viewport; Chromium gives 100. The row guessed the cause was the float-only parent. It isn't: **every float's percentage height resolved against the viewport**, with or without in-flow siblings, left or right, and nested in a percentage chain.

`layout_float` (rustkit-layout lib.rs) ran after the box's normal layout and redid `calculate_block_height`. It used `containing_block.content.height` as the percent base, but on this path that value is the parent's flow cursor, not a height. For the first float of a box the cursor is 0, so the base was `None` and the height took the viewport fallback. That overwrote the right base the caller had already passed (`percent_height_base`).

## Fix

`layout_float` takes the dispatcher's `percent_height_base` and uses it for the children's definite height and for `calculate_block_height`, exactly as the block path does (lib.rs ~4269 / ~4341). The flow cursor stays the fallback, unchanged, when there is no base.

## Commits
- c8e6b901 test (red): `float_percent_height_tests`, 8 pages at 400x600 from `tools/parity_oracle/float_percent_height_cases.json` (Chromium 143.0.7499.4). develop fails 7.
- 873020ec fix. 5 of the 7 now match Chromium. The other two are wrong for **every** box, not only floats, so they are tagged `known` in the case file. The test fails the day either of them flips.
  - `min-height: 25%` resolves against the viewport: the `calculate_block_height` min-height arm uses `self.viewport.1`, and the comment there admits the inconsistency. 150 vs 50.
  - A parent with `height:200px; max-height:150px` hands its children 200 (the specified height) as the base, not the clamped 150. 200 vs 150.

## Receipt
- base develop 232fca86, candidate 873020ec
- binaries (`--profile parity`): develop sha256 82fdc07e…5c, branch sha256 f35e08d1…065c
- rustc 1.91.0; macOS 26.5.2 arm64; oracle Chromium 143.0.7499.4 (Playwright pin)
- `float_percent_height_tests`: develop 1/8, branch 6/8 + 2 known (the test fails if either known case flips)
- rustkit-layout 896/0 (13 ignored)
- rustkit-engine `--lib` filters: float 20/0, clear 16/0, percent 42/0
- 26-case campaign: 26/26 on both arms, average 1.1%, 0 cases moved
- chrome board: 42/42 rows identical. The first branch run moved chrome/focus_mode/1280x800 (0.432 → 0.546%, geometry 211 → 209), but that frame carried `body.cursor-hidden`, which focus mode adds on an idle timer, so it was a capture-timing artifact at load 16. A rerun of the chrome page gave 0.432% / 211, the same as develop.
- Not run: full engine suite and the all-site A/B; those are the batch's. Pages that may move: floats with percentage heights in a definite-height parent (cards, sidebars, float grids).

## Follow-up rows (not in this PR)
- min-height % against the containing block on every box. Expect many live-site movers: `min-height:100%` under an auto-height body is 0 in Chromium and the viewport in RustKit. That needs its own all-site A/B.
- The percent base should be the max/min-clamped used height.

R1 asked of Prometheus.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
