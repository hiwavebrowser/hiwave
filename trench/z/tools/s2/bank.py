#!/usr/bin/env python3
"""bank.py: S2 run lines into receipts/2026-11-04-s2-runs.txt; S2 row back to open with the #876 note."""
import os, subprocess
here = os.path.dirname(os.path.abspath(__file__))
out = os.path.join(here, '..', '..', 'receipts', '2026-11-04-s2-runs.txt')
with open(out, 'w') as o:
    o.write('S2 #876, base develop 76c6ff8b, red 3c3c3dbd, candidate 1c7da77c\n')
    o.write('\n### stops.py on live-20261103T1704.log\n')
    o.write(subprocess.run(['python3', os.path.join(here, 'stops.py'),
                            os.path.expanduser('~/Library/Logs/hiwave/live-20261103T1704.log')],
                           capture_output=True, text=True).stdout)
    o.write('(the 288-burst follows "Navigating content to: https://www.yahoo.com" at 22:10:39.239; '
            'Loading URL yahoo at 22:10:44.748; 11 entry=move holds between)\n')
    for name in ('red.log', 'fix.log', 'narrow.log'):
        o.write(f'\n### {name}\n')
        for l in open(os.path.join(here, name), errors='replace'):
            s = l.rstrip()
            if 'test result' in s or 'FAILED' in s or 'panicked' in s or 'left:' in s or 'right:' in s:
                o.write(s + '\n')
p = os.path.join(here, '..', '..', 'PLAN-z.md'); s = open(p).read()
old = "| Z lane | Prometheus | any non-author | in-progress | 03:37 (11-04) Z lane: in-progress (01:05 order, after S1)."
assert s.count(old) == 1
s = s.replace(old, "| Z lane | Prometheus | any non-author | open | 04:00 (11-04) Z lane: **draft #876 @ `1c7da77c`** (`atlas/z-s2-pointer-budget`, red `3c3c3dbd`). **Re-scoped, Atlas to accept:** the 288 stops are not a budget charge; they follow Pete's navigation to yahoo (22:10:39.239), whose cancel cut the leaving reddit page's queued move listeners; the load started 5.5 s later behind 11 queued ~430 ms hover-restyle moves. Fix: `coalesce` keeps only the latest of adjacent moves (marks/renders between), nothing reordered. Narrow 161/0. Open: the cancel is logged with the budget wording (mislabel); reddit hover restyle ~430 ms/move (suggest a cost row). 03:37 (11-04) Z lane: in-progress (01:05 order, after S1).")
open(p, 'w').write(s)
print(open(out).read()[:2500])
