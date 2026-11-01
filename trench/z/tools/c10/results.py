#!/usr/bin/env python3
"""results.py <worktree> [gates output file]: suite and campaign lines of a slice."""
import sys
wt = sys.argv[1]
for f in ('crates.log', 'suite.log'):
    print('##', f)
    for l in open(wt + '/' + f, errors='replace'):
        if l.startswith(('===', 'test result')) or ' rc=' in l or l.rstrip().endswith('FAILED'):
            print(l.strip()[:120])
if len(sys.argv) > 2:
    for l in open(sys.argv[2], errors='replace'):
        if l.startswith(('head', 'cases', 'Passed', 'binary')):
            print(l.strip()[:120])
