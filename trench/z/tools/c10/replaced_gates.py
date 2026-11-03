#!/usr/bin/env python3
"""replaced_gates.py <worktree> <log>: C10(e) replaced slice narrow gates, each through z-cargo.py."""
import subprocess, sys
wt, log = sys.argv[1], sys.argv[2]
Z = "/Users/petecopeland/Repos/.worktrees/z-cargo.py"
runs = [
    ["test", "-p", "rustkit-engine", "--features", "headless", "--lib", "replaced_ratio"],
    ["test", "-p", "rustkit-layout", "--lib"],
    ["test", "-p", "rustkit-engine", "--features", "headless", "--lib", "grid"],
    ["test", "-p", "rustkit-engine", "--features", "headless", "--lib", "image"],
    ["test", "-p", "rustkit-engine", "--features", "headless", "--lib", "nested_layout_matrix"],
    ["test", "-p", "rustkit-engine", "--features", "headless", "--lib", "aspect"],
]
with open(log, "w") as f:
    for r in runs:
        f.write("\n### " + " ".join(r) + "\n"); f.flush()
        rc = subprocess.run(["python3", Z, wt] + r, stdout=f, stderr=subprocess.STDOUT).returncode
        f.write(f"### rc={rc}\n"); f.flush()
for l in open(log):
    if l.startswith("###") or "test result" in l or "panicked" in l or l.startswith("error"):
        print(l.rstrip()[:300])
