#!/usr/bin/env python3
"""part_851.py <head8> <site ...>: #851's campaign and a partial A/B on its built binary against develop cae49416."""
import os
import shutil
import subprocess
import sys

W = "/Users/petecopeland/Repos/.worktrees/"
T = W + "z-hub/trench/z/tools/"
C = W + "z-c2d-rework"
head = sys.argv[1]
os.makedirs(C + "/scratch/bins", exist_ok=True)
a, b = C + "/scratch/bins/base2", C + "/scratch/bins/cand2"
shutil.copy2(W + "z-base-cae49416/target/parity/parity-capture", a)
shutil.copy2(C + "/target/parity/parity-capture", b)
r = subprocess.run(["python3", T + "camp.py", C, "c2d3-" + head, b], capture_output=True, text=True)
print([l for l in r.stdout.splitlines() if l.startswith(("Passed", "Failed"))])
r = subprocess.run(["python3", T + "campdiff.py", W + "z-base-cae49416/scratch/camp-base-cae49416.json", C + "/scratch/camp-c2d3-" + head + ".json"], capture_output=True, text=True)
print(r.stdout.splitlines()[-1] if r.stdout else r.stderr[:300])
subprocess.run(["python3", T + "ab5.py", C, "c2d3", a, b] + sys.argv[2:])
for i, name in ((0, "base"), (1, "cand")):
    subprocess.run(["python3", T + "c2/ppm2png.py", f"{C}/scratch/x-c2d3/shopify-{i}.ppm", f"{C}/scratch/c2d3-{name}.png"])
