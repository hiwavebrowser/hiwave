#!/usr/bin/env python3
"""serial_bin.py <worktree> <log> <filter>: the worktree's newest built engine test binary, one thread, from the crate dir.
The GPU guard times out at high load in a parallel run, so a red count needs this. Prints counts, failures and their first assert lines."""
import glob
import os
import re
import subprocess
import sys

wt, log, flt = sys.argv[1], sys.argv[2], sys.argv[3]
bins = [p for p in glob.glob(wt + "/target/debug/deps/rustkit_engine-*") if os.access(p, os.X_OK) and not os.path.splitext(p)[1]]
binary = max(bins, key=os.path.getmtime)
print("bin", os.path.basename(binary), flush=True)
with open(log, "w") as f:
    rc = subprocess.run([binary, flt, "--test-threads=1"], cwd=wt + "/crates/rustkit-engine", stdout=f, stderr=subprocess.STDOUT).returncode
print("rc", rc)
text = open(log, errors="replace").read()
print("guard timeouts", text.count("to finish with the GPU"))
for block in re.split(r"(?m)^---- ", text)[1:]:
    lines = block.splitlines()
    print(lines[0].split(" stdout")[0], "|", " / ".join(l[:150] for l in lines[2:7] if l.strip()))
for line in text.splitlines():
    if line.startswith("test result"):
        print(line)
print("SERIAL-DONE")
