"""owed.py: names in the built binary with no result in suite.log -> owed.txt; print counts."""
import re, subprocess
S = "/Users/petecopeland/Repos/.worktrees/scratch-e29b/"
BIN = '/Users/petecopeland/Repos/.worktrees/z-ch2-e29b/target/debug/deps/rustkit_engine-0bcc04c2cb80b63e'
out = subprocess.run([BIN, '--list'], capture_output=True, text=True,
                     cwd='/Users/petecopeland/Repos/.worktrees/z-ch2-e29b/crates/rustkit-engine').stdout
names = [l[:-len(': test')] for l in out.split('\n') if l.endswith(': test')]
txt = open(S + "suite.log", errors="replace").read()
done = dict(re.findall(r"^test (\S+) \.\.\. (ok|FAILED|ignored)", txt, re.M))
rer = open(S + "rerun1-1t.log", errors="replace").read()
rdone = dict(re.findall(r"^test (\S+) \.\.\. (ok|FAILED|ignored)", rer, re.M))
owed = [n for n in names if n not in done]
open(S + "owed.txt", "w").write("\n".join(owed) + "\n")
fails = [n for n, r in done.items() if r == "FAILED"]
print("binary tests", len(names), "ran", len(done), "ok", sum(r == "ok" for r in done.values()),
      "ignored", sum(r == "ignored" for r in done.values()), "failed", len(fails), "owed", len(owed))
print("1-thread rerun of fails: ok", sum(rdone.get(f) == "ok" for f in fails), "failed",
      sum(rdone.get(f) == "FAILED" for f in fails), "not reached", [f for f in fails if f not in rdone])
