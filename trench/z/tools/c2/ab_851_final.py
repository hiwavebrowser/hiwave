#!/usr/bin/env python3
"""ab_851_final.py: the owed #851 items at 2efc47f6. Parity builds of base and head, then the 20-site A/B
on banked binaries, then hiwave-app's own tests. Log lines end in ALL-DONE."""
import os, shutil, subprocess

W = "/Users/petecopeland/Repos/.worktrees/"
T = W + "z-hub/trench/z/tools/"
ZC = W + "z-cargo.py"
C = W + "z-c2-ab851"
B = W + "z-base-afa159da"
R = W + "z-c12-opacity"
# The lease dir was left empty (no pid) at about 10:48 on 11-02, and cargo-serial never treats that as stale.
# Do not wait out its 2400 s per build; this script runs its own builds one at a time.
os.environ["CARGO_SERIAL_WAIT"] = "0"

for wt in (B, C):
    with open(wt + "/parity-build.log", "w") as f:
        rc = subprocess.run(["python3", ZC, wt, "build", "--profile", "parity", "-p", "parity-capture"],
                            stdout=f, stderr=subprocess.STDOUT).returncode
    print(wt, "parity rc", rc, flush=True)
with open(R + "/red.log", "w") as f:
    rc = subprocess.run(["python3", ZC, R, "test", "-p", "rustkit-engine", "--features", "headless", "--lib", "opacity_value_tests"],
                        stdout=f, stderr=subprocess.STDOUT).returncode
print("RED-DONE rc", rc, flush=True)
os.makedirs(C + "/scratch/bins", exist_ok=True)
A_BIN, B_BIN = C + "/scratch/bins/base", C + "/scratch/bins/cand"
shutil.copy2(B + "/target/parity/parity-capture", A_BIN)
shutil.copy2(C + "/target/parity/parity-capture", B_BIN)
print("AB-START", flush=True)
subprocess.run(["python3", T + "ab5.py", C, "c2final", A_BIN, B_BIN])
print("AB-DONE", flush=True)
with open(C + "/app-tests.log", "w") as f:
    rc = subprocess.run(["python3", ZC, C, "test", "-p", "hiwave-app", "--features", "rustkit"],
                        stdout=f, stderr=subprocess.STDOUT).returncode
print("app tests rc", rc, flush=True)
for line in open(C + "/app-tests.log", errors="replace"):
    if line.startswith("test result") or line.rstrip().endswith("FAILED") or line.startswith("error"):
        print(line.rstrip(), flush=True)
print("ALL-DONE", flush=True)
