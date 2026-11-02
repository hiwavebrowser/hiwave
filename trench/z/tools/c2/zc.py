#!/usr/bin/env python3
"""zc.py <log> <worktree> <cargo args...>: z-cargo with CARGO_SERIAL_WAIT=0 (the lease dir sat empty from 11-02 10:48;
cargo-serial never treats that as stale). Prints test outcomes and failure lines, wall seconds at the end."""
import os, re, subprocess, sys, time

log, wt, args = sys.argv[1], sys.argv[2], sys.argv[3:]
os.environ["CARGO_SERIAL_WAIT"] = "0"
t = time.time()
with open(log, "w") as f:
    rc = subprocess.run(["python3", "/Users/petecopeland/Repos/.worktrees/z-cargo.py", wt] + args, stdout=f, stderr=subprocess.STDOUT).returncode
for line in open(log, errors="replace"):
    if re.match(r"test result|error|test .*FAILED|\d+ of \d+ wrong|opacity:|computed ", line):
        print(line.rstrip()[:170])
print("rc", rc, "secs", int(time.time() - t))
