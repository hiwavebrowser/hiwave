#!/usr/bin/env python3
"""setstate.py <row> <state> <note>: set a row's state cell in PLAN-z.md and put a note first in its log cell."""
import sys

PLAN = "/Users/petecopeland/Repos/.worktrees/z-hub/trench/z/PLAN-z.md"
row, state, note = sys.argv[1:4]
lines = open(PLAN).read().split("\n")
for i, line in enumerate(lines):
    if line.startswith(f"| {row} |"):
        cells = line.split(" | ")
        # id+title | owner | reviewer | r2 | state | log
        cells[-2] = state
        cells[-1] = note + " " + cells[-1]
        lines[i] = " | ".join(cells)
        print("set", row, state)
        break
else:
    sys.exit("no row " + row)
open(PLAN, "w").write("\n".join(lines))
