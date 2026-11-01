#!/usr/bin/env python3
"""#851 finding 4: a sticky box painted over a held fixed box wins the hit test."""
P = "/Users/petecopeland/Repos/.worktrees/z-c2d-rework/crates/rustkit-layout/src/lib.rs"
s = open(P).read()
old = """        match top {
            Some((z_index, hit)) if z_index >= 0 => Some(hit),
            Some((_, hit)) => page().or(Some(hit)),
            None => page(),
        }
    }
"""
new = """        match top {
            Some((z_index, hit)) if z_index >= 0 => {
                // Pages with no sticky box pay for nothing here.
                if !self.sticky_paths.borrow().is_empty() {
                    if let Some(over) = page().filter(|p| self.sticky_is_over(p, z_index, &hit)) {
                        return Some(over);
                    }
                }
                Some(hit)
            }
            Some((_, hit)) => page().or(Some(hit)),
            None => page(),
        }
    }

    /// Whether the page's hit `page` is in a sticky box painted over the held
    /// fixed box `fixed` with this `z-index`: one with a higher `z-index`, or
    /// the same one later in the tree. A sticky box is positioned, so the page
    /// can be over a fixed box, and it moves to where the fixed box is.
    fn sticky_is_over(&self, page: &HitTestResult, z_index: i32, fixed: &HitTestResult) -> bool {
        let (Some(page_node), Some(fixed_node)) = (page.node_id, fixed.node_id) else {
            return false;
        };
        let Some(fixed_path) = self.path_to_node(fixed_node) else {
            return false;
        };
        self.sticky_paths.borrow().iter().any(|path| {
            let Some(sticky) = path.iter().try_fold(self, |at, &index| at.children.get(index)) else {
                return false;
            };
            let z = sticky.style.z_index;
            (z > z_index || (z == z_index && path.as_slice() > fixed_path.as_slice()))
                && !fixed_path.starts_with(path)
                && sticky.path_to_node(page_node).is_some()
        })
    }

    /// The child indices from this box to the first box of `node`.
    fn path_to_node(&self, node: usize) -> Option<Vec<usize>> {
        if self.node_id == Some(node) {
            return Some(Vec::new());
        }
        self.children.iter().enumerate().find_map(|(index, child)| {
            let mut path = child.path_to_node(node)?;
            path.insert(0, index);
            Some(path)
        })
    }
"""
assert s.count(old) == 1
s = s.replace(old, new)
open(P, "w").write(s)
print("ok")
