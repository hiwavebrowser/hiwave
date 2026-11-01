#!/usr/bin/env python3
"""repeats.py: noisy A/B rows again (base vs C10b, C10b vs C10b2), and cnn at the 90 s limit. Ends REPEATS-DONE."""
import subprocess
W = '/Users/petecopeland/Repos/.worktrees/'
T = W + 'z-hub/trench/z/tools/'
for wt, tag, sites in [(W + 'z-c10b', 'c10b-rep', ['google', 'linkedin', 'shopify', 'lyft']),
                       (W + 'z-c10b2', 'c10b2-rep', ['google', 'linkedin', 'yahoo', 'bing', 'shopify', 'lyft'])]:
    a, b = wt + '/scratch/bins/base', wt + '/scratch/bins/cand'
    subprocess.run(['python3', T + 'ab5.py', wt, tag, a, b] + sites)
    subprocess.run(['python3', T + 'ab5_long.py', wt, tag + '-cnn', a, b, 'cnn'])
print('REPEATS-DONE', flush=True)
