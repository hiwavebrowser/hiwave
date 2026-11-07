"""progress.py <log>: chunks started, ok / failed / ignored counts, failed names, done flag."""
import re
import sys
import time

s = open(sys.argv[1]).read()
ok = len(re.findall(r" \.\.\. ok$", s, re.M))
ign = len(re.findall(r" \.\.\. ignored", s, re.M))
failed = re.findall(r"^test (\S+) \.\.\. FAILED$", s, re.M)
print("chunks", s.count("### chunk"), "ok", ok, "ignored", ign, "failed", len(failed),
      "done", "### runlist done" in s, time.strftime("%H:%M"))
for f in failed:
    print("  FAILED", f)
