#!/usr/bin/env python3
"""crates.py <worktree> <log>: layout, bindings, engine lib tests at the worktree's head; prints the counts."""
import subprocess, sys
ZC = "/Users/petecopeland/Repos/.worktrees/z-cargo.py"
wt, log = sys.argv[1], sys.argv[2]
steps = [("layout", ["test", "-p", "rustkit-layout"]), ("bindings", ["test", "-p", "rustkit-bindings"]),
         ("engine lib", ["test", "-p", "rustkit-engine", "--lib"])]
with open(log, "w") as f:
    for name, args in steps:
        f.write("\n=== " + name + " ===\n"); f.flush()
        rc = subprocess.run(["python3", ZC, wt] + args, stdout=f, stderr=subprocess.STDOUT).returncode
        f.write("\n%s rc=%d\n" % (name, rc)); f.flush()
for l in open(log):
    if l.startswith("=== ") or " rc=" in l or l.startswith("test result") or l.rstrip().endswith("FAILED"):
        print(l.rstrip())
