#!/usr/bin/env python3
"""gates_851.py <head8>: #851's parity build, campaign and A/B against develop cae49416, no suites. Ends G851-DONE."""
import os
import shutil
import subprocess
import sys

W = "/Users/petecopeland/Repos/.worktrees/"
T = W + "z-hub/trench/z/tools/"
C = W + "z-c2d-rework"
head = sys.argv[1]
print("parity rc", subprocess.run(["python3", W + "z-cargo.py", C, "build", "--profile", "parity", "-p", "parity-capture"], capture_output=True).returncode, flush=True)
os.makedirs(C + "/scratch/bins", exist_ok=True)
a, b = C + "/scratch/bins/base2", C + "/scratch/bins/cand2"
shutil.copy2(W + "z-base-cae49416/target/parity/parity-capture", a)
shutil.copy2(C + "/target/parity/parity-capture", b)
subprocess.run(["python3", T + "camp.py", C, "c2d3-" + head, b])
subprocess.run(["python3", T + "campdiff.py", W + "z-base-cae49416/scratch/camp-base-cae49416.json", C + "/scratch/camp-c2d3-" + head + ".json"])
print("AB-START", flush=True)
subprocess.run(["python3", T + "ab5.py", C, "c2d3", a, b])
print("G851-DONE", flush=True)
