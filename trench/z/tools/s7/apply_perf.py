"""S7 batch 13 hold: swap the eager sibling list for a lazy memoised walk.
Usage: python3 apply_perf.py <worktree>"""
import sys

wt = sys.argv[1]
p = wt + '/crates/rustkit-engine/src/lib.rs'
s = open(p).read()
start = s.index("thread_local! {\n    /// The checkedness that has left the `checked` attribute")
end = s.index("/// Keeps [`HAS_MEMO`] for one build.")
new = open(wt.rstrip('/') + '/../z-hub/trench/z/tools/s7/walk_block.rs').read() if False else open(sys.argv[2]).read()
s = s[:start] + new + s[end:]
old_q = "let _walk_checked = (!checked.is_empty()).then(|| WalkCheckedScope::enter(checked.clone()));"
assert s.count(old_q) == 1
s = s.replace(old_q, "let _walk_checked = WalkCheckedScope::enter((!checked.is_empty()).then(|| checked.clone()));")
s = s.replace("checkedness (`dom_earlier_siblings`).", "checkedness (`dom_sibling_key`).")
open(p, 'w').write(s)
p2 = wt + '/crates/rustkit-engine/src/layout_ctx.rs'
t = open(p2).read()
assert t.count("crate::WalkCheckedScope::enter(checked);") == 1
t = t.replace("crate::WalkCheckedScope::enter(checked);", "crate::WalkCheckedScope::enter(Some(checked));")
open(p2, 'w').write(t)
for name in ("dom_earlier_siblings", "WALK_CHECKED"):
    print(name, s.count(name))
