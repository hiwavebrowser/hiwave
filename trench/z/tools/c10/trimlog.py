#!/usr/bin/env python3
"""trimlog.py <file> [more files]: keep only test results, failed test names, panics and asserts."""
import re
import sys

keep = re.compile(r"^(test result|test .*FAILED|error|thread '|assertion|\s+left:|\s+right:|\s+Running )")
for p in sys.argv[1:]:
    lines = [l for l in open(p, errors="replace").read().splitlines() if keep.match(l)]
    open(p, "w").write("\n".join(lines) + "\n")
    print(p.rsplit("/", 1)[-1], len(lines))
