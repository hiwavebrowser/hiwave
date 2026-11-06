#!/usr/bin/env python3
"""zrows.py: list package rows whose owner cell names the Z lane and whose state is open/in-progress (line, id, owner, state)."""
import sys
path = '/Users/petecopeland/Repos/.worktrees/z-hub/trench/z/PLAN-z.md'
for i, l in enumerate(open(path), 1):
    if not l.startswith('|'):
        continue
    c = [x.strip() for x in l.split('|')]
    if len(c) < 8:
        continue
    # | id | package | owner | R1 | R2 | state | note |
    owner, state = c[3], c[6]
    if 'Z lane' in owner and state in ('open', 'in-progress'):
        print(i, c[1][:12], '| owner:', owner[:60], '| state:', state)
