"""absum.py <ab table>: wall-clock A vs B over the sites with no failed capture, and the sites whose
across-arm difference exceeds both within-arm differences (pixel movers)."""
import re, sys
A = B = 0.0
clean, movers, dropped = [], [], []
for line in open(sys.argv[1]):
    site = line.split()[0]
    secs = [float(x) for x in re.search(r"secs A,B,A,B ([\d.,]+)", line).group(1).split(",")]
    if "failed: 0" not in line:
        dropped.append(site)
        continue
    clean.append(site)
    A += secs[0] + secs[2]
    B += secs[1] + secs[3]
    wa, wb = (float(x) for x in re.search(r"within A ([\d.]+)%  within B ([\d.]+)%", line).groups())
    across = [float(x) for x in re.search(r"across ([\d.]+)% ([\d.]+)% ([\d.]+)% ([\d.]+)%", line).groups()]
    if min(across) > max(wa, wb):
        movers.append(site)
print(f"clean {len(clean)} sites: A {A:.1f} s, B {B:.1f} s, B/A {B / A:.3f}")
print("dropped (a failed capture):", ", ".join(dropped) or "none")
print("pixel movers (every across pair above both within-arm diffs):", ", ".join(movers) or "none")
