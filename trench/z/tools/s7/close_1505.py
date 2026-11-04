"""Close the 15:05 Z-lane S7 session: plan note + digest entry."""
hub = '/Users/petecopeland/Repos/.worktrees/z-hub/trench/z/'
p = hub + 'PLAN-z.md'
s = open(p).read()
old = "**15:05 (11-04) Z lane: on it (quadratic sibling walk), same branch.** |"
assert s.count(old) == 1
s = s.replace(old, "**15:50 (11-04) Z lane: walk fixed, #878 @ `5dcee394` (red `852db2a4`), delta R1 asked (comment 6641696427).** `+` reads one element, `~` walks lazily and is memoised per (compound, node) per build/query scope; 3000-sibling pin: all four shapes within 1.0x of control (red 2.8x). Engine lib 1602/0. Waits on R1 delta, then batch. |")
open(p, 'w').write(s)

d = hub + 'digest-z.md'
entry = """
## 2026-11-04 15:50 Z-lane S7 (#878 batch 13 hold: quadratic sibling walk)
Picked S7: in-progress, returned to the lane by Atlas 12:20 with a concrete fix. Open hiwave-macos PRs unchanged (#878 still draft).

- **#878 @ `5dcee394`** (plain push on `atlas/z-s7-checked-sibling`; red `852db2a4`, fix `5dcee394`).
- Before: once a descendant/child step moved the walk to an ancestor, `+`/`~` built the ancestor's whole earlier-sibling list (keys and attribute clones) per subject: O(N^2). Debug pin, 3000 `<li><span>`: `li ~ li span` 2474 ms vs control 884 ms.
- After: `+` reads the one element before via `previous_sibling`; `~` steps back to its nearest match, memoised per (compound address, node id) inside the build/query scope (`WalkState` beside the live checkedness), so `.absent ~ li span` is not rescanned per subject. Pin, control 862 ms: `li ~ li span` 859, `li + li span` 840, `.absent ~ li span` 842, `li ~ li > span` 846. Matching semantics unchanged.
- Runs: whole `rustkit-engine --features headless --lib` 1602 pass / 0 fail / 28 ignored (2082 s, load ~1.8); no new warnings.
- Not run (batch): campaign, A/B, real window.

**For Atlas:** delta R1 asked on #878 (comment 6641696427); the batch can re-run once it clears. The memo keys on the prepared compound's address, which is stable because the rule index / query holds the prepared selector for the whole scope; flag if any path re-prepares selectors mid-build.
Receipts: `receipts/2026-11-04-s7-perf-{body.md,runs.txt}`; apply script + block `tools/s7/`. Worktree removed. Aleph not used (grep, small known area); no lease waits.
"""
open(d, 'a').write(entry)
print('ok')
