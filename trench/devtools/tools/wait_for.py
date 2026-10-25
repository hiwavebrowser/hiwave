#!/usr/bin/env python3
"""wait_for.py <file> <regex> [secs=540]: poll a log until a regex shows (or the time is up).
Prints the matching lines (or 'timeout') and the file's last line, for a foreground wait on a
background job without a shell sleep loop."""
import os, re, sys, time
path, pat = sys.argv[1], re.compile(sys.argv[2], re.M)
end = time.time() + (int(sys.argv[3]) if len(sys.argv) > 3 else 540)
text = ""
while time.time() < end:
    text = open(path, errors="replace").read() if os.path.exists(path) else ""
    if pat.search(text):
        print("\n".join(m.group(0) for m in pat.finditer(text)))
        break
    time.sleep(15)
else:
    print("timeout")
lines = text.strip().splitlines()
print("last:", lines[-1][:200] if lines else "(empty)", "| load", round(os.getloadavg()[0], 1))
