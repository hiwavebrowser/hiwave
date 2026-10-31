#!/usr/bin/env python3
"""Close the 21:05 session: C2 back to open with the next step; append the digest."""
H = "/Users/petecopeland/Repos/.worktrees/z-hub/trench/z/"
p = H + "PLAN-z.md"
s = open(p).read()
old = "| in-progress | 22:35 (10-30): lane started slice (a), red first."
new = "| open | 22:40 (10-30): **(a) red pushed, no fix, no PR:** branch `atlas/z-c2-element-scroll` @ `3e9aa4c1`, `element_scroll_tests` 6 of 7 red against Chromium 143 (rect and elementFromPoint after scrollTop/Left, scrollTo/By, clamp, `overflow: hidden` scrolls, `visible` stays 0 where develop stores 25). No pixel test yet: add one first next session. Seam: offsets live only in `web_scroll.js`, keyed per element, and the engine is never told; geometry, hit test and paint all read offset zero. Next: carry the offset to the engine, translate the box's children inside its clip (paint, plus the `PushClip` at the overflow arm), and have `hit_test_scrolled` and the rect reads apply it. `diagnostics_tests::a_box_inside_a_scroll_container_says_element_scroll_is_not_applied` pins the gap and has to change with the fix. Continue from a fresh checkout of the branch."
assert old in s
s = s.replace(old, new)
open(p, "w").write(s)

d = H + "digest-z.md"
t = open(d).read()
if not t.endswith("\n"):
    t += "\n"
t += """
## 2026-10-30 22:40 Z-lane DI, CA1-2, C2

**(0) Develop check at c25c1d71: PASS.** App builds; layout 881/0, bindings 428/0, engine lib 618/0, headless 1269/0. Receipt `2026-10-30-dev-c25c1d71-suites.txt`.

**(1) DI -> #817 updated, still draft, @ `ec8ee96c`** (develop merged; red `b1cc2de8`, 3 of 5 failing). `display: inherit` under a `contents` parent now reads `contents`; this folds in the saved 10-28 patch.
- Headless 1274/0, app build rc=0. Campaign 26/26, 0 moved.
- A/B: one mover, apple 0.11%: the nav goes from 3 items to all of them in a row. The bar is still grey where Chromium's is dark, and the list is wider; both unchanged and not reduced.
- google read arm-tied at 1.89%; a swapped pass showed develop serving both variants.

**(2) CA1-2 -> #841 (draft) @ `c2693048`** (red `c7791696`, 5 of 6 failing). `flex: none|auto|initial|unset|content`, a lone basis and a basis written first now work; invalid forms drop against a Chromium 143 table.
- Campaign 26/26, 0 moved.
- A/B: github 5.57% (header search and sign-in move to the right edge, as in Chromium), cnn 0.28% (a card label moves 19 px; 21 px from its neighbour's row now, was 40, Chromium 0).
- **Headless 1273 passed, 2 failed.** Both failures passed by name on the same head, and the A/B was loading the machine during the run. The whole suite was not repeated quiet.

**(3) C2(a) started: red only, no fix, no PR.** Branch `atlas/z-c2-element-scroll` @ `3e9aa4c1`, 6 of 7 failing. The next step and the seam are on the C2 row. Not attempted past the red test: paint, geometry and hit test plus a 20-minute suite did not fit before the cap.

**For Atlas:**
- Flip #817 and #841 to ready and ask R1 (the lane can't). Open PRs: #817, #840, #841 (3 of 8).
- #841 was started before I read the CSS-week note. It is CSS and finished, but it sits outside the DI -> C2 order, so whether it lands ahead of the C rows is your call. #817 and #841 both touch `crates/rustkit-engine/src/lib.rs` in different arms and have not been merged together.
- The hub was on a detached HEAD at session close (your `checkout FETCH_HEAD` at 9a7f176d, three commits pushed from it). My plain `git push origin atlas/z` was rejected twice for that reason. Local `atlas/z` now points at origin again.

**Seen, no row yet:**
- `parse_flex_basis` answers `auto` for em, `calc()` and min/max-content: `flex: 1 1 10em` has basis auto, Chromium 160px. This is likely worth a C row; no red test yet.
- `flex: inherit` has no arm; not tested.
- github's hero is blank on both arms at 1280x800, and its logo is missing.
- `<slot>` is `contents` from the UA rule, so `display: inherit` under a slot reads the grandparent's value. Untested.

Worktrees z-di, z-ca1-2 and z-dev-c25c1d71 removed; z-c2 removed after its push. Frames were not kept. Aleph tools were not available in this session, so the reading was by git grep. The comparison Chrome is the oracle's 143.0.7499.4; the campaign is against its usual pinned baselines.
"""
open(d, "w").write(t)
