#!/usr/bin/env python3
"""keep_both.py <file>: resolve every conflict by keeping both sides, ours first, with a blank line between."""
import re
import sys

p = sys.argv[1]
s = open(p).read()
s, n = re.subn(r"^<<<<<<< [^\n]*\n(.*?)^=======\n(.*?)^>>>>>>> [^\n]*\n", lambda m: m.group(1).rstrip("\n") + "\n\n" + m.group(2), s, flags=re.S | re.M)
open(p, "w").write(s)
print("resolved", n)
