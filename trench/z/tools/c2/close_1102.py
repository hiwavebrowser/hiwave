#!/usr/bin/env python3
"""Session close 11-01 09:05: digest section, plan note, row states."""
import subprocess

H = "/Users/petecopeland/Repos/.worktrees/z-hub/trench/z/"
digest = """
## 2026-11-01 11:02 Z-lane C2 (d) rework, C10 fixed rects, translate, (b2) rework

**(1) #854 LANDED by Atlas -> develop `cae49416`** (R1 CLEAR WITH NITS). Before: a fixed box read the window's scroll (centred modal `300 -490`, Chromium `300 10`). After: fixed boxes and everything under them read as Chromium 143 at any scroll. This was not a #852 regression as the order said: a plain fixed box was wrong too (`7 -491`, Chromium `7 9`).

**(2) #851 CANNOT LAND YET. My 10-31 receipt was wrong.** I called its shopify row page variance. It is real: the sticky header now paints, which is right, but two opaque black columns cover the hero. Cause: `translate: 0px calc(-100% - 1px)` was dropped by the parser, so dropdown panels stayed in place. Hold posted on #851 and in the plan.

**(3) #855 (draft) @ `6e32672f`**, the fix for that (`atlas/z-c10-translate-calc`, red `7ab360e1`, 3 of 4 failing). On a merge with #851, one shopify frame shows the columns gone and the header painted.
- Layout 881/0, bindings 428/0 at `b6ec465d`; engine lib 618/0 at head; `transform_rect_tests` 31/0. Campaign 26/26, 0 moved. 20-site A/B: no row where the arms agree within and differ across; not repeated; cnn hit the 30 s limit on all four.
- **Headless engine suite and `hiwave-app` build NOT run: the cap.**
- The suite did catch one thing: an old test pinned the refusal of a depth in `translate`. Re-pinned to Chromium, say so in review.
- My conflict resolver also cut a test open on the merge with develop; pushed broken for about 10 minutes, fixed at `b6ec465d`.

**(4) #851 @ `d6f2eb54`: R1 rework done, gates NOT finished.** Merges develop `cae49416` and #855's branch. Red first: sticky under transforms (a mutation reproduces the R1's wrong numbers), finding 5 (fixed cuts off sticky above), finding 4 (a stuck box over a fixed bar wins the hit test), Atlas's `held` under a filter.
- `transform_rect_tests` + `sticky_scroll_tests` 70/0 at `42fc0c49`. Campaign 26/26, 0 moved. A/B on 5 sites only (shopify, netflix, yahoo, apple, github): shopify 2.83% is the header; github and netflix differ inside one arm.
- **No full suites at any rework head**, and only 5 of 20 sites at `42fc0c49`.
- The `held` rule covers transform and filter. `will-change`, `contain`, `perspective`, `backdrop-filter`, `transform-style`, `content-visibility: auto` also hold a fixed box in Chromium (`held_probe.mjs`) and are not parsed here. `scale:1` holds too and is identity here.

**(5) #853 @ `179d39ea`: R1 items done, gates NOT run.** Red `8fe8cc07`, 8 of 11 failing. Negative `perspective()`, `calc`/`min`/`max`/`clamp` in angles and numbers, upper-case units and keywords, `initial`, `unset`, `revert`, `inherit`, `inf`, `NaN`, `5.`. `transform` filter 67/0; census guard passes. No campaign, A/B or full suite. `calc(infinity)` is not modelled. R1 said `perspective(10)` was accepted; I found it already refused, and it is pinned.

**Not done:** the standing develop check was not run on its own; #854's suites at `2095df23` (develop `e5e0fd97` + fix: headless 1388/0, layout 881/0, bindings 428/0, engine lib 618/0, app build rc=0) are the nearest evidence, and nothing checked `cae49416`. Atlas's C10 (3) items not touched: fixed inside fixed placed wrong; `getClientRects` of an inline holding a child.

**Next slot, in this order:** (a) #855: headless suite and app build, from a fresh checkout. (b) #851: merge whatever landed, full suites, full A/B. (c) #853: merge develop, campaign, A/B, suites.

**For Atlas:** flip #855 ready and ask R1 only with the suite gap in mind; do not flip #851 or #853. Real-window: Tailwind v4 dropdown on hover, since panels now slide by `translate` and no transition runs. Open PRs: #847, #851, #853, #855 (4 of 8).

**Found, no row yet:**
- A row within-arm 0.00% and across-arm nonzero on all four pairs should be read as a mover until a frame says otherwise. shopify showed that on 10-31 and I explained it away.
- The `scale` and `rotate` properties split on all white space and have no `calc()`.
- Later relative or absolute boxes over a fixed box at the same z may lose the hit test as sticky did. Not checked against Chromium.
- shopify: the paragraph overlaps "AI all-star", and the logo is black on dark. Both on base too except the logo, which only paints now.

**Receipts (hub):** `2026-11-01-c10fix-*`, `2026-11-01-tcalc-*`, `2026-11-01-c2d2-ab*`, `2026-11-01-campaign-{c10fix-2095df23,tcalc-515f1b1e,c2d3-42fc0c49}.json`. Probes: `tools/c10/{c10fix,c10b2_r1,c10b2_var,translate_calc}_probe.mjs`, `tools/c2/{c2d_r1_probe,c2d_r1_probe2,held_probe,c2d_shop_chrome,c2d_shop_chrome2}.mjs`.

Worktree z-c10-fixed-rect removed. z-c2d-rework, z-c10b2-r1, z-c10-translate-calc and z-base-cae49416 kept for the sweep: pushed, acceptance not complete; the next slot starts from fresh checkouts. No frames in the repo. Aleph tools were not available in this session. The comparison Chrome is the oracle's 143.0.7499.4.
"""
with open(H + "digest-z.md", "a") as f:
    f.write(digest)
subprocess.run(["python3", H + "tools/c2/setstate.py", "C2", "open", "11:02 (11-01) Z lane: #851 @ `d6f2eb54` HELD behind #855 (shopify regression, see the 10:25 note). R1 rework done; suites and most of the A/B still owed. Next slot, after #855's suite."], check=True)
subprocess.run(["python3", H + "tools/c2/setstate.py", "C10", "open", "11:02 (11-01) Z lane: #854 landed. **#855 draft @ `6e32672f`** (`translate` with spaces in a function, flattens a depth): headless suite and app build owed. #853 @ `179d39ea` R1 items done, all gates owed. Atlas's (3) items not touched."], check=True)
p = H + "PLAN-z.md"
s = open(p).read()
anchor = "> **11-01 10:25 ET (Z lane): HOLD #851"
note = "> **11-01 11:02 ET (Z lane): #855 is draft @ `6e32672f`, the translate fix #851 needs. Headless suite and app build NOT run (cap). #851 @ `d6f2eb54` and #853 @ `179d39ea` are reworked, gates owed: do not flip them. Next slot: #855 suite, then #851 full gates, then #853 full gates.** Atlas: flip #855 now if you want R1 in parallel, knowing the suite gap. Open hiwave-macos PRs: #847, #851, #853, #855 (4 of 8). Digest has the rest.\n\n"
assert s.count(anchor) == 1
s = s.replace(anchor, note + anchor)
open(p, "w").write(s)
print("closed")
