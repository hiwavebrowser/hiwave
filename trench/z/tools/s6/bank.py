#!/usr/bin/env python3
"""bank.py: S6 run lines into receipts, S6 row back to open, digest addendum."""
import os
here = os.path.dirname(os.path.abspath(__file__))
z = os.path.join(here, '..', '..')
out = os.path.join(z, 'receipts', '2026-11-04-s6-runs.txt')
with open(out, 'w') as o:
    o.write('S6 #877, base develop 76c6ff8b, red 054b2019, candidate 301af344\n')
    for name in ('red.log', 'fix.log', 'narrow.log'):
        o.write(f'\n### {name}\n')
        for l in open(os.path.join(here, name), errors='replace'):
            s = l.rstrip()
            if 'test result' in s or 'FAILED' in s or 'panicked' in s or 'left:' in s or 'right:' in s:
                o.write(s + '\n')
p = os.path.join(z, 'PLAN-z.md'); s = open(p).read()
old = "| Z lane | Prometheus | any non-author | in-progress | 03:40 (11-04) Z lane: in-progress (01:05 order, after S2)."
assert s.count(old) == 1
s = s.replace(old, "| Z lane | Prometheus | any non-author | open | 03:50 (11-04) Z lane: **draft #877 @ `301af344`** (`atlas/z-s6-late-sheets`, red `054b2019`). Cause: a sheet still loading at `subresource_budget_ms` (8 s; 6 at a time, so microsoft's 37 queue into it) was dropped for good. Fix: the same fetch moves to `view.live_sheets`; `pump_live` inserts it at its document-order slot and restyles; budget unchanged, load not longer. Narrow 252/0. Fetch+paint: all-site A/B in batch (frames move only with `--live-ms`). Real-window microsoft check owed. Open: remote `@font-face` in a late sheet not fetched. 03:40 (11-04) Z lane: in-progress (01:05 order, after S2).")
open(p, 'w').write(s)
d = os.path.join(z, 'digest-z.md')
open(d, 'a').write("""- **S6 late stylesheets → draft #877 @ `301af344`** (red `054b2019`), added 03:50. A sheet still out at the 8 s subresource budget was dropped for good (microsoft: 37 sheets, 6 at a time). Now its fetch continues on the live loop and it lands at its document-order slot, then a restyle; the load itself is not longer. Narrow 252/0. Open PRs now 6 of 8. Real-window microsoft check owed; remote `@font-face` in a late sheet still not fetched.
""")
print(open(out).read())
