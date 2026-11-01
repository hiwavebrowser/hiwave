#!/usr/bin/env python3
"""digest1505.py: this slot's digest section and plan note, written once."""
H = "/Users/petecopeland/Repos/.worktrees/z-hub/trench/z/"
TEXT = """
## 2026-11-01 17:06 Z-lane C10 #855 z part, #851 held rule and gates, #853 gates

**(1) #855 LANDED by Atlas -> develop `525f6ec0`.** Before: the z part of `translate` took `%`, `auto`, `fit-content`. After: refused, as in Chromium 143, also inside `calc`/`min`/`max`/`clamp`, and a bare non-zero number too (my test caught that one). Red `a6d71353`, fix `b5cc8df8`. Headless 1393/0, app debug build rc=0, campaign 26/26 0 moved. A/B not rerun at this head.

**(2) #851 @ `68f4cf7b` (draft, merges develop `525f6ec0`).** `held` now keys on a containing block for fixed boxes: transform, filter, `will-change`, `contain`. Red `b3baf512` (3 of 75 failing), fix `bbf114fe`, 75/0 after. One change beyond the order: such a box inside a scroller now carries its fixed and absolute children with the scroller (Chromium `held2_probe.mjs`).
- **The shopify hold is cleared in a capture:** the header paints and the two black columns are gone. Frames at this seat, `renders-private/2026-11-01-851-shopify/`, not committed.
- Campaign 26/26, 0 moved against `525f6ec0`. Layout 881/0, bindings 428/0, engine lib 618/0, app debug build rc=0. Headless suite: see the line below.
- 20-site A/B: shopify is the one mover, the header, 0.81% to 2.83% across on every pair in two runs (its hero video also varies within an arm). linkedin and bing vary inside one arm, and move between arms from run to run. cnn at the 90 s limit 0.03% at most. lyft refused one capture, in the second slot.

**(3) #853 @ `b27f19fa` (draft, merges develop `525f6ec0`).** Gates posted, measured at `b6e3089b` (one merge earlier): headless 1411/0, layout 881/0, bindings 428/0, engine lib 618/0, app debug build rc=0, campaign 26/26 0 moved, A/B no mover. At `b27f19fa` only the tests named `transform` (79/0) and the census guard. **Atlas: send it to re-review.**

**Not done:**
- No real window on #851 or #853; the lane has no input grant. Atlas's dropdown page needs a rerun on #851's build, since the panel did not paint on #855's.
- `perspective`, `backdrop-filter`, `transform-style`, `content-visibility` still do not set `held`, though Chromium holds for all four. Not in the order.
- Where layout places a fixed box under its containing block is still row C10 (m): this slot changes rects and scrolling only.
- #855 findings 2, 4, 5 and Atlas's C10 (3) items not touched. A bare number as x or y in `translate` not checked. A `calc()` with a percentage still passes `depth()` for `translate3d` on #853.
- No standing develop check on its own; the base campaign at `92342645` and `525f6ec0` is the only develop evidence. Aleph tools were not available in this session, so the reading was by grep.

**Slip:** I wrote a new `tools/c2/ppm2png.py` over the existing tracked one; restored from git before any commit.

**Receipts (hub):** `2026-11-01-{tcalc2,c10b2g,c2dg}-*`, `2026-11-01-campaign-{tcalc2-b5cc8df8,c10b2g-b6e3089b,c2dg-68f4cf7b}.json`. Probes: `tools/c10/translate_z_probe.mjs`, `tools/c2/held2_probe.mjs`. Worktrees z-c10-tcalc2, z-c10b2-g, z-base-92342645 removed. The comparison Chrome is the oracle's 143.0.7499.4. Open hiwave-macos PRs: #847, #851, #853 (3 of 8).
"""
open(H + "digest-z.md", "a").write(TEXT)
p = open(H + "PLAN-z.md").read()
mark = "> **11-01 11:02 ET (Z lane): #855 is draft"
note = "> **11-01 17:06 ET (Z lane): 12:35 order done apart from what is yours. #855 landed. #851 @ `68f4cf7b` and #853 @ `b27f19fa` have their gates on the PR (see each comment for what ran at which head). Atlas: both are draft; flip and send to R1, #851 first. #851 needs your real-window run (the dropdown page from #855). Next slot: the first open row in table order after C10's remaining items are placed; C15 and C16 wait behind them.** Open hiwave-macos PRs: #847, #851, #853 (3 of 8).\n\n"
assert mark in p
open(H + "PLAN-z.md", "w").write(p.replace(mark, note + mark, 1))
