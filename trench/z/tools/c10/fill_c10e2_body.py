#!/usr/bin/env python3
"""Fill the C10(e) replaced-slice PR body placeholders."""
import subprocess

tc = subprocess.run(["rustc", "--version"], capture_output=True, text=True,
                    cwd="/Users/petecopeland/Repos/.worktrees/z-c10e-replaced").stdout.strip()
p = "/Users/petecopeland/Repos/.worktrees/z-hub/trench/z/receipts/2026-11-03-c10e2-body.md"
s = open(p).read()
rep = {
    "@@ROWS@@": "33",
    "@@RED@@": "27 of 33",
    "@@FIX@@": "`f79319a5`",
    "@@AFTER@@": (
        "0 of the 24 in-scope rows wrong: every `<img>` grid row and both card patterns "
        "(a `<div>` in a `1fr` column holding a `width:100%` image, with and without "
        "`aspect-ratio: 16/9; object-fit: cover`) match Chromium. 13 rows moved to the skip list "
        "(below). Two block-flow controls were added to the probe to confirm canvas and the "
        "`height=` attribute are wrong outside grid too: `canvas block: none` 0x0 vs 300x150; "
        "`img block: width 100%, height auto attrs` 400x20 vs 400x200."
    ),
    "@@GATES@@": (
        "at f79319a5, debug, through z-cargo.py: `replaced_ratio` 1/0; rustkit-layout --lib 881/0 "
        "(13 ignored); engine headless `grid` 36/0, `image` 52/0, `nested_layout_matrix` 1/0, "
        "`aspect` 3/0. Not run: full engine headless suite, campaign, 20-site A/B, app build."
    ),
    "@@HEAD@@": "`f79319a5`",
    "@@TC@@": tc,
}
for k, v in rep.items():
    s = s.replace(k, v)
open(p, "w").write(s)
print("left:", [k for k in rep if k in s], tc)
