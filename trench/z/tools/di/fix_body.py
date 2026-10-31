#!/usr/bin/env python3
"""Correct two lines of the CA1-2 PR body with what was measured."""
p = "/Users/petecopeland/Repos/.worktrees/z-ca1-2/scratch/final-body-ca12.md"
s = open(p).read()
old = "The band at y 607-646 is the same change further down the page."
new = "The band at y 607-646 is a coloured bar lower on the page moving up 19 px (y 626 to 607; Chromium 526). The hero above that bar is blank on both arms; not reduced."
assert old in s
s = s.replace(old, new)
i = s.index("- linkedin: ")
j = s.index("- lyft: ", i)
s = s[:i] + "- linkedin: develop against itself reads 89.90%, 2.96% and 2.64% with 6 and 18 script records, so those are page variants. One pass read arm-tied at 40.96% (`ab-ca12-r.txt`); it did not repeat in four later passes, and the seats' notes record 41% as another served page. Not proven beyond that.\n" + s[j:]
open(p, "w").write(s)
