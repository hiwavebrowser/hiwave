p = '/Users/petecopeland/Repos/.worktrees/z-hub/trench/z/PLAN-z.md'
s = open(p).read()
a = "| any non-author | in-progress | 09:05 (10-31): session on (a). 22:40 (10-30):"
assert s.count(a) == 1
s = s.replace(a, "| any non-author | in-progress | 10:15 (10-31): **(a) draft #845 @ `0e913b79`** (`atlas/z-c2-element-scroll`, red `3e9aa4c1` + `b1a09479`, 15 of 17): `scrollTop`/`scrollLeft` move paint, rects and the hit test as in Chromium 143; absolute boxes follow their containing block's scroller, fixed none; element `scroll` event; a box's own border is no longer scrollable overflow. Headless 1316/0 at `77457291` (head adds one test, module 20/0), layout 881/0, bindings 428/0, engine lib 618/0, app build rc=0; campaign 26/26 0 moved; 20-site A/B no mover (google, shopify, linkedin, yahoo, lyft repeated). Needs Atlas: flip ready, ask R1, real-window check. Next: (b). 22:40 (10-30):")
a = "`RK_NO_POS` should force `style.position = Static` in `transfer_positioning`;"
assert s.count(a) == 1
s = s.replace(a, "`RK_NO_POS` should force `style.position = Static` in `transfer_positioning`; (from C2a, 10-31) a `position: fixed` box inside a box with a relative offset moves with it (`shift_subtree` carries it: `top: 10px` on the parent reads the fixed child at y 10, Chromium 0);")
note = "> **10-31 10:15 ET (Z lane): C2(a) is draft #845 @ 0e913b79. Atlas: flip ready and ask R1 (the lane can't); the real-window check is yours per the row.** Develop check at 3bc6a2fb PASS. Open hiwave-macos PRs: #845.\n"
b = "> **10-31 05:50 ET (Atlas): C13 landed"
assert s.count(b) == 1
s = s.replace(b, note + b)
open(p, 'w').write(s)
