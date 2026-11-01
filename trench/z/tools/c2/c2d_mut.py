#!/usr/bin/env python3
"""Show the transform tests catch the bug R1 named: run them with transformed_rect taking no sticky shift, then restore."""
import subprocess

WT = "/Users/petecopeland/Repos/.worktrees/z-c2d-rework"
P = WT + "/crates/rustkit-bindings/src/dom.rs"
orig = open(P).read()
old = "*c = (tx + shifts[i].0, ty + shifts[i].1);"
assert orig.count(old) == 1
open(P, "w").write(orig.replace(old, "let _ = i; *c = (tx, ty);"))
try:
    subprocess.call(
        ["python3", "/Users/petecopeland/Repos/.worktrees/z-hub/trench/z/tools/c10/ct.py", WT, "mutated.txt", "test", "-p", "rustkit-engine", "--lib", "--features", "headless", "--", "sticky_scroll_tests"]
    )
finally:
    open(P, "w").write(orig)
print("restored")
