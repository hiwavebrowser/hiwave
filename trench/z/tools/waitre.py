#!/usr/bin/env python3
"""waitre.py <file> <regex> [secs=580]: wait for a regex in a file; prints its matching lines, or TIMEOUT."""
import os
import re
import sys
import time

path, rx = sys.argv[1], re.compile(sys.argv[2])
end = time.time() + (float(sys.argv[3]) if len(sys.argv) > 3 else 580)
while time.time() < end:
    if os.path.exists(path):
        hits = [l for l in open(path, errors="replace").read().splitlines() if rx.search(l)]
        if hits:
            print("\n".join(h[:300] for h in hits))
            sys.exit(0)
    time.sleep(10)
print("TIMEOUT")
