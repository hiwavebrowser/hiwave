#!/usr/bin/env python3
"""bank.py: S1 result lines from the run logs into receipts/2026-11-04-s1-runs.txt; S1 row back to open."""
import os
here = os.path.dirname(os.path.abspath(__file__))
out = os.path.join(here, '..', '..', 'receipts', '2026-11-04-s1-runs.txt')
with open(out, 'w') as o:
    o.write('S1 #875, base develop 76c6ff8b, red 0b57baa0 + ed9ec076, candidate 6381303b, Chromium 143.0.7499.4\n')
    for name in ('red.log', 'red2.log', 'fix.log', 'core.log', 'engine-narrow.log', 'inspector.log'):
        o.write(f'\n### {name}\n')
        for l in open(os.path.join(here, name), errors='replace'):
            s = l.rstrip()
            if ('test result' in s or 'FAILED' in s or 'panicked' in s or 'left:' in s
                    or 'right:' in s or s.startswith('assertion')):
                o.write(s + '\n')
p = os.path.join(here, '..', '..', 'PLAN-z.md'); s = open(p).read()
old = "| Z lane | Prometheus | any non-author | in-progress | 03:25 (11-04) Z lane: in-progress (01:05 order, after S5)."
assert s.count(old) == 1
s = s.replace(old, "| Z lane | Prometheus | any non-author | open | 03:35 (11-04) Z lane: **draft #875 @ `6381303b`** (`atlas/z-s1-redirect-base`, red `0b57baa0` + `ed9ec076`). Cause confirmed: `load_url_for_nav` committed the requested URL after redirects, so `view.url`, address bar, `location`, `baseURI`, history entry and every relative URL belonged to the first host. Fix: rebind to `response.url` (request fragment kept) + `NavigationStateMachine::redirected_to`. Chromium 143 agrees on the same two-origin shape (`tools/s1/redirect_probe.mjs`). Narrow: redirect_base 3/0, core 30/0, engine nav/load/history/inspector 167+21 (one inspector pin updated to `/final`). Touches fetch/scripts: all-site A/B in batch. Real-window gmail check owed (Atlas). 03:25 (11-04) Z lane: in-progress (01:05 order, after S5).")
open(p, 'w').write(s)
print(open(out).read())
