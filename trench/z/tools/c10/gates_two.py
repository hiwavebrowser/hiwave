#!/usr/bin/env python3
"""gates_two.py: gates.py for #851's and #853's reworks, one after the other, against develop e5e0fd97. Ends TWO-DONE."""
import subprocess

W = "/Users/petecopeland/Repos/.worktrees/"
T = W + "z-hub/trench/z/tools/"
for wt, tag in ((W + "z-c2d-rework", "c2d2"), (W + "z-c10b2-r1", "c10b2r1")):
    print("START", tag, flush=True)
    subprocess.run(["python3", T + "c10/gates.py", wt, "e5e0fd97", tag])
    subprocess.run(["python3", T + "c10/rep_fix.py", wt, tag, "google", "linkedin", "bing", "netflix"])
    print("DONE", tag, flush=True)
print("TWO-DONE", flush=True)
