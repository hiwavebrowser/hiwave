# IFC Slice C — GATE OPEN

**Author:** Prometheus · **Date:** 2026-07-11 (grind tick, post-Atlas #37–#41 merge wave)  
**Status:** **OPEN for implement** — Atlas may start C0 tonight  
**Implements from:** `forensics/2026-07-11-ifc-slice-c-baseline-BRIEF.md` (contract unchanged)  
**Pinned tree:** `hiwavebrowser/hiwave-macos` `origin/master` @ **`740656c`**  
**B2 content SHA:** `53ab3ca` (merged via PR #37 / merge commit `287d0be`)  
**Lane:** IFC quality next tip — **not** DIG-2 buttons, not campaign thresholds

---

## 0. Gate checklist (was §0 of C brief)

| # | Criterion | Verdict | Evidence |
|---|-----------|---------|----------|
| 1 | **#37 B2 on master** | **PASS** | `gh pr view 37` → MERGED; master log shows `287d0be Merge #37` then #38–#41 stacked on top. Tip `740656c` = DIG-1 after CI-1/2 + GradientText + B2. |
| 2 | **Wrap hard rows green** | **PASS** | B2 PR body: `probe_b2_wrap.py` on `mixed-inline-wrap.html` → **12/12 hard assertions** (center/right/left split-after-sibling). Unit tests live on master: `center_midline_split_line0_uses_flow_plus_align`, `center_midline_split_does_not_stomp_earlier_text_lines`, `left_midline_split_offsets_unchanged`, `right_midline_split_line_ends_at_container`. Final B2 PR Parity Gate `29162498221` green (all 4 swarms + **pr-aggregate SUCCESS** after CI-1). |
| 3 | **Nested-inline residual ledgered, not expanded into C** | **PASS** | `probe_b2_wrap.py` marks rows 1–3 (`hard=False`) as informational fragmentation gap; only B2 split-after-sibling rows are hard. C brief §0.3 / residual map: do not expand nested Inline fragmentation into valign. |

**Therefore:** the hard gate that blocked C is **lifted**. Atlas should open C0 (probe-first) from the existing implement brief without waiting for another design ceremony.

---

## 1. Live truth re-pin (master@740656c)

Re-verified with `git show` / `git grep` against `origin/master` (no dirty working-tree checkout — local tree has unrelated WIP).

### 1.1 B2 machinery present

| Symbol | Still true |
|--------|------------|
| `LayoutBox.text_flow_first_offset: Option<f32>` | yes (~L724) |
| `text_splits_inline` (align gate removed) | yes (~L1212) |
| Dual IFC loops both call split path | yes (~L2187 / ~L2574) |
| Mid-line contract unit tests | yes (~L5285–5373) |
| Fixtures | `parity-tests/repro/mixed-inline-wrap.html`, `mixed-inline-img.html`, `probe_b2_wrap.py` |

### 1.2 Slice C still needed (unchanged mechanism)

| Claim | Evidence @ 740656c |
|-------|-------------------|
| `vertical_align` parsed on `ComputedStyle` | `rustkit-css` only (`vertical_align: VerticalAlign` ~L1952) |
| **layout never reads it** | `git grep vertical_align crates/rustkit-layout` → **empty** |
| Member place Y is still **top-of-line** | Both IFC loops: `content.y = container.y + cursor_y + margin.top + border.top + padding.top` (~L2166–2171 and ~L2554–2559) |
| `baseline_is_bottom_edge` only feeds **line height** (`line_below_baseline`), not Y place | same sites; comment claims “box bottom sits ON the baseline” but place path does not move Y to baseline |
| Text paint half-leading still emission-time | ~L4318–4360 |
| C fixture ready | `mixed-inline-img.html` with L/C/R baseline rows + `.mid` middle row |

**No C design rewrite required.** Prior brief pins survive DIG-1 / GradientText / CI honesty (orthogonal files).

---

## 2. Atlas order of operations (now)

1. **C0 probe (mandatory, ≤30–60m)** — on master@740656c (or tip):  
   - Render `parity-tests/repro/mixed-inline-img.html` → RK layout.json / y_table.  
   - Chrome CfT 148 vs RK: `rk_img_bottom`, `rk_text_baseline`, `chrome_delta` for baseline rows; img mid vs text mid for `.mid`.  
   - If baseline rows already within ~2px structural band → **shrink C to middle-only**. Do not invent work.  
2. **C1** — both IFC loops: `baseline` + `baseline_is_bottom_edge` → margin-bottom on alphabetic baseline.  
3. **C2** — `vertical-align: middle` midpoint rule; hard-assert `.mid`.  
4. Ring Prometheus for outside-eye (checklist still §6 of C brief).

**Expected size:** ~80–150 LOC layout + units if scoped. Shared line-model rewrite = stop and split.

### Explicit non-combine (still)

Do **not** fold into the C PR:

- DIG-2 form **buttons** (Atlas has that queued as separate dig — keep separate)  
- Nested-inline fragmentation  
- Campaign / KF threshold edits  
- CI workflow churn  
- Windows port (Athena contracts only)

DIG-2 may run **in parallel** as a separate PR; it is form metrics, not IFC baseline.

---

## 3. Scoreboard / CI notes (context only — not C blockers)

| Signal | Status | Implication for C |
|--------|--------|-------------------|
| Campaign | 21/26 @ t15 avg ~8.6 (Atlas seq 71) | C is structure, not a scoreboard sweep promise |
| Holdout | 6/6 avg 5.8 | Holdout stays sacred; don't edit holdout fixtures for C |
| css-selectors | 18.94 → **16.65** after DIG-1 | Residual dig debt; DIG-2 next; not a C gate |
| B2 PR gate | swarms + aggregate green after CI-1 | Wrap hard criterion met |
| Master **push** Parity Gate red | Job `commit-gate` step **“Trigger umbrella metrics update”** fails; swarms skipped on that workflow path | **Infra/umbrella**, not pixel/IFC. Do not re-gate C on master-push red. PR-path swarms remain the visual signal. |

---

## 4. Seat notes

### Atlas

Gate open. Start **C0** from `2026-07-11-ifc-slice-c-baseline-BRIEF.md` (status updated to OPEN). Cite this doc + B2 merge SHA in the PR body. DIG-2 stays a separate PR if you touch buttons.

### Athena

Portable only: layout owns `vertical-align` for replaced + empty atomic; paint does not invent image baseline. When Windows IFC reaches line-level place, port the same dual-loop mirror rule. No Windows code from this tick.

### Pete

Next IFC tip is live for Atlas. Prometheus design lane for C is now **outside-eye on the PR**, not further banking. No merge from this seat.

---

## 5. Docs updated this tick

| File | Change |
|------|--------|
| **This file** | Gate OPEN receipt |
| `forensics/2026-07-11-ifc-slice-c-baseline-BRIEF.md` | Status → OPEN; §0 checked; pins → 740656c; seat guidance post-merge |
| `IFC_PHASE3_SKETCH.md` | B2 SHIPPED; C OPEN with pointer |

---

## 6. One-line verdict

**#37 on master + B2 wrap hard 12/12 + nested residual ledgered → Slice C is OPEN. Atlas: C0 probe then C1/C2; Prometheus: outside-eye when the PR opens.**
