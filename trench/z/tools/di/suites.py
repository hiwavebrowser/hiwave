#!/usr/bin/env python3
"""suites.py: candidate gates in sequence through the lease; one log per worktree, ending in SUITES-DONE."""
import subprocess, time
ZC = "/Users/petecopeland/Repos/.worktrees/z-cargo.py"
W = "/Users/petecopeland/Repos/.worktrees/"
steps = [
    ("build hiwave-app", ["build", "-p", "hiwave-app"]),
    ("headless engine", ["test", "-p", "rustkit-engine", "--lib", "--features", "headless"]),
]
for wt in ["z-di", "z-ca1-2"]:
    with open(W + wt + "/suite.log", "w") as f:
        for name, args in steps:
            t0 = time.time()
            f.write("\n=== " + name + " ===\n"); f.flush()
            rc = subprocess.run(["python3", ZC, W + wt] + args, stdout=f, stderr=subprocess.STDOUT).returncode
            f.write("\n%s rc=%d %.0fs\n" % (name, rc, time.time() - t0)); f.flush()
        f.write("\nSUITES-DONE\n")
