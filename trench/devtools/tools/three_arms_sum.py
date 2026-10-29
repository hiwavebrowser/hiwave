"""three_arms_sum.py <three_arms log>: per page, each arm's median load time, and
the paired per-round diffs w2-w1 and w2-off (median, min, max), plus the load
average each round started under."""
import re
import statistics
import sys

times = {}  # (round, arm, page) -> seconds
loads = {}
for line in open(sys.argv[1]):
    m = re.match(r"round (\d+) load .*load averages: ([\d.]+)", line)
    if m:
        loads[int(m.group(1))] = float(m.group(2))
    m = re.match(r"round (\d+) arm (\w+): two tabs .*https://www\.(\w+)\.com/ load complete ([\d.]+) s", line)
    if m:
        times[(int(m.group(1)), m.group(2), m.group(3))] = float(m.group(4))
rounds = sorted({r for r, _, _ in times})
print(f"rounds {len(rounds)}; load at round start: " + ", ".join(f"{loads.get(r, '?')}" for r in rounds))
for page in ("cnn", "yahoo"):
    print(f"\n{page}")
    for arm in ("off", "w1", "w2"):
        xs = [times[(r, arm, page)] for r in rounds if (r, arm, page) in times]
        print(f"  {arm:3} median {statistics.median(xs):.2f} s  (n={len(xs)}, {min(xs):.1f}-{max(xs):.1f})")
    for a, b in (("w2", "w1"), ("w2", "off"), ("w1", "off")):
        d = [times[(r, a, page)] - times[(r, b, page)] for r in rounds if (r, a, page) in times and (r, b, page) in times]
        base = statistics.median([times[(r, b, page)] for r in rounds if (r, b, page) in times])
        print(f"  {a}-{b}: paired median {statistics.median(d):+.2f} s ({statistics.median(d) / base * 100:+.1f}%), "
              f"spread {min(d):+.2f}..{max(d):+.2f} s")
