import shutil
W = '/Users/petecopeland/Repos/.worktrees/'
H = W + 'z-hub/trench/z/'
R = H + 'receipts/2026-10-31-'
B = W + 'z-c2b/'
for a, b in [(B + 'scratch/pr.md', R + 'c2b-pr.md'),
             (B + 'scratch/camp-c2b-45292397.json', R + 'campaign-c2b-45292397.json')]:
    shutil.copyfile(a, b)
keep = []
for l in open(B + 'suite.log'):
    if l.startswith('test result') or ' rc=' in l:
        keep.append(l.rstrip())
for l in open(B + 'crates.log'):
    if l.startswith('===') or l.startswith('test result') or ' rc=' in l:
        keep.append(l.rstrip())
open(R + 'c2b-suite.txt', 'w').write('\n'.join(keep) + '\n')

p = H + 'PLAN-z.md'
s = open(p).read()
a = "| any non-author | in-progress | 10:15 (10-31): **(a) draft #845 @ `0e913b79`**"
assert s.count(a) == 1
s = s.replace(a, "| any non-author | open | 10:50 (10-31): **(b) draft #846 @ `45292397`** (`atlas/z-c2b-wheel`, stacked on #845; red `54e2b947`, 11 of 18): the content view's wheel moves the innermost scroller under the pointer that can move, then hands on, as Chromium 143; a 300 ms gesture hold is the engine's own rule (the oracle's discrete wheels cannot show one). Headless 1335/0, layout 881/0, bindings 428/0, engine lib 618/0, app build rc=0; campaign 26/26 0 moved; no site A/B (captures never send a wheel); hiwave-app's own tests not run. Needs Atlas after #845: flip ready, ask R1, real-window check (the lane has no input grant). `overscroll-behavior` is not parsed: candidate item here or on C12. **Next: (c), from a fresh checkout of #846's branch or develop once they land.** 10:15 (10-31): **(a) draft #845 @ `0e913b79`**")
a = "Needs Atlas: flip ready, ask R1, real-window check. Next: (b). 22:40 (10-30):"
assert s.count(a) == 1
s = s.replace(a, "Needs Atlas: flip ready, ask R1, real-window check. 22:40 (10-30):")
a = "> **10-31 10:15 ET (Z lane): C2(a) is draft #845 @ 0e913b79. Atlas: flip ready and ask R1 (the lane can't); the real-window check is yours per the row.** Develop check at 3bc6a2fb PASS. Open hiwave-macos PRs: #845.\n"
assert s.count(a) == 1
s = s.replace(a, "> **10-31 10:50 ET (Z lane): C2(a) is draft #845 @ 0e913b79; C2(b) is draft #846 @ 45292397, stacked on #845. Atlas: flip #845 ready and ask R1 (the lane can't), then #846; the real-window check is yours per the row. Both are unproven in a real window.** Develop check at 3bc6a2fb PASS. Open hiwave-macos PRs: #845, #846. C2 stays first in table order: next slice (c).\n")
open(p, 'w').write(s)

digest = """
## 2026-10-31 10:50 Z-lane C2 (a), (b)

**(0) Develop check at 3bc6a2fb: PASS.** App builds; layout 881/0, bindings 428/0, engine lib 618/0, headless 1297/0. Receipt `2026-10-31-dev-3bc6a2fb-suites.txt`. This includes C13 (6f64c7c4), merged into the C2 branch first as ordered.

**(1) C2(a) -> PR #845 (draft) @ `0e913b79`** (red `3e9aa4c1`, `b1a09479`, 15 of 17 failing). Before: `scrollTop` on a box was stored and read by nothing. After: paint, rects and the hit test follow it, as in Chromium 143, with absolute boxes following their containing block's scroller and fixed boxes none.
- Beyond the row's wording: elements now get their own `scroll` event, and a box's own border no longer counts as scrollable overflow, which moves `scrollHeight`/`scrollWidth` for every bordered element.
- Headless 1316/0 at `77457291` (the head adds one test; module 20/0), layout 881/0, bindings 428/0, engine lib 618/0, app build rc=0. Campaign 26/26, 0 moved.
- 20-site A/B: no mover. It is a regression guard only, since few captures show an element scroll. Noisy rows repeated: google's variant showed on develop's arm too once the arms were swapped; shopify and linkedin on both arms; yahoo settled; lyft 2 failed captures of 12, both on develop's arm.
- 3 tests and one fixture line came after the fix and have no recorded red run; the PR says which.

**(2) C2(b) -> PR #846 (draft) @ `45292397`, stacked on #845** (red `54e2b947`, 11 of 18 failing). Before: the wheel only scrolled the window. After: it moves the innermost scroller under the pointer that can move, then hands on, per 15 cases against Chromium 143.
- Headless 1335/0, layout 881/0, bindings 428/0, engine lib 618/0, app build rc=0. Campaign 26/26, 0 moved. No site A/B: captures never send a wheel. hiwave-app's own tests were not run.

**Not proven, for Atlas:**
- **Neither PR has run in a real window.** The lane has no input grant. For (b), the path from `scrollWheel:` to `scroll_at` is compiled, not run.
- **The 300 ms gesture hold in (b) is my own rule.** Playwright's discrete wheels chain at once, so the oracle cannot show gesture latching. Worth a feel test on a trackpad, which also answers the next point.
- **Each wheel step on a box rebuilds the whole display list.** Not timed on a large page.

**For Atlas:** flip #845 ready and ask R1, then #846 after it. Open PRs: #845, #846 (2 of 8). #846's diff against develop includes #845 until that lands.

**Seen, no row yet:**
- A `position: fixed` box inside a box with a relative offset moves with it (#843's `shift_subtree`). Written on C12.
- `overscroll-behavior` is a style field the engine never parses, so a `contain` box hands on where Chromium stops.
- A fixed box inside a positioned scroller is still clipped by it (old). An escaping absolute or fixed box still counts toward its scroller's `scrollWidth` (old).

**Receipts (hub):** `2026-10-31-c2a-{pr.md,ab.txt,ab-rep.txt,ab-swap.txt,suite.txt}`, `2026-10-31-c2b-{pr.md,suite.txt}`, `2026-10-31-campaign-{dev-3bc6a2fb,c2a-77457291,c2b-45292397}.json`. Probes and wrappers: `tools/c2/`.

Worktrees z-c2, z-c2b and z-dev-3bc6a2fb removed. No frames kept. Aleph tools were not available in this session, so the reading was by git grep. The comparison Chrome is the oracle's 143.0.7499.4; the campaign is against its usual pinned baselines.
"""
with open(H + 'digest-z.md', 'a') as f:
    f.write(digest)
