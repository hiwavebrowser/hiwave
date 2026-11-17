"""Run the tests the cut full-lib log never reached, by exact name, on the same binary."""
import re, subprocess, sys

W = "/Users/petecopeland/Repos/.worktrees/dt-t32-0647"
BIN = W + "/target/debug/deps/rustkit_engine-2c1af477a349a063"
log = open(W + "/full-lib.log", errors="replace").read()
seen = set(re.findall(r"^test (\S+) \.\.\. ", log, re.M))
listed = subprocess.run([BIN, "--list"], capture_output=True, text=True, cwd=W + "/crates/rustkit-engine").stdout
names = [l[: -len(": test")] for l in listed.splitlines() if l.endswith(": test")]
rest = [n for n in names if n not in seen]
print(f"listed {len(names)} seen {len(seen)} rest {len(rest)}", flush=True)
out = open(W + "/rest-lib.log", "w")
p = subprocess.run([BIN, "--exact", *rest], stdout=out, stderr=subprocess.STDOUT, cwd=W + "/crates/rustkit-engine")
out.close()
t = open(W + "/rest-lib.log", errors="replace").read()
print("rc", p.returncode, "guard", t.count("GPU test guard: waited"))
print(re.findall(r"test result:.*", t))
print([n for n, s in re.findall(r"^test (\S+) \.\.\. (\w+)", t, re.M) if s == "FAILED"])
