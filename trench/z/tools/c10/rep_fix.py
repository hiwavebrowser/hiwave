#!/usr/bin/env python3
"""rep_fix.py <worktree> <tag>: lyft with the arms swapped, the noisy rows again, cnn at the 90 s limit. Ends REPEATS-DONE."""
import subprocess
import sys

T = "/Users/petecopeland/Repos/.worktrees/z-hub/trench/z/tools/"
wt, tag = sys.argv[1], sys.argv[2]
a, b = wt + "/scratch/bins/base", wt + "/scratch/bins/cand"
subprocess.run(["python3", T + "ab5.py", wt, tag + "-swap", b, a, "lyft"])
subprocess.run(["python3", T + "ab5.py", wt, tag + "-rep", a, b] + sys.argv[3:])
subprocess.run(["python3", T + "ab5_long.py", wt, tag + "-cnn", a, b, "cnn"])
print("REPEATS-DONE", flush=True)
