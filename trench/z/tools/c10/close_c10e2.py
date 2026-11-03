#!/usr/bin/env python3
"""Close the 11-03 09:05 Z-lane slot: C10 row back to open with #871's head, digest entry."""
hub = "/Users/petecopeland/Repos/.worktrees/z-hub/trench/z/"
p = hub + "PLAN-z.md"
s = open(p).read()
old = ("| Z lane | Prometheus | any non-author | in-progress | 09:20 (11-03) Z lane: session started on (e) "
       "replaced boxes in flex/grid (#869 skip list), new branch off develop 6090c1eb; #869 untouched. ")
assert s.count(old) == 1
new = ("| Z lane | Prometheus | any non-author | open | 10:15 (11-03) Z lane: **(e) replaced boxes in grid is draft "
       "#871 @ f79319a5** (red 5466ec03: 27 of 33 Chromium 143 rows wrong on develop 6090c1eb; fix grid.rs only: "
       "replaced sizing in the area, start alignment for `normal`, Phase 9 records the image height so 9.5 stops "
       "shrinking the row to 0, row contribution at the column width, percentage width compressible, an image "
       "grandchild with a % width re-sized against the item; 24 in-scope rows all match, card grids included). "
       "Narrow runs only; full gates in batch, expect card-grid movers. Left of (e): replaced FLEX items keep their "
       "natural height (flex.rs, after #869); `<canvas>` has no natural size anywhere (0x0 in block flow too); an "
       "author `height:auto` loses to `height=` (block flow too). ")
s = s.replace(old, new)
open(p, "w").write(s)

d = hub + "digest-z.md"
entry = """
## 2026-11-03 10:15 Z-lane C10 (e) replaced boxes in grid

**Row choice:** the CSS-week note (10-30 22:40) parks I0, D0, D1 and B0 until 11-07, so this slot took the first open C row, C10, and its next item: the replaced half of (e) that #869 skipped. I0's Z-lane items are all on develop anyway: (a) #730 content thread, (b) #693 input queue, (d) H9 in #564, (e) `webview-fallback` removed in 9a0c9050; only (c) (cloud) is left. The row can be closed when the parking ends. There is still no 'PETE'S HAND TEST' CONSEQUENCE line in the plan.

**Before -> after:** an `<img>` grid item on develop 6090c1eb was stretched across its area and its row shrank to 0 (40x20 image: 400x0; `width:100%` in a 200px column: 400x0; a card's `width:100%` image: 400x200 in a 200px column). Now draft **#871** @ `f79319a5` (branch `atlas/z-c10e-replaced`, base 6090c1eb). Red `5466ec03`: **27 of 33** Chromium 143.0.7499.4 rows wrong. Fix (grid.rs only): **all 24 in-scope rows match**, card grids included. Open hiwave-macos PRs: 6 of 8.

**Gates, narrow (batch trial):** replaced_ratio 1/0, layout 881/0, engine `grid` 36/0, `image` 52/0, `nested_layout_matrix` 1/0, `aspect` 3/0. Campaign, A/B, full suite and app build owed in the batch. Expect movers on any page with an image grid item.

**Not fixed, in the test's skip list (wrong on develop too, block-flow controls confirm two of them):**
- Replaced flex items keep their natural height when the flexed or stretched width changes (img in a flex column 100x20 vs 100x50). flex.rs: after #869, so two PRs don't touch one file.
- `<canvas>` has no natural size anywhere: 0x0 in block flow, Chromium 300x150. The box builder makes it an empty inline box.
- An author `height: auto` loses to the `height=` attribute (400x20 vs 400x200 in block flow).

**For Atlas:** (1) #871 reads the engine's default `stretch` as `normal` for replaced items, so an image the page explicitly stretches keeps its own size. Chromium stretches it. Accept, or fund a `normal` keyword. (2) Stop rule: this is the second straight C10 session without a landed receipt (#869, #871 are both batch drafts). The lane can't land; if the next slot still has none, C10 goes blocked by the rule. Do you want the batch trial to count as "landed" when the batch lands?

**Time:** about 30 min of the slot waited on the lease: Atlas's batch-7 engine suite, then another lane's release parity-capture build. One 20-min background run was killed before it got the lease.

**Tools:** `tools/c10/replaced_ratio_probe.mjs`, `replaced_ratio_gen.py`, `replaced_ratio_skip.txt`, `replaced_gates.py`. Receipts: `receipts/2026-11-03-c10e2-body.md`, `2026-11-03-c10e2-runs.txt`. Worktree z-c10e-replaced removed. Aleph and Null not used; reading was by grep. The three untracked `tools/c2/` files are still uncommitted (not this session's).
"""
open(d, "a").write(entry)
print("ok")
