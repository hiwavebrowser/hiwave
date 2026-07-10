# Code review — light refactor / reduce size (Prometheus)

**Scope:** recent hiwave-macos PRs #10–#22 + hot files on master `c305ef0`.  
**Tone:** constructive; campaign velocity was high and correct. This is **debt from that velocity**, not a fail grade.  
**Lane:** Atlas implements; Prometheus advises.

---

## 1. What the recent PRs did well

| Pattern | Examples | Why keep it |
|---------|----------|-------------|
| Tiny measured fixes | #19 (+25/−11), #21 (+15/−25), #22 (+140/−20) | Best ROI; easy review |
| Delete duplicate, use crate of record | #6 color → rustkit-css | Correct architecture |
| Wire existing dead code | #10 margin-collapse callers; #15 wrap_text callers | Cheaper than rewriting |
| Repro + receipt | toggle-height, y-table, controlled A/B | Makes refactors safe later |

**Biggest size events (harder to review, more debt):**

| PR | +/− | Note |
|----|-----|------|
| #11 images | +2011/−1410 | Includes baselines; real code churn still large |
| #17 phase 3 line boxes | +1579/−766 | Structural; expected bulk |
| #15 phase 1 wrap | +922/−391 | Structural |
| #14 flex border-box | +282/−23 | Flex path growing without Axis helpers |

**Process suggestion:** after every 2–3 feature PRs, allow **one “delete-only” PR** (net negative lines, tests hold). That trains the muscle of shrinking without stopping the trench.

---

## 2. Highest-leverage shrinks (ordered)

### A. Kill engine’s private CSS parser island (~1.1k lines) — **#1 size win**

`rustkit-engine/src/lib.rs` is **5826** lines. From ~L4290 down is a second CSS language:

- private `parse_color` (full named/hex/rgb/hsl) **despite** `rustkit_css::parse_color`
- `parse_gradient`, `parse_length`, `parse_calc`, `parse_transform`, `parse_grid_*`, …

PR #6 was the right idea; **the island grew back / was never fully deleted**. Call sites still use local `parse_color` (e.g. L1808, L1934, …).

**Refactor:**

```text
// engine
use rustkit_css::{parse_color, parse_length, …}; // or thin wrappers only
// delete private fn parse_color / hsl_to_rgb / … once call sites match
```

**Gate:** engine tests + one parity smoke (bg-solid / gradients).  
**Expected:** −500 to −1000 lines if gradients/lengths already exist in css; if not, **move** functions to `rustkit-css` once, don’t leave two homes.

### B. `Axis` helpers for flex (~50–80 lines deleted, many bugs prevented)

`flex.rs` has **53** `match main_axis` / `cross_axis` sites. §11b already has the classic bug shape: `children_height` written into **width** on the horizontal-cross arm (L313–316).

```rust
impl Axis {
    fn size(self, w: f32, h: f32) -> f32 { match self { H => w, V => h } }
    fn set_content(self, d: &mut Dimensions, v: f32) { … }
    fn margin_pair(self, style) -> (start, end) { … }
}
```

Then §11b becomes ~10 lines with a **definite-cross** skip (settings dig) instead of another copy-paste match.

### C. One place for “content origin = CB + margin + border + padding”

In `lib.rs`, this formula appears **many times** (block, float L/R, absolute, collapse path):

```text
content.x = cb.x + margin.left + border.left + padding.left
// same for y
```

**Extract:**

```rust
fn place_in_containing_block(&mut self, cb: &Dimensions) {
    self.dimensions.content.x = cb.content.x
        + self.dimensions.margin.left
        + self.dimensions.border.left
        + self.dimensions.padding.left;
    // y analog
}
```

#22’s border-box fix was exactly “we forgot part of this formula in one path.” One helper → fewer 2px ghosts later.

### D. Collapse `layout_block_children` vs `_with_collapse` (~20 lines + one brain)

Today (~L1238 / L1261): same loop; differ only in `layout` vs `layout_with_collapse` and cursor advance (margin-box height vs border-box bottom).

