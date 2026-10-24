#!/usr/bin/env python3
"""Run the rustkit-engine headless lib suite N times in a row (T5 acceptance).
    suite3.py <worktree> <log-prefix> [runs=3]
Writes <log-prefix>-<i>.log per run and <log-prefix>.done with one summary line per run.
"""
import re, subprocess, sys, time
wt, prefix = sys.argv[1], sys.argv[2]
runs = int(sys.argv[3]) if len(sys.argv) > 3 else 3
summary = []
for i in range(1, runs + 1):
    t0 = time.time()
    log = f"{prefix}-{i}.log"
    with open(log, "w") as f:
        rc = subprocess.run(
            ["python3", "/Users/petecopeland/Repos/.worktrees/z-cargo.py", wt,
             "test", "-p", "rustkit-engine", "--features", "headless", "--lib"],
            stdout=f, stderr=subprocess.STDOUT).returncode
    text = open(log, errors="replace").read()
    results = re.findall(r"test result: .*", text)
    failed = re.findall(r"^test (\S+) \.\.\. FAILED", text, re.M)
    line = f"run {i}: rc={rc} {int(time.time() - t0)}s {results[-1] if results else 'no result'} failed={failed}"
    summary.append(line)
    print(line, flush=True)
open(f"{prefix}.done", "w").write("\n".join(summary) + "\n")
