"""three_arms.py <worktree> <rounds> [profile=parity]: the T8 gate receipt.

The engine's ignored two_heavy_tabs_receipt test (cnn + yahoo loading at once
in one process) under three arms, interleaved per round (ABCABC..., never
AAA..BBB..): HIWAVE_NET_RUNTIME=0 (page-polled), HIWAVE_NET_WORKERS=1 (T7a's
one thread), HIWAVE_NET_WORKERS=2. Built with --profile <profile> through
z-cargo.py. Prints each arm's receipt lines with the round, plus `uptime` per
round so a round under load > 8 can be re-run, not dropped silently."""
import os
import subprocess
import sys

wt, rounds = sys.argv[1], int(sys.argv[2])
profile = sys.argv[3] if len(sys.argv) > 3 else "parity"
ARMS = {"off": {"HIWAVE_NET_RUNTIME": "0"}, "w1": {"HIWAVE_NET_WORKERS": "1"}, "w2": {"HIWAVE_NET_WORKERS": "2"}}
for rnd in range(1, rounds + 1):
    print(f"round {rnd} load {subprocess.run(['uptime'], capture_output=True, text=True).stdout.strip()}", flush=True)
    for arm, extra in ARMS.items():
        env = dict(os.environ)
        env.pop("HIWAVE_NET_RUNTIME", None)
        env.pop("HIWAVE_NET_WORKERS", None)
        env.update(extra)
        r = subprocess.run(["python3", "/Users/petecopeland/Repos/.worktrees/z-cargo.py", wt, "test", "--profile", profile,
                            "-p", "rustkit-engine", "--features", "headless", "--lib", "--",
                            "two_heavy_tabs_receipt", "--ignored", "--nocapture"],
                           env=env, capture_output=True, text=True)
        for line in (r.stdout + r.stderr).splitlines():
            if "two tabs" in line or "test result" in line or "panicked" in line:
                print(f"round {rnd} arm {arm}: {line}", flush=True)
