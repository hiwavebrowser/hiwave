#!/usr/bin/env python3
"""Run the rustkit-engine headless lib suite N times in a row (T5 acceptance).
    suite3.py <worktree> <log-prefix> [runs=3]
Writes <log-prefix>-<i>.log per run and <log-prefix>.done with one summary line per run.
"""
import os, re, subprocess, sys, threading, time
wt, prefix = sys.argv[1], sys.argv[2]
loads = []
def sample():
    while True:
        loads.append(os.getloadavg()[0])
        time.sleep(30)
threading.Thread(target=sample, daemon=True).start()
runs = int(sys.argv[3]) if len(sys.argv) > 3 else 3
summary = []
for i in range(1, runs + 1):
    t0 = time.time()
    loads.clear()
    log = f"{prefix}-{i}.log"
    with open(log, "w") as f:
        rc = subprocess.run(
            ["python3", "/Users/petecopeland/Repos/.worktrees/z-cargo.py", wt,
             "test", "-p", "rustkit-engine", "--features", "headless", "--lib"],
            stdout=f, stderr=subprocess.STDOUT).returncode
    text = open(log, errors="replace").read()
    results = re.findall(r"test result: .*", text)
    failed = re.findall(r"^test (\S+) \.\.\. FAILED", text, re.M)
    load = f"load1 min/median/max {min(loads):.1f}/{sorted(loads)[len(loads) // 2]:.1f}/{max(loads):.1f}" if loads else "load n/a"
    line = f"run {i}: rc={rc} {int(time.time() - t0)}s {load} {results[-1] if results else 'no result'} failed={failed}"
    summary.append(line)
    print(line, flush=True)
open(f"{prefix}.done", "w").write("\n".join(summary) + "\n")
