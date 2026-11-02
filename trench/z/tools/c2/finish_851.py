#!/usr/bin/env python3
"""finish_851.py: the 07:30 order. Red at e3dc36b2 in its own worktree and target, green at the head, census pins,
then c10/gates.py against develop afa159da (campaigns, A/B, crates, suites). Ends FINISH-DONE."""
import subprocess

W = "/Users/petecopeland/Repos/.worktrees/"
ZC = W + "z-cargo.py"
T = W + "z-hub/trench/z/tools/"
C = W + "z-c2d-finish"
R = W + "z-c2d-red"
BASE = "afa159da4cdcfb41a3bd3cbae78ab7c0aec81665"
STICKY = ["test", "-p", "rustkit-engine", "--features", "headless", "--lib", "sticky_scroll_tests"]


def module(wt, log):
    with open(log, "w") as f:
        rc = subprocess.run(["python3", ZC, wt] + STICKY, stdout=f, stderr=subprocess.STDOUT).returncode
    print(wt, "sticky rc", rc, flush=True)
    for line in open(log):
        if line.startswith("test result") or line.rstrip().endswith("FAILED"):
            print(line.rstrip(), flush=True)


module(R, R + "/red.log")
print("RED-DONE", flush=True)
module(C, C + "/green.log")
print("GREEN-DONE", flush=True)
for wt in (R, C):
    p = subprocess.run(["python3", wt + "/scripts/tests/test_declaration_census.py"], cwd=wt, capture_output=True, text=True)
    print(wt, "census rc", p.returncode, p.stdout[-300:], flush=True)
subprocess.run(["python3", T + "c10/gates.py", C, BASE, "c2d4"])
print("FINISH-DONE", flush=True)
