#!/usr/bin/env python3
"""Standing develop check (10-29 11:58 rule): build hiwave-app, then the touched crates' tests.
    devcheck.py <worktree> <logfile>
Each step's cargo output goes to <logfile>; a summary line per step is appended at the end.
"""
import os, subprocess, sys, time
wt, log = sys.argv[1], sys.argv[2]
ZC = "/Users/petecopeland/Repos/.worktrees/z-cargo.py"
steps = [
    ("build hiwave-app", ["build", "-p", "hiwave-app"]),
    ("layout", ["test", "-p", "rustkit-layout"]),
    ("bindings", ["test", "-p", "rustkit-bindings"]),
    ("engine lib", ["test", "-p", "rustkit-engine", "--lib"]),
    ("headless engine", ["test", "-p", "rustkit-engine", "--features", "headless"]),
]
summary = []
with open(log, "w") as f:
    for name, args in steps:
        t0 = time.time()
        f.write("\n=== " + name + " ===\n"); f.flush()
        rc = subprocess.run(["python3", ZC, wt] + args, stdout=f, stderr=subprocess.STDOUT).returncode
        summary.append("%s rc=%d %.0fs" % (name, rc, time.time() - t0))
        if name.startswith("build") and rc != 0:
            break
with open(log) as f:
    results = [l.strip() for l in f if l.startswith("test result") or "FAILED" in l or l.startswith("error")]
with open(log, "a") as f:
    f.write("\n--- SUMMARY ---\n" + "\n".join(summary) + "\n" + "\n".join(results[-60:]) + "\n")
print("\n".join(summary))
