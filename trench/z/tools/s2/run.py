#!/usr/bin/env python3
"""run.py <worktree> <log> <cargo args...>: z-cargo.py into a log, then print the result lines."""
import subprocess, sys, time

wt, log, args = sys.argv[1], sys.argv[2], sys.argv[3:]
t = time.time()
with open(log, "w") as f:
    rc = subprocess.run(["python3", "/Users/petecopeland/Repos/.worktrees/z-cargo.py", wt] + args,
                        stdout=f, stderr=subprocess.STDOUT).returncode
print(f"rc={rc} wall={time.time() - t:.0f}s")
keep = False
for l in open(log, errors="replace"):
    s = l.rstrip()
    if "panicked" in s or "wrong:" in s:
        keep = True
    if keep or "test result" in s or s.startswith("error") or s.startswith("test ") or ": ink " in s:
        print(s[:300])
    if keep and s == "":
        keep = False
