#!/usr/bin/env python3
"""trial_shop.py <worktree> <tag>: bank the worktree's parity binary as scratch/bins/trial, A/B shopify against scratch/bins/base, write PNGs of one frame of each arm."""
import shutil
import subprocess
import sys

T = "/Users/petecopeland/Repos/.worktrees/z-hub/trench/z/tools/"
wt, tag = sys.argv[1], sys.argv[2]
trial = wt + "/scratch/bins/trial"
shutil.copy2(wt + "/target/parity/parity-capture", trial)
subprocess.run(["python3", T + "ab5.py", wt, tag, wt + "/scratch/bins/base", trial, "shopify"])
for i, name in ((0, "base"), (1, "trial")):
    subprocess.run(["python3", T + "c2/ppm2png.py", f"{wt}/scratch/x-{tag}/shopify-{i}.ppm", f"{wt}/scratch/{tag}-{name}.png"])
