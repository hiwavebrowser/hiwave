# T35 — chrome board: join failures as a column, named by selector

Branch `atlas/dt-t35-join-column` @ e9512d87 (red 41892d9e, fix e9512d87), base develop 83b46110. Tooling only: `scripts/chrome_board.py` and `scripts/tests/test_chrome_board.py`. No engine change. **No PR yet: PR cap (40 open, cap 8). This file is the PR body.**

## The row's question, answered on macOS at develop 83b46110

Talos (11-09) read the 11-05 board.json: macOS failed to join 8–10 more elements than Linux (sidebar_collapsed 1024x700: 11 vs 3), so macOS geometry might be under-counted. One macOS layout-oracle run (the full 42-row board, parity build of 83b46110, `dump_joins.py` over the work dir) says:

- **The chrome page now has 0 join failures at every state and size** (it had 8–13 on 11-05). Geometry diffs on the chrome page fell from 210–238 to 3–22. The Mac-vs-Linux join gap Talos saw is gone on the Mac side. The Linux side was not re-run; this seat has no Linux host.
- **9 rows still have join failures, all `missing_box`, all real elements**:
  - inspector default ×3 sizes: 7 each. Every one is an **empty `<span class="unit"></span>`** inside the computed-styles value (`rgb(<number>, <number>, <number>)`). Chromium's rect is 0×14 at the right x. RustKit makes no box for an empty inline; the following text starts exactly where Chromium put the span (1039.21 vs 1039.23).
  - report default/weekly ×3 sizes: 1 each. This is the **empty `<div id="error-container">`** (Chromium 1200×0). RustKit emits no box for it.
- So the join in the scorer is right, and **nothing in the join needed fixing**. These are honest missing boxes from an engine behaviour: an empty element gets no layout box. That is a Z-lane observation, not a scorer bug. It moves no pixel today, and an `elementFromPoint`/`getBoundingClientRect` on those elements would differ from Chromium.
- **Is the green count generous?** No. `green_rule` already refuses the geometry rule when `join_failures > 0`. All 9 rows with joins are green on the pixel rule (≤ 0.5 %), which does not read geometry. Join failures move no verdict on today's board.

## Change

- `compare_geometry` returns `join_detail`: one `{kind, selector}` per non-delta failure (missing, ambiguous, phantom, no_border_box, missing_axis).
- `summarize` carries it into each board.json row.
- BOARD.md gains a **join failures** column after geometry diffs and a **## Join failures** section. The section has one line per (page, state, kind, selector) with the sizes it failed at, or "None" when everything joined.

## Tests

- 3 new tests in `scripts/tests/test_chrome_board.py`; one existing test's column index moves 6 → 7 for the new column. At 41892d9e (tests only): **4 red** (2 errors, 2 failures), 19 passed. At e9512d87: **23/23**. Neighbouring gate tests (`test_layout_oracle_gate`, `test_ratchet_gate`, `test_finish_line_receipt`): 91/91.
- End to end: the full 42-row board at e9512d87 gives **39/42 green**, the same rows and verdicts as the develop run. Inspector default shows `| 31 | 7 | pixel |`, report shows `| 4 | 1 | pixel |`, and the Join failures section lists 8 distinct selectors (7 inspector, 1 report), each at all three sizes.
- Campaign: **26/26, mean 0.405 %**, on this branch's parity build (no-op cargo shim on PATH, `target/release/parity-capture` symlinked to the parity build; the seed binary was renamed aside first).

## Receipt (`scripts/receipt.py`)

```
candidate_sha e9512d879c5422fcac1421649a7402dd0f93b8e5  base_sha 83b46110  branch atlas/dt-t35-join-column
profile parity  dirty_state false  toolchain rustc 1.91.0 (f8297e351 2025-10-28)
binary target/parity/parity-capture sha256 c74149704161c65e…
campaign: cases 26 passed 26 failed 0 mean_diff_pct 0.4051 (sha256 ad41dabacd2eb50b…)
note: tooling only (scripts/chrome_board.py + its tests); no engine change
```

## Not done / for Atlas

- `trench/chrome/` is not re-generated on this branch, to avoid a conflict with T34's re-baseline (`atlas/dt-t34-one-oracle`, also waiting on the cap). Whichever lands second should re-run the board once so the committed BOARD.md has the column.
- Talos's Linux 3-vs-11 count was not re-measured here.
