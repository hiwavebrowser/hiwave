#!/usr/bin/env python3
"""add_through.py: replace the THROUGH table in float_margin_tests.rs with empty_through_probe.mjs's current output."""
import re, subprocess

W = "/Users/petecopeland/Repos/.worktrees/"
out = subprocess.run(["node", W + "z-hub/trench/z/tools/c10/empty_through_probe.mjs", W + "z-c12-opacity/tools/parity_oracle"],
                     capture_output=True, text=True, check=True).stdout
rows = "\n".join(l for l in out.splitlines() if not l.startswith("//"))
P = W + "z-c10a/crates/rustkit-engine/src/float_margin_tests.rs"
s = open(P).read()
s, n = re.subn(r"(const THROUGH: &\[\(&str, &str, &str\)\] = &\[\n).*?(\n\];)", lambda m: m.group(1) + rows + m.group(2), s, flags=re.S)
assert n == 1
open(P, "w").write(s)
print(rows.count("\n") + 1, "rows")
