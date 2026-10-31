#!/usr/bin/env python3
"""logstat.py <log> [lines]: step headers, test-result lines and the last lines of a cargo log; load and time."""
import os, sys, time
path = sys.argv[1]
n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
print(time.strftime("%H:%M:%S"), "load %.1f" % os.getloadavg()[0])
try:
    lines = open(path, errors="replace").read().splitlines()
except OSError as e:
    print(e)
    sys.exit(0)
for l in lines:
    if l.startswith("===") or l.startswith("test result") or " rc=" in l:
        print(l[:160])
print("---")
for l in lines[-n:]:
    print(l[:220])
