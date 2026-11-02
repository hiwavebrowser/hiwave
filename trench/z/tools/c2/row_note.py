#!/usr/bin/env python3
"""row_note.py <row id> <state> <note>: set a package row's state in PLAN-z.md and put the note first in its notes cell."""
import re, sys

P = "/Users/petecopeland/Repos/.worktrees/z-hub/trench/z/PLAN-z.md"
rid, state, note = sys.argv[1:4]
lines = open(P).read().split("\n")
for i, line in enumerate(lines):
    if not line.startswith("| %s |" % rid):
        continue
    cells = line.split(" | ")
    for j in range(len(cells) - 1, 0, -1):
        if re.fullmatch(r"open|in-progress|blocked|done", cells[j].strip()):
            cells[j] = state
            cells[j + 1] = note + " " + cells[j + 1]
            lines[i] = " | ".join(cells)
            open(P, "w").write("\n".join(lines))
            print("row", rid, "cell", j, "of", len(cells))
            sys.exit(0)
    sys.exit("no state cell in row " + rid)
sys.exit("no row " + rid)
