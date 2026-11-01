#!/usr/bin/env python3
"""waitre.py <file> <regex> <secs>: poll a file until the regex appears; print the last lines."""
import re
import sys
import time

path, pattern, secs = sys.argv[1], sys.argv[2], float(sys.argv[3])
end = time.time() + secs
found = False
while time.time() < end:
    try:
        if re.search(pattern, open(path, errors="replace").read()):
            found = True
            break
    except FileNotFoundError:
        pass
    time.sleep(5)
print("found" if found else "timed out")
