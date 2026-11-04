#!/usr/bin/env python3
"""Set S5 back to open with the #874 note."""
p = '/Users/petecopeland/Repos/.worktrees/z-hub/trench/z/PLAN-z.md'; s = open(p).read()
old = "| Z lane | Prometheus | any non-author | in-progress | 03:05 (11-04) Z lane: in-progress per the 01:05 order (S5 first)."
assert s.count(old) == 1
s = s.replace(old, "| Z lane | Prometheus | any non-author | open | 03:25 (11-04) Z lane: **draft #874 @ `bbfeb08a`** (`atlas/z-s5-clip`, red `38264a63`: 14 of 25 Chromium 143 ink rows wrong on develop 76c6ff8b, now 25/25). Two causes: legacy `clip: rect()` was never parsed; `clip-path` skipped `<button>`/`<input>` boxes (eBay's header buttons). Narrow runs only (css 116/0, layout 881/0, engine clip/filter/outline/overflow/opacity/paint 209/0); full gates in batch, paint change so its own slot. Real-window eBay check owed (Atlas). Residuals: hit test ignores clip/clip-path; `getComputedStyle().clip` unread. 03:05 (11-04) Z lane: in-progress per the 01:05 order (S5 first).")
open(p, 'w').write(s)
print('ok')
