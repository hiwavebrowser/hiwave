"""Rerun the FAILED tests of a suite log on one thread, by exact name."""
import re, subprocess, sys
log, out = sys.argv[1], sys.argv[2]
s = open(log, errors="replace").read()
fails = re.findall(r"^test (\S+) \.\.\. FAILED$", s, re.M)
print(len(fails), "to rerun")
cmd = ["python3", "/Users/petecopeland/Repos/.worktrees/z-cargo.py", "/Users/petecopeland/Repos/.worktrees/z-ch2-e37",
       "test", "-p", "rustkit-engine", "--features", "headless", "--lib", "--", "--exact", "--test-threads=1"] + fails
with open(out, "w") as f:
    subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)
t = open(out, errors="replace").read()
r = re.findall(r"^test (\S+) \.\.\. (ok|FAILED)$", t, re.M)
print(sum(1 for x in r if x[1] == "ok"), "ok;", [x[0] for x in r if x[1] == "FAILED"])
for line in t.splitlines():
    if "test result" in line:
        print(line)
