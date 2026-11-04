#!/usr/bin/env python3
"""stops.py <app log>: group 'Script stopped at the script budget' lines into bursts and print, for each
burst, its size, sources, and the last navigation / click / load line before it (with the gap in ms)."""
import re, sys
from datetime import datetime
ansi = re.compile(r'\x1b\[[0-9;]*m')
def ts(l):
    try:
        return datetime.strptime(l[:26], '%Y-%m-%dT%H:%M:%S.%f')
    except ValueError:
        return None
marks = ('Navigating content to', 'Link clicked', 'Navigation finished', 'content click', 'Content thread hold',
         'Navigation started', 'commit', 'Starting navigation')
last_mark = None
bursts = []
for raw in open(sys.argv[1], errors='replace'):
    l = ansi.sub('', raw).rstrip()
    t = ts(l)
    if t is None:
        continue
    if 'Script stopped at the script budget' in l:
        src = re.search(r'source=(\S+)', l).group(1)
        el = re.search(r'elapsed_ms=(\d+)', l).group(1)
        if bursts and (t - bursts[-1]['end']).total_seconds() < 1.0:
            b = bursts[-1]
        else:
            b = {'start': t, 'end': t, 'n': 0, 'src': {}, 'el': set(), 'mark': last_mark}
            bursts.append(b)
        b['end'] = t; b['n'] += 1; b['src'][src] = b['src'].get(src, 0) + 1; b['el'].add(el)
    elif any(m in l for m in marks):
        last_mark = (t, l[27:200])
for b in bursts:
    m = b['mark']
    gap = (b['start'] - m[0]).total_seconds() * 1000 if m else None
    print(f"{b['start'].time()} n={b['n']} elapsed={sorted(b['el'])} src={b['src']}")
    print(f"    before (+{gap:.1f} ms): {m[1] if m else None}")
