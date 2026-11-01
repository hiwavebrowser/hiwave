#!/usr/bin/env python3
"""bank2.py <worktree> <tag> <head8>: small text receipts of one slice to the hub."""
import os
import shutil
import sys

W = "/Users/petecopeland/Repos/.worktrees/"
R = W + "z-hub/trench/z/receipts/2026-11-01-"
wt, tag, head = sys.argv[1], sys.argv[2], sys.argv[3]
pairs = [
    ("scratch/pr-final.md", tag + "-pr.md"),
    ("scratch/red.txt", tag + "-red.txt"),
    (f"scratch/ab-{tag}.txt", tag + "-ab.txt"),
    (f"scratch/ab-{tag}-swap.txt", tag + "-ab-swap.txt"),
    (f"scratch/ab-{tag}-rep.txt", tag + "-ab-rep.txt"),
    (f"scratch/ab-{tag}-cnn.txt", tag + "-ab-cnn.txt"),
    (f"scratch/camp-{tag}-{head}.json", f"campaign-{tag}-{head}.json"),
]
for a, b in pairs:
    p = os.path.join(wt, a)
    if os.path.exists(p):
        shutil.copyfile(p, R + b)
    else:
        print("missing", a)
keep = []
for f in ("crates.log", "suite.log"):
    p = os.path.join(wt, f)
    if os.path.exists(p):
        keep += [l for l in open(p, errors="replace").read().splitlines() if l.startswith(("===", "test result")) or " rc=" in l]
open(R + tag + "-suite.txt", "w").write("\n".join(keep) + "\n")
print("banked", tag)
