"""Set a PLAN-z.md package row's state cell and prepend a note to its notes cell.
usage: rowstate.py <row id> <new state> <note>"""
import sys

P = '/Users/petecopeland/Repos/.worktrees/z-hub/trench/z/PLAN-z.md'
row, state, note = sys.argv[1], sys.argv[2], sys.argv[3]
lines = open(P).read().split('\n')
hits = [i for i, l in enumerate(lines) if l.startswith('| %s |' % row)]
assert len(hits) == 1, hits
cells = lines[hits[0]].split(' | ')
# cells: [ '| ID', desc, owner, r1, r2, state, notes |' ]
cells[5] = state
cells[6] = note + ' ' + cells[6]
lines[hits[0]] = ' | '.join(cells)
open(P, 'w').write('\n'.join(lines))
print(lines[hits[0]][:200], '...', cells[5])
