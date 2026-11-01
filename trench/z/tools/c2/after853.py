#!/usr/bin/env python3
"""after853.py <seq output file> <base sha>: wait for SEQ-DONE, then #851's full gates. Ends AFTER-DONE."""
import subprocess
import sys
import time

W = "/Users/petecopeland/Repos/.worktrees/"
T = W + "z-hub/trench/z/tools/"
seq, base = sys.argv[1], sys.argv[2]
while "SEQ-DONE" not in open(seq, errors="replace").read():
    time.sleep(20)
subprocess.run(["python3", T + "c10/gates.py", W + "z-c2d-g", base, "c2dg"])
print("AFTER-DONE", flush=True)