```rust
fn layout_block_children_inner(&mut self, collapse: Option<(&mut MarginCtx, &mut FloatCtx)>) 
```

Or always take collapse contexts (nullable no-op). Removes “which entry point?” tax for the next agent.

### E. Don’t grow `text.rs` inside layout (structural, not this week)

`text.rs` is **1328** lines of font/shaping platform code living under **layout**. Layout already has `rustkit-text`. Long-term: layout keeps **line breaking API only**; move font chains to `rustkit-text`.  
**Not a nightly dig** — schedule as a pure-move PR when trench is green for a day.

### F. `calculate_block_height` Length match duplication

`match self.style.height` with Px/Percent/Vh/Em/Rem repeated in width/height paths. One:

```rust
fn resolve_used_length(len: &Length, font: f32, pct_base: f32, viewport: (f32,f32)) -> Option<f32>
```

Used by width, height, min/max. Small but multiplies every new unit.

---

## 3. Per-PR notes (recent)

| PR | Review take | Slim opportunity |
|----|-------------|------------------|
| **#22** strut/border-box | Correct surgical fix | Extract `place_in_containing_block`; avoid third copy of m+b+p |
| **#21** display→box type | Good deletion (−25) | Template for future PRs: prefer delete |
| **#20** phase 5 IFC split | Feature bulk OK | Ensure split helpers live in one module; avoid parallel split in lib.rs + text.rs |
| **#18** whitespace collapse | OK | Keep collapse pure in box-build; no re-collapse in layout |
| **#17** phase 3 share lines | Necessary bulk | Follow with “delete old layout_inline path if dead” commit |
| **#15–16** wrap + intrinsic | Good | Shared `estimate_min_content_width` already pub — keep **one** estimator for flex/grid/text |
| **#14** flex border-box | Growing flex.rs | Bundle with Axis helpers |
| **#13** content width not line-height | Good | Same estimator as #16 |
| **#11** images | Huge | Renderer bind_group selection table > triple-copy flush paths |
| **#10** sibling context | Correct | Engine style path still dense; sibling args as a small struct reduces arity |
| **#6** color delegate | **Incomplete** | Local `parse_color` still ~L4290 — finish the job |

---

## 4. Suggested PR stack (low risk → higher)

| Order | Title | Net | Risk |
|------:|-------|-----|------|
| 1 | `chore(engine): use rustkit_css::parse_color; delete private color parser` | −100–200 | Low if tests cover named/hex/rgb |
| 2 | `chore(layout): place_in_containing_block helper` | −30–50 | Low + prevents #22-class bugs |
| 3 | `fix(flex): Axis content size helpers + skip §11b on definite cross` | −20 + **settings fix** | Medium — functional + cleanup |
| 4 | `chore(engine): move remaining parse_* into rustkit-css or delete` | −500–900 | Medium — needs inventory |
| 5 | `chore(layout): unify layout_block_children*` | −15–30 | Low |
| 6 | (later) `chore: move font stack from layout/text.rs → rustkit-text` | large move | High process, low behavior if pure move |

Pair **#3** with the settings dig Pete wants — cleanup that **pays a pixel**, not cleanup for its own sake.

---

## 5. Review checklist for future trench PRs (Atlas / Athena)

1. **Net lines:** if +200 without a new subsystem, ask “what dies?”  
2. **Single owner crate:** CSS parse only in css; layout geometry only in layout; paint bind only in renderer.  
3. **No second formula** for content origin / axis size / color.  
4. **Comment must match code** (§11b’s “only if fallback” is a lying comment — either implement or delete).  
5. **Baselines** in separate commit from logic when possible (#11 mixed them → harder review).

---

## 6. What not to do

- Don’t pause the trench for a multi-week “architecture rewrite.”  
- Don’t merge layout_text into fastrender or vice versa mid-campaign.  
- Don’t “simplify” by removing tests.  
- Don’t big-bang delete engine parsers without a call-graph pass (`rg parse_`).

---

— Prometheus · 2026-07-10 · review only
