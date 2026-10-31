#!/usr/bin/env python3
"""CA1-2 red commit: register flex_shorthand_tests, correct its row comment, add three table rows."""
wt = "/Users/petecopeland/Repos/.worktrees/z-ca1-2/crates/rustkit-engine/src/"
p = wt + "flex_shorthand_tests.rs"
s = open(p).read()
old = """/// refuses to shrink, a lone length is a basis that still grows. Chromium
/// 143: `a:0,100 b:100,500 c:600,300` in the first row, `d:0,500` and
/// `e:500,500` overflowing the second, `f:0,200 g:200,200` in the third.
"""
new = """/// refuses to shrink, a lone length is a basis that still grows. The expected
/// string is Chromium 143 on this page (`flex_row_probe.mjs`).
"""
assert old in s
s = s.replace(old, new)
old = """        ("initial", (0.0, 1.0, Auto)),
"""
new = """        ("initial", (0.0, 1.0, Auto)),
        ("unset", (0.0, 1.0, Auto)),
"""
assert old in s
s = s.replace(old, new)
old = """        ("2 3 auto", (2.0, 3.0, Auto)),
"""
new = """        ("2 3 auto", (2.0, 3.0, Auto)),
        ("1e1", (10.0, 1.0, Percent(0.0))),
        ("+1", (1.0, 1.0, Percent(0.0))),
        (".5 10px", (0.5, 1.0, Length(10.0))),
"""
assert old in s
s = s.replace(old, new)
open(p, "w").write(s)

p = wt + "lib.rs"
s = open(p).read()
old = """#[cfg(all(test, feature = "headless"))]
mod box_sizing_inherit_tests;
"""
new = """#[cfg(all(test, feature = "headless"))]
mod box_sizing_inherit_tests;
#[cfg(all(test, feature = "headless"))]
mod flex_shorthand_tests;
"""
assert s.count(old) == 1
s = s.replace(old, new)
open(p, "w").write(s)
