#!/usr/bin/env python3
"""ct.py <worktree> <log name> <cargo args...>: run cargo through the lease, log to <worktree>/scratch/<log>, print result lines."""
import os
import re
import subprocess
import sys

wt, log = sys.argv[1], sys.argv[2]
args = sys.argv[3:]
os.makedirs(f"{wt}/scratch", exist_ok=True)
path = f"{wt}/scratch/{log}"
with open(path, "w") as f:
    rc = subprocess.call(
        ["python3", "/Users/petecopeland/Repos/.worktrees/z-cargo.py", wt] + args,
        stdout=f,
        stderr=subprocess.STDOUT,
    )
text = open(path, errors="replace").read()
for line in text.splitlines():
    if re.match(r"^test .*(FAILED|failed)$", line) or line.startswith("test result") or line.startswith("error") or re.match(r"^\s+Running ", line):
        print(line[:300])
for m in re.finditer(r"---- (\S+) stdout ----\n(.*?)(?=\n\n)", text, re.S):
    print(m.group(1), "::", m.group(2)[:700])
print("rc", rc)
