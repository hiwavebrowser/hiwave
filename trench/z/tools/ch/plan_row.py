"""Set a package row's owner/state/note in PLAN-z.md. usage: plan_row.py <id> <state> <note> [owner]"""
import re, sys

pid, state, note = sys.argv[1], sys.argv[2], sys.argv[3]
owner = sys.argv[4] if len(sys.argv) > 4 else None
p = '/Users/petecopeland/Repos/.worktrees/z-hub/trench/z/PLAN-z.md'
lines = open(p).read().split('\n')
hits = [i for i, l in enumerate(lines) if l.startswith('| ' + pid + ' |')]
assert len(hits) == 1, hits
cells = lines[hits[0]].split(' | ')
# cells: [ '| id', title, owner, r1, r2, state, notes |' ]
if owner:
    cells[2] = owner
cells[5] = state
cells[6] = cells[6].rstrip(' |') + ' ' + note + ' |'
lines[hits[0]] = ' | '.join(cells)
open(p, 'w').write('\n'.join(lines))
print(lines[hits[0]][-300:])
