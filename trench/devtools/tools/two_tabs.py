"""two_tabs.py <worktree> <rounds>: the engine's ignored two_heavy_tabs_receipt
test (cnn + yahoo loading at once in one process), HIWAVE_NET_RUNTIME on vs =0,
arms interleaved, through z-cargo.py. Prints the test's receipt lines."""
import os
import subprocess
import sys

wt, rounds = sys.argv[1], int(sys.argv[2])
for _ in range(rounds):
    for arm in ("on", "0"):
        env = dict(os.environ)
        env.pop("HIWAVE_NET_RUNTIME", None)
        if arm == "0":
            env["HIWAVE_NET_RUNTIME"] = "0"
        r = subprocess.run(["python3", "/Users/petecopeland/Repos/.worktrees/z-cargo.py", wt, "test", "-p", "rustkit-engine",
                            "--features", "headless", "--lib", "--", "two_heavy_tabs_receipt", "--ignored", "--nocapture"],
                           env=env, capture_output=True, text=True)
        for line in (r.stdout + r.stderr).splitlines():
            if "two tabs" in line or "test result" in line or "panicked" in line:
                print(line, flush=True)
