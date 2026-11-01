#!/usr/bin/env python3
"""#851 finding 5: stamp_sticky_shifts stops taking shifts from above at a fixed box, as the rect read's chain does."""
P = "/Users/petecopeland/Repos/.worktrees/z-c2d-rework/crates/rustkit-layout/src/lib.rs"
s = open(P).read()
old = """            let (mut at, mut above, mut scroller) = (self, (0.0, 0.0), None);
            for &index in path {
                let shift = at.sticky_shift.get();
                above = (above.0 + shift.0, above.1 + shift.1);
                if at.is_element_scroller() {
                    above = (0.0, 0.0);
                    scroller = at.node_id.map(|node| (node, at.element_scroll.get()));
                }
"""
new = """            let (mut at, mut above, mut scroller) = (self, (0.0, 0.0), None);
            // What a fixed box starts from: only what moves its containing
            // block, a transform, moves it.
            let mut at_transform = (0.0, 0.0);
            for &index in path {
                if at.position == Position::Fixed {
                    above = at_transform;
                }
                let shift = at.sticky_shift.get();
                above = (above.0 + shift.0, above.1 + shift.1);
                if at.is_element_scroller() {
                    above = (0.0, 0.0);
                    scroller = at.node_id.map(|node| (node, at.element_scroll.get()));
                }
                if !at.style.effective_transform().is_identity() {
                    at_transform = above;
                }
"""
assert s.count(old) == 1
s = s.replace(old, new)
open(P, "w").write(s)
print("ok")
