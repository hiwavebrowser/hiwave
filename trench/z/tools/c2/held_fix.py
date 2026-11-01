#!/usr/bin/env python3
"""`held` keys on what is a containing block for fixed boxes, of what the engine parses: a transform or a filter."""
P = "/Users/petecopeland/Repos/.worktrees/z-c2d-rework/crates/rustkit-engine/src/lib.rs"
s = open(P).read()
for old, new in [
    (
        """        /// which holds a fixed box to the page.
        held: bool,
        transformed: bool,
""",
        """        /// which holds a fixed box to the page. So does a filter. Chromium's
        /// other such properties (`will-change`, `contain`, `perspective`,
        /// `backdrop-filter`) are not parsed here.
        held: bool,
        holds_fixed: bool,
""",
    ),
    ("(b.position == Position::Fixed && !scrollers.transformed)", "(b.position == Position::Fixed && !scrollers.holds_fixed)"),
    ("            transformed: scrollers.transformed || transformed,\n", "            holds_fixed: scrollers.holds_fixed || transformed || !b.style.filter.is_empty(),\n"),
    ("held: false, transformed: false };", "held: false, holds_fixed: false };"),
]:
    assert s.count(old) == 1, old
    s = s.replace(old, new)
open(P, "w").write(s)
print("ok")
