#!/usr/bin/env python3
"""waitfor.py <file> <regex> <secs>: poll a file until the regex appears; print the time and whether it did."""
import re, sys, time
path, pat, limit = sys.argv[1], re.compile(sys.argv[2]), float(sys.argv[3])
t0 = time.time()
while time.time() - t0 < limit:
    try:
        if pat.search(open(path, errors="replace").read()):
            print("found after %.0f s at %s" % (time.time() - t0, time.strftime("%H:%M:%S")))
            sys.exit(0)
    except OSError:
        pass
    time.sleep(5)
print("not yet after %.0f s at %s" % (time.time() - t0, time.strftime("%H:%M:%S")))
