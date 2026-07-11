# Outside-eye review: hiwave-macos PR #37 (IFC Slice B2)

**Author:** Prometheus · **Date:** 2026-07-11 (grind tick)  
**PR:** https://github.com/hiwavebrowser/hiwave-macos/pull/37  
**Branch / tip:** `atlas/ifc-b2-midline` @ `26490c3`  
**Against brief:** `trench/forensics/2026-07-11-ifc-b2-midline-split-BRIEF.md`  
**Lane:** design/review only — no merge from this seat.

---

## Verdict

**APPROVE — merge when CI infrastructure is honest.**

Contract match to the B2 brief is tight. The four unit probes named in brief §6 are present and assert the right invariants. Dual IFC loops are mirrored without the shared-loop extract (brief §5). Nested-`<b>` fragmentation is correctly ledgered, not chased (brief §7). Campaign flat at 21/26 avg 8.7 and holdout 6/6 avg 5.8 matches the brief's "suite not required to move" exit.

Do **not** block on `pr-aggregate` red this run: the log is `Merging runs: ` (empty) → `Error: No data to aggregate`. All four `pr-swarm` shards **passed**. That is an artifact-path / merge-job flake, not a pixel regression from B2. Re-run aggregate or confirm local receipt before merge if policy requires a green rollup; do not rewrite engine to silence an empty merge.

---

## Checklist vs brief

| Brief item | Status | Evidence |
|------------|--------|----------|
| Open `text_splits_inline` to Center/Right | **PASS** | Align gate removed; signature is `(child, cursor_x)` only |
| Explicit mid-line flag (no offset sniffing) | **PASS** | `LayoutBox.text_flow_first_offset: Option<f32>`; set in `layout_text_in_flow`, cleared on block path |
| Line 0 = FLOW ⊕ ALIGN | **PASS** | `align_split_close`: `tls[0].x_offset = flow0 + o0`; O₀ from **assembled** `flow0 + tls[0].width` |
| Prior siblings shift by same O₀ | **PASS** | `translate_subtree` on non-split priors; split priors only `+=` last visual line |
| Never `translate_subtree` multi-line text that owns per-line offsets | **PASS** | Text child never translated; only its line 0 offset written |
| Middle lines pure per-line align | **PASS** | `tls[1..n-1]` get `align(tl.width)` |
| Last line open; last-fragment close does not re-stomp | **PASS** | Last left to recorded-lines; `apply_text_align_offset` branches on flag → `last.x_offset += offset` only |
| Left/Justify no-op for align writes | **PASS** | `align_split_close` early-returns; Left unit test keeps FLOW + origin |
| Both IFC loops | **PASS** | `layout_block_children` + `_with_collapse` both push `split_records` + call `align_split_close` |
| No shared-loop extract | **PASS** | Deliberate, brief-aligned |
| Fixtures wrap + img | **PASS** | `mixed-inline-wrap.html`, `mixed-inline-img.html` + `probe_b2_wrap.py` |
| 4 named unit tests | **PASS** | Exact brief §6 names present |
| Nested Inline fragmentation | **LEDGERED** | Probe hard=False on rows 1–3; PR body documents 151px vs 180px container |

---

## Design notes (not blockers)

### 1. `line0_width = flow0 + tls[0].width` assumes FLOW already on `x_offset`

`layout_text_in_flow` must bake FLOW into `text_lines[0].x_offset` before `align_split_close` runs. That is true on this PR (flag set with the same `first_line_offset`). Future edits that zero line-0 offsets before the close pass will silently pure-center. Worth one comment near the push into `split_records` if anyone refactors emission order — optional.

### 2. `n_lines == 1` mid-line join path unchanged

When the run fits the remainder (`n_lines == 1`), no `split_records` entry — correct. Flag is still set on the box; a later recorded close uses `+=` so FLOW survives. Good for the "Hi " + short bold join under Center.

### 3. Nested `Inline` fragmentation remains the real residual

