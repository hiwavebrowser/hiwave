"""C2(c): plan row, top note and digest."""
H = '/Users/petecopeland/Repos/.worktrees/z-hub/trench/z/'
p = H + 'PLAN-z.md'
s = open(p).read()
a = "| any non-author | in-progress | 15:20 (10-31) Z lane: (c) in progress, branch `atlas/z-c2c-scroll-into-view` off develop 546d6196. 12:05 (10-31) Atlas:"
assert s.count(a) == 1
s = s.replace(a, "| any non-author | open | 16:45 (10-31) Z lane: **(c) draft #850 @ `f490aa7a`** (`atlas/z-c2c-scroll-into-view`, red `e63af36a`, 18 of 19): `scrollIntoView` and every fragment route move each enclosing scroller, then the window, as Chromium 143; `location.hash` now works as a setter (it did nothing); a page loaded with a fragment opens there; extents fixed: padding-end on a scroller, clipped content is not outer overflow. Headless 1356/0, app build rc=0; layout 881/0, bindings 428/0, engine lib 618/0 at `0828c4c1` (head changes one test); hiwave-app's own tests not run; campaign 26/26 0 moved; 20-site A/B no mover. Needs Atlas: flip ready, ask R1, real-window check (link into a nested scroller, URL opened with a fragment). **Residuals for this row:** the window has no horizontal extent (`max_scroll_offset.0` always 0); `scroll-margin`/`scroll-padding` unparsed (a sticky header covers the target); in-flow `margin-bottom` missing from a scroller's extent (109 vs 100); transform-held fixed and shadow-crossing fixed not handled. **Next: (d)**, from a fresh checkout of develop once #850 lands, or of #850's branch and say so. 12:05 (10-31) Atlas:")
a = "> **10-31 12:05 ET (Atlas):** C2(a) #845"
assert s.count(a) == 1
s = s.replace(a, "> **10-31 16:45 ET (Z lane): C2(c) is draft #850 @ f490aa7a. Atlas: flip ready and ask R1 (the lane can't); the real-window check is yours per the row.** Develop check at 546d6196 PASS. Open hiwave-macos PRs: #847, #848, #849, #850. **Found, no row yet, for Atlas to place:** an absolute box with no positioned ancestor is placed from its static parent, not the initial containing block (untouched develop: `top:300px` under a parent at y=200 paints at 500; Chromium's measured shape reads 1800 where the engine reads 2800). Looks broad; the cause in layout is not traced. Probes: `tools/c2/c2c_abs_probe.mjs`, `c2c_abs_develop.py`.\n\n" + a)
open(p, 'w').write(s)

digest = """
## 2026-10-31 16:45 Z-lane C2 (c)

**(0) Develop check at 546d6196: PASS.** App builds; layout 881/0, bindings 428/0, engine lib 618/0, headless 1336/0. Receipt `2026-10-31-dev-546d6196-suites.txt`.

**(1) C2(c) -> PR #850 (draft) @ `f490aa7a`** (red `e63af36a`, 18 of 19 failing). Before: `scrollIntoView` moved only the window, a fragment moved only the window's y, and assigning `location.hash` did nothing. After: each enclosing scroller moves, innermost first, then the window, as in Chromium 143, from every fragment route; a page loaded with a fragment opens there.
- Beyond the row's wording: `location.hash` is now a working setter, so pages that assign it navigate and hear `hashchange` for the first time. Two extent residuals from the (a) R1 are fixed, which moves `scrollHeight`/`scrollWidth` on scrollers with end padding and around clipped content. A fragment's `scroll` event now comes from a timer, so one existing test changed to pump first.
- Headless 1356/0 at the head, app build rc=0. Layout 881/0, bindings 428/0, engine lib 618/0 at `0828c4c1`; the head changes one test after it. hiwave-app's own tests were not run.
- The first full run at `0828c4c1` was 1355/1: that existing test, found only by the full suite. The window-x expectations, a fixture spacer and one replacement test changed after the red run, so they have no red run of their own; the PR says which.
- Campaign 26/26, 0 moved. 20-site A/B: no mover, and a regression guard only, since captures rarely scroll to anything. shopify differed on all four cross pairs at first; swapped and repeated twice, develop's own arm shows the same split. google and linkedin repeated as noise too; bing showed inside both arms and was not repeated; lyft had one failed capture on the candidate's arm and four clean on the repeat.

**Not proven, for Atlas:**
- **No real-window run.** The lane has no input grant. Try a link click into a nested scroller and opening a URL with a fragment.
- **The load-time fragment scroll is new behaviour on real pages**, covered by engine tests and not by any capture. It is skipped if the window has already moved, and a late layout does not re-apply it, where Chromium's anchor does.

**For Atlas:** flip #850 ready and ask R1. Open PRs: #847, #848, #849, #850 (4 of 8). C2 stays first in table order: next slice (d).

**Found, no row yet (the one to read):**
- **An absolute box with no positioned ancestor is placed from its static parent, not the initial containing block.** Untouched develop paints `top:300px` under a parent at y=200 at rows 500-519; Chromium's measured shape reads 1800 where the engine reads 2800, for plain, `auto` and `hidden` parents. It looks broad and the campaign and A/B never named it. The cause in layout is not traced. I first called this margin collapse in my session notes, and a spacer disproved that.

**Seen, on the C2 row:** the window has no horizontal extent; `scroll-margin`/`scroll-padding` are unparsed, so a sticky header covers a fragment's target; in-flow `margin-bottom` is missing from a scroller's extent.

**Receipts (hub):** `2026-10-31-c2c-{pr.md,ab.txt,ab-swap.txt,ab-shop.txt,ab-shop2.txt,suite.txt}`, `2026-10-31-campaign-{dev-546d6196,c2c-f490aa7a}.json`. Probes and wrappers: `tools/c2/c2c_*`.

Worktrees z-c2c and z-dev-546d6196 removed. No frames kept. Aleph tools were not available in this session, so the reading was by git grep. The comparison Chrome is the oracle's 143.0.7499.4; the campaign is against its usual pinned baselines.
"""
with open(H + 'digest-z.md', 'a') as f:
    f.write(digest)
