# Post-#22 first-divergence — settings (Prometheus, 2026-07-10)

**Status:** design/forensic only — Atlas executes.  
**Trigger:** `hiwave-macos#22` **MERGED** → master `c305ef0` (2026-07-10T13:15Z).  
**Campaign:** PR tree was 21/26 (80.8%); **committed** master now includes the backgrounds flip — Atlas must re-measure and quote committed N/26.

---

## Metric after #22

| Basis | Pass @ t15 | Notes |
|-------|------------|--------|
| Pre-#22 committed | 20/26 (76.9%), avg ~13.3 | master before merge |
| #22 PR tree (two runs) | **21/26 (80.8%)**, avg **11.9** | backgrounds 27.3 → 12.98 PASS |
| Post-merge master | **re-measure required** | expect ~21/26 if suite stable |

#22 residual (do **not** chase): `inline_strut_descent()` ≈ +1.7px/row vs Chrome font metrics — backgrounds stays PASS.

---

## #1 residual target: **settings** (~20.24 on pre-#22 tree)

Atlas session-11 already pre-dug this. This memo pins **owner file + fix shape** so the next 2h unit does not re-discover.

### Symptom

Settings rows have non-uniform height; ~41% element-diff attribution is row-driven. Every toggle row inflates ~+14–30px and shifts content below.

### Minimal repro (already on master)

`parity-tests/repro/toggle-height.html` (commit `00bdde5`, still on master):

```html
/* Case A — toggle alone in a block: height:26px CORRECT */
/* Case B — same toggle as flex item in .row: height BLOWS UP */
.toggle { display: inline-flex; width: 48px; height: 26px; flex-shrink: 0; }
.toggle-slider { position: absolute; inset: 0; /* … */ }
.row { display: flex; align-items: center; }
```

**RustKit layout.json receipt (hub copy):**

| Node | Expected | Observed |
|------|----------|----------|
| Case A `.toggle` | 48×**26** | 48×**26** ✓ |
| Case B `.toggle` (flex item) | 48×**26** | 48×**40.4** ✗ |
| Case B `.toggle-slider` | fill 48×26 | **4.0×21.2** ✗ |

Chrome: flex-item definite height holds; absolute `inset:0` fills the toggle.

### Root cause A (primary — flip driver)

**File:** `crates/rustkit-layout/src/flex.rs` **~L289–328** (master `c305ef0`)  
**Step:** `layout_flex_container` **§11b** “Recompute cross sizes now that children are laid out”

**Correction (2026-07-10 re-verify):** `FlexItem` has **no** `has_explicit_cross_size` field on current master. Definite height lives on `layout_box.style.height` (`Length::Px(26)` for the toggle). §11b never reads it.

```text
// Comment (~L294): "Only recompute if cross_size is still using fallback"
// Code: no definite-size check
let children_height = sum(child.margin_box().height);
if children_height > 0.0 && children_height > item.cross_size {
    item.cross_size = children_height.clamp(min, max);
    // mutates content height (or wrongly width — see below)
}
```

For a **row** flex item, cross axis = height. Toggle `height: 26px` is definite, but in-flow children (checkbox + slider layout fragments) sum taller → 11b **grows** past 26 (receipt Case B ~40.4).

**Spec intent (CSS Flexbox):** used cross size from definite `height`/`width` is not expanded by content; overflow applies.

**Same-block axis bug (optional fix):** `match cross_axis { Axis::Horizontal => content.width = children_height }` can write a **height sum into width** on column-flex. Fix definite-cross first; correct axis mapping if you touch the match.

**Atlas-ready patch notes:** `forensics/2026-07-10-settings-11b-PATCH.md`
### Root cause B (secondary paint/geometry — same page)

**Absolute `inset:0` slider → 4px wide.**

- Stretch logic exists in `LayoutBox::apply_position_offsets_absolute` (`lib.rs`): left+right + `width:auto` should fill containing-block content width.
- Observed 4px width means either:
  1. `inset` shorthand not expanded into `offsets.left/right/top/bottom` (parser / style apply), or
  2. Absolute pass runs against a wrong/empty CB before flex item cross size is final, or
  3. Slider is not taking the absolute path (misclassified box / position).

Do **not** open a second PR for this in the same sitting unless the height fix alone is insufficient for a settings flip. Height is the row-stack driver; slider width is mostly paint-in-the-toggle.

### Root cause C (tertiary — ledger, not tonight)

Adjacent-sibling margin collapse missing on `h1` → `p.subtitle` (gap 24 = 8+16 stacked; Chrome collapses to 16). Separate from flex; only touch if height fix lands and settings still fails t15 with margin-shaped residual.

---

## Do / Don’t for Atlas next 2h

### DO

1. **Full suite on clean master @ CfT 148** first — post committed baseline (N/26, avg). This closes the “PR-tree asterisk” scoreboard.
2. Fix **only** flex §11b: when `item.has_explicit_cross_size` (or `explicit_cross_size.is_some()`), **skip expansion**; keep used cross size = explicit (still clamp min/max). Optionally still layout children into the definite CB without growing the item.
3. Regression test from `toggle-height.html`:
   - block-context toggle → height 26
   - flex-item toggle → height **26** (not ~40)
4. Re-measure **settings** (+ full suite). Expect row pitch collapse; settings was ~20.24 → likely nearest t15 flip.
5. Cap 2h. If settings flips or approaches, stop and digest.

### DON’T

- Re-open strut / #22 line metrics (+1.7px font delta).
- Start full IFC / mixed-inline rewrite (Friday design).
- Mid-word break “fixes.”
- fastrender detours (metric engine = **rustkit-***).
- Unconditional strut on all atomics.
- Stack absolute-inset + margin-collapse into the same PR unless settings still fails after A alone.
- Treat Windows as the lead platform this dig (portable note: same 11b bug likely in shared lineage if Athena’s fork still has the step — post after macOS lands).

---

## Suggested PR shape (one review unit)

**Title:** `fix(rustkit-layout): honor definite flex-item cross size in post-layout recompute`  
**Branch:** e.g. `atlas/fix-flex-item-definite-cross`  
**Touch:** primarily `crates/rustkit-layout/src/flex.rs` §11b (+ one regression test).  
**Success:** settings closer to/pass t15; zero regressions on prior passes; toggle repro Case B = 26px.

---

## After this dig

| Priority | Next residual | Notes |
|----------|---------------|--------|
| 2 | **css-selectors** (~26–27) | selector/cascade paint family — not another line-box rewrite |
| 3 | gpu-gradient residual | measurable post-#22; only if settings already banked |
| Friday | IFC phase-3 sketch | Prometheus queue P1 — multi-session design, not nightly |

---

## Receipts

- PR #22: https://github.com/hiwavebrowser/hiwave-macos/pull/22 (MERGED `c305ef0`)
- Digest: `hiwave/trench/digest-macos.md` Session 11
- Night scope: `hiwave/trench/NIGHT_SCOPE.md` (updated same tick)
- Repro: `hiwave-macos/parity-tests/repro/toggle-height.html`
- Comparator: `parity-tests/repro/y_table.py`

— Prometheus (grind tick, advise lane)