Rows with long text **inside** `<b>` still align against the inline box's width, not the container. Brief §7 non-goal — do not expand #37. When Slice C or a later IFC night opens fragmentation, the fixture rows 1–3 become the hard gate; keep `probe_b2_wrap.py`'s hard/info split.

### 4. Collapse-path twin is behavioral, not line-identical

Both loops call the same helper; fine. If a future bug is collapse-only, add one unit that forces margin-collapse IFC — not required for #37.

---

## CI reading (this head)

| Check | Result |
|-------|--------|
| audit | pass |
| pr-swarm 0–3 | pass |
| collect-metrics | pass |
| pr-aggregate | **fail — empty shard merge, not suite** |

Local receipts claimed by Atlas (trust with usual discount; symbols + tests inspected): rustkit-layout 244/244; probe 12/12 hard; campaign 21/26 @ 8.7; holdout 6/6 @ 5.8.

---

## Advance-contract post-ship (orthogonal, closes P0 outside-eye)

PR #36 already on master (`8e00d22`). Quick checklist against `2026-07-11-advance-contract-IMPLEMENT.md` §5:

| Item | Status |
|------|--------|
| `DisplayCommand::Text` carries advances + ascent | **SHIPPED** |
| Paint cursor uses layout advances | **SHIPPED** (`draw_text_with_metrics`) |
| Third TextShaper in glyph hot path deleted | **SHIPPED** (baseline-relative entries) |
| Unit sum(advances) vs measure ±0.5px | **SHIPPED** |
| **`GradientText` carries advances** | **OPEN residual** |

### GradientText residual (confirmed on origin/master)

Emission path:

```text
if is_gradient_text:
  push GradientText { text, x, y, font…, gradient, rect }  // NO advances, NO ascent
  continue
// only regular Text gets shape_line_advances(...)
```

`GradientText` struct still has no `advances` / `ascent` fields. Renderer `draw_text_gradient` therefore re-owns horizontal placement (Atlas seq 68 correctly flagged this). Regular `Text` closed the 17px measure-vs-paint lie; **clip:text / GradientText still on the dual path**.

**Follow-up chore (Atlas, small — not B2, not #37 scope):**

1. Add `advances: Option<Vec<f32>>` + `ascent: Option<f32>` to `DisplayCommand::GradientText` (mirror `Text`).
2. At emission, call the same `shape_line_advances` before push (do not `continue` past the shape call).
3. `draw_text_gradient` consumes layout advances the same way as `draw_text_with_metrics`.
4. Unit: shape a clip:text string with `letter-spacing: 2px`; sum(command.advances) == measure ±0.5px; paint cursor delta matches.

Do **not** combine with B2 merge. After #37 lands, this is the cleanest one-night text-stack closer left on macOS.

---

## Sequencing after merge

1. **Merge #37** (Pete/Atlas) once aggregate flake is re-run or waived.  
2. **GradientText advance carry** (chore, ~0.5 night).  
3. **Slice C baseline brief** — Prometheus can author when B2 is green on wrap hard rows; hooks still `baseline_is_bottom_edge` / strut; `vertical_align` still missing.  
4. Campaign residuals (css-selectors underline/bullets/forms) stay dig items; no new matcher brief. Holdout already 6/6.

---

## Portable (Athena)

B2 contracts from brief §10 still stand; after #37 merges she can port fixtures + the flag/`align_split_close` shape when Windows IFC reaches line-level align. Canvas §14.2 + grid Phase 9.5 + advance contract notes from Atlas overnight still apply first on her paint stack.

---

## Decision board (this tick)

1. Merge #37 as B2 complete? **YES** (infra aggregate aside).  
2. Block on nested-inline fragmentation? **NO** — ledgered.  
3. Open Slice C brief this tick? **NO** — wait for merge green + wrap hard rows on master.  
4. GradientText advance follow-up? **YES, separate PR after #37.**

— Prometheus
