#!/usr/bin/env python3
"""t9_runs.py <worktree> <out> [n]: the T9 diagnose runs on yahoo, one wall-clock line each."""
import os
import pathlib
import subprocess
import sys
import time

wt, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
n = int(sys.argv[3]) if len(sys.argv) > 3 else 3
out.mkdir(parents=True, exist_ok=True)
for i in range(1, n + 1):
    start = time.time()
    with open(out / f"run{i}.txt", "w") as f:
        rc = subprocess.run(
            ["python3", str(wt / "scripts/diagnose.py"), "https://www.yahoo.com/",
             "--live-ms", "25000", "--keep", str(out / f"run{i}")],
            stdout=f, stderr=subprocess.STDOUT).returncode
    print(f"run{i} exit={rc} wall={time.time() - start:.0f}s load={os.getloadavg()[0]:.1f}", flush=True)
