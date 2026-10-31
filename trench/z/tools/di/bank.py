#!/usr/bin/env python3
"""Bank the 21:05 session's small text receipts on the hub. Frames stay behind and die with the worktrees."""
import pathlib
W = pathlib.Path("/Users/petecopeland/Repos/.worktrees")
R = W / "z-hub/trench/z/receipts"
D = "2026-10-30-"
pairs = [
    ("z-di/scratch/final-body-di.md", "di-pr.md"),
    ("z-di/scratch/ab-di.txt", "di-ab.txt"),
    ("z-di/scratch/ab-di-swap.txt", "di-ab-swap.txt"),
    ("z-di/scratch/ab-di-swap2.txt", "di-ab-swap2.txt"),
    ("z-ca1-2/scratch/final-body-ca12.md", "ca12-pr.md"),
    ("z-ca1-2/scratch/ab-ca12.txt", "ca12-ab.txt"),
    ("z-ca1-2/scratch/ab-ca12-r.txt", "ca12-ab-r.txt"),
    ("z-ca1-2/scratch/ab-ca12-swap.txt", "ca12-ab-swap.txt"),
    ("z-ca1-2/scratch/ab-ca12-swap2.txt", "ca12-ab-swap2.txt"),
    ("z-ca1-2/scratch/ab-ca12-long.txt", "ca12-ab-long.txt"),
    ("z-ca1-2/scratch/ab-ca12-li1.txt", "ca12-ab-li1.txt"),
    ("z-ca1-2/scratch/ab-ca12-li2.txt", "ca12-ab-li2.txt"),
    ("z-ca1-2/scratch/ab-ca12-li3.txt", "ca12-ab-li3.txt"),
]
for src, dst in pairs:
    (R / (D + dst)).write_bytes((W / src).read_bytes())


def results(path):
    keep = []
    for l in (W / path).read_text(errors="replace").splitlines():
        if l.startswith(("===", "test result", "failures:", "    ")) or " rc=" in l or "FAILED" in l:
            keep.append(l[:200])
    return "\n".join(keep) + "\n"


(R / (D + "di-suite-ec8ee96c.txt")).write_text(results("z-di/suite.log"))
(R / (D + "ca12-suite-c2693048.txt")).write_text(results("z-ca1-2/suite.log"))
log = (W / "z-dev-c25c1d71/devcheck.log").read_text(errors="replace")
(R / (D + "dev-c25c1d71-suites.txt")).write_text(log[log.index("--- SUMMARY"):])
print("banked", len(pairs) + 3)
