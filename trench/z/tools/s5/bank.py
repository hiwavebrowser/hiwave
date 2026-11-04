#!/usr/bin/env python3
"""bank.py: S5 result lines from the run logs into receipts/2026-11-04-s5-runs.txt."""
import os
here = os.path.dirname(os.path.abspath(__file__))
out = os.path.join(here, '..', '..', 'receipts', '2026-11-04-s5-runs.txt')
with open(out, 'w') as o:
    o.write('S5 #874, base develop 76c6ff8b, red 38264a63, candidate bbfeb08a, Chromium 143.0.7499.4\n')
    for name in ('red.log', 'fix-head.log', 'css-parse.log', 'narrow-css-layout.log', 'engine-narrow.log'):
        o.write(f'\n### {name}\n')
        keep = False
        for l in open(os.path.join(here, name), errors='replace'):
            s = l.rstrip()
            if 'wrong:' in s:
                keep = True
            if keep or 'test result' in s or 'Running' in s or 'FAILED' in s:
                o.write(s + '\n')
            if keep and s == '':
                keep = False
print(open(out).read()[:3000])
