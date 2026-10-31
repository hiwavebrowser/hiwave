#!/usr/bin/env python3
"""suite.py <worktree>: the candidate's gates through the lease; log in <worktree>/suite.log, ending in SUITES-DONE."""
import subprocess, sys, time
ZC = "/Users/petecopeland/Repos/.worktrees/z-cargo.py"
wt = sys.argv[1]
steps = [
    ("build hiwave-app", ["build", "-p", "hiwave-app"]),
    ("headless engine", ["test", "-p", "rustkit-engine", "--lib", "--features", "headless"]),
]
with open(wt + "/suite.log", "w") as f:
    for name, args in steps:
        t0 = time.time()
        f.write("\n=== " + name + " ===\n"); f.flush()
        rc = subprocess.run(["python3", ZC, wt] + args, stdout=f, stderr=subprocess.STDOUT).returncode
        f.write("\n%s rc=%d %.0fs\n" % (name, rc, time.time() - t0)); f.flush()
    f.write("\nSUITES-DONE\n")
