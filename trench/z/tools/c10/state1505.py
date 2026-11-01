#!/usr/bin/env python3
"""state1505.py <text>: prefix a dated note on the C10 row's note cell and set it in-progress/open."""
import re
import sys

P = "/Users/petecopeland/Repos/.worktrees/z-hub/trench/z/PLAN-z.md"
state, note = sys.argv[1], sys.argv[2]
lines = open(P).read().split("\n")
for i, l in enumerate(lines):
    if l.startswith("| C10 |"):
        m = re.search(r"\| any non-author \| (open|in-progress|blocked) \| ", l)
        lines[i] = l[: m.start()] + f"| any non-author | {state} | {note} " + l[m.end():]
        break
else:
    raise SystemExit("no row")
open(P, "w").write("\n".join(lines))
