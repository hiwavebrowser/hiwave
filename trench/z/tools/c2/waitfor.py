#!/usr/bin/env python3
"""waitfor.py <file> <regex> [secs=570]: foreground wait; prints the matching line or TIMEOUT, then the file's size."""
import os, re, sys, time
path, rx, secs = sys.argv[1], re.compile(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 570
end = time.time() + secs
while time.time() < end:
    if os.path.exists(path):
        hit = [l for l in open(path, errors='replace') if rx.search(l)]
        if hit:
            print('HIT', hit[-1].strip()[:200])
            sys.exit(0)
    time.sleep(10)
print('TIMEOUT', os.path.getsize(path) if os.path.exists(path) else 'absent', time.strftime('%H:%M:%S'))
