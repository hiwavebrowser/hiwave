#!/usr/bin/env python3
"""close.py: C10(b)/(b2) row, plan note, digest."""
H = '/Users/petecopeland/Repos/.worktrees/z-hub/trench/z/'
p = H + 'PLAN-z.md'
s = open(p).read()
old = '| any non-author | in-progress | 03:10 (11-01) Z lane: (b) transforms on rects started. 02:00 (10-31)'
assert old in s
s = s.replace(old, '| any non-author | open | 04:25 (11-01) Z lane: **(b) draft #852 @ `9551f252`** (`atlas/z-c10b-transform-rects`, off develop; red 18 of 21): rects of transformed boxes read as Chromium 143, `offset*` unchanged. **(b2) draft #853 @ `64e4081e`** (`atlas/z-c10b2-transform-3d`, stacked on #852; red 12 of 14), not on this row by name, Atlas to place: 3D functions parse and flatten, a bad value refuses the declaration. Both: campaign 26/26 0 moved, 20-site A/B no mover (guard only), headless 1356/0 and 1370/0. Added by these: (m) a fixed box under a transform is placed from the viewport (`13 24`, Chromium `13 124`; ignored test on #852); (n) the painter and hit test transform a plain inline, Chromium does not; (o) a transformed box is an `offsetParent` in Chromium (goes with (c)); (p) `em`, `rem`, `vw`, `vh` in a transform resolve against 16px and a zero viewport (ignored test on #853); (q) perspective with depth (ignored test on #853). Next slice in this row: (a). 02:00 (10-31)')
note = '''> **11-01 04:25 ET (Z lane): C10(b) is draft #852 @ 9551f252; (b2) is draft #853 @ 64e4081e, stacked on it. Atlas: flip ready and ask R1 in that order (the lane can't).** Develop is still 546d6196, so no develop check. Open hiwave-macos PRs: #847, #848, #849, #850, #851, #852, #853 (**7 of 8**). **Two calls for Atlas:** (1) #853 is not on C10 by name; the (b) red tests showed `translate3d` and every other 3D function doing nothing, so I took it as a follow-on. Accept it or send it back. (2) #852 and #851 both rewrite the rect read: whichever lands second needs a merge, and if #852 lands first, `transformed_rect` needs the sticky shift added to its walk. **Next slot: C10(a)**, the one PR the cap leaves. The abspos finding from 10-31 16:45 is still unplaced.

'''
mark = '> **10-31 22:25 ET (Z lane): C2(d) is draft #851'
assert mark in s
s = s.replace(mark, note + mark, 1)
open(p, 'w').write(s)
d = H + 'digest-z.md'
open(d, 'a').write('''
## 2026-11-01 04:25 Z-lane C10 (b), (b2)

**(1) C10(b) -> PR #852 (draft) @ `9551f252`**, off develop (red `f4f29b9f`, 18 of 21 failing). Before: `getBoundingClientRect` and `getClientRects` answered the untransformed box while paint and hit tests moved it. After: they read as Chromium 143 for every transform tested, through nesting, element scrolls and the window's scroll; `offset*` stay where layout put the box.
- Beyond the row's wording: an absolute box under a transformed box that is not positioned now takes that box as its chain parent.
- Headless 1356/0, layout 881/0, bindings 428/0, engine lib 618/0, app build rc=0. hiwave-app's own tests were not run.
- Campaign 26/26, 0 moved. 20-site A/B: no mover, a regression guard only, since captures do not interact. google, linkedin and shopify differ between captures of the same binary, so they cannot rule out a small real change there. lyft failed one capture on the candidate's arm in both runs; I read that as the site, unproven. cnn clean at a 90 s limit.

**(2) C10(b2) -> PR #853 (draft) @ `64e4081e`**, stacked on #852 (red `32212297`, 12 of 14 failing). **Not on the row by name.** Before: `translate3d`, `translateZ`, `scale3d`, `scaleZ`, `rotateX/Y/Z`, `rotate3d`, `matrix3d` and `perspective` did nothing, and an unknown function was skipped with the rest kept. After: they flatten as in Chromium 143, and a bad value refuses the whole declaration.
- **Biggest risk:** `translateZ(0)` and `translate3d(0,0,0)` now create a real transform on every page using them as a GPU hint: a containing block, a stacking context and a `PushTransform`. Chromium does the same, but it was not timed, and it exposes the fixed-box gap below on more pages.
- Stricter parsing can remove a transform that used to apply, on values Chromium also refuses.
- Headless 1370/0, layout 881/0, bindings 428/0, engine lib 618/0, app build rc=0. hiwave-app's own tests were not run.
- Paint checked with frames on seven values: base left all six 3D boxes unmoved; the candidate lands on Chromium's rect on all seven (half-pixel edges read one row short on the pure-lime test).
- Campaign 26/26, 0 moved. 20-site A/B: no mover, also a guard only: a page whose 3D transforms change after script acts would not show. bing and linkedin vary between captures of the same binary and cannot rule out a small real change. cnn clean at a 90 s limit.

**Not proven, for Atlas:**
- **No real-window run for either.** The lane has no input grant. For #853 try a carousel or drawer that animates by `translate3d`.
- **#852 against #851 is unmerged and untested:** both rewrite the rect read, and a sticky box under a transform has no test against the two together.

**For Atlas:** flip #852 ready and ask R1, then #853. Accept or send back #853, since it is off the row's wording. Open PRs: #847-#853 (7 of 8). Next slot takes C10(a).

**Found, on the C10 row as (m)-(q):**
- A fixed box under a transform is placed from the viewport (`13 24`, Chromium `13 124`). This is the one to read: #853 makes it reachable through `translateZ(0)`.
- The painter and hit test transform a plain inline; Chromium does not, and the rect now follows Chromium.
- A transformed box is an `offsetParent` in Chromium, not here.
- `em`, `rem`, `vw` and `vh` in a transform resolve against 16px and a zero viewport.
- Perspective with depth is lost.
- The 10-31 abspos bug is still unplaced.

**Receipts (hub):** `2026-11-01-c10b-{pr.md,ab.txt,ab-rep.txt,ab-cnn.txt,red.txt,suite.txt}`, `2026-11-01-c10b2-{same}`, `2026-11-01-campaign-{base-546d6196,c10b-9551f252,c10b2-64e4081e}.json`. Probes and wrappers: `tools/c10/`.

Worktrees z-c10b, z-c10b2 and z-base-546d6196 removed. No frames kept. Aleph tools were not available in this session, so the reading was by git grep. The comparison Chrome is the oracle's 143.0.7499.4; the campaign is against its usual pinned baselines.
''')
