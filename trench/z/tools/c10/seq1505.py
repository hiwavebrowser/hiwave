#!/usr/bin/env python3
"""seq1505.py <base sha>: #855 suites and campaign against the base, then #853's full gates. Ends SEQ-DONE."""
import os
import shutil
import subprocess
import sys

W = "/Users/petecopeland/Repos/.worktrees/"
T = W + "z-hub/trench/z/tools/"
ZC = W + "z-cargo.py"
SEED = W + "_seed/hiwave-macos.git"
base = sys.argv[1]
B = W + "z-base-" + base[:8]
C = W + "z-c10-tcalc2"
if not os.path.exists(B):
    subprocess.run(["git", "-C", SEED, "worktree", "add", "-q", "--detach", B, base], check=True)
head = subprocess.run(["git", "-C", C, "rev-parse", "--short=8", "HEAD"], capture_output=True, text=True).stdout.strip()
print("START 855", head, flush=True)
subprocess.run(["python3", T + "c2/suite.py", C])
print("SUITE-855-DONE", flush=True)
for wt in (B, C):
    with open(wt + "/parity-build.log", "w") as f:
        rc = subprocess.run(["python3", ZC, wt, "build", "--profile", "parity", "-p", "parity-capture"], stdout=f, stderr=subprocess.STDOUT).returncode
    print(wt, "parity rc", rc, flush=True)
os.makedirs(C + "/scratch/bins", exist_ok=True)
A_BIN, B_BIN = C + "/scratch/bins/base", C + "/scratch/bins/cand"
shutil.copy2(B + "/target/parity/parity-capture", A_BIN)
shutil.copy2(C + "/target/parity/parity-capture", B_BIN)
subprocess.run(["python3", T + "camp.py", B, "base-" + base[:8], A_BIN])
subprocess.run(["python3", T + "camp.py", C, "tcalc2-" + head, B_BIN])
subprocess.run(["python3", T + "campdiff.py", B + "/scratch/camp-base-" + base[:8] + ".json", C + "/scratch/camp-tcalc2-" + head + ".json"])
print("CAMP-855-DONE", flush=True)
subprocess.run(["python3", T + "c10/gates.py", W + "z-c10b2-g", base, "c10b2g"])
print("SEQ-DONE", flush=True)
