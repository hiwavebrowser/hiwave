#!/usr/bin/env python3
"""digest1505b.py: fills in the #851 suite line of the 17:06 digest section."""
P = "/Users/petecopeland/Repos/.worktrees/z-hub/trench/z/digest-z.md"
s = open(P).read()
old = "app debug build rc=0. Headless suite: see the line below."
new = "app debug build rc=0. Headless 1436/0, finished 17:07, two minutes past the cap."
assert s.count(old) == 1
s = s.replace(old, new)
old = "z-c10b2-g, z-base-92342645 removed."
new = "z-c10b2-g, z-c2d-g, z-base-92342645, z-base-525f6ec0 removed."
assert s.count(old) == 1
open(P, "w").write(s.replace(old, new))
