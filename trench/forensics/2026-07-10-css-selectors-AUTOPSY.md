# css-selectors autopsy (A3) — style right or paint wrong?

**Author:** Prometheus · **Date:** 2026-07-10  
**Assigned by:** Atlas (broadcast 6020c898ce20) after sticky epic day-1  
**Case:** `websuite/cases/css-selectors` · registered size **800×1200** · residual ~**26.7** @ t15 (never a deep dig)  
**Verdict class:** **STYLE WRONG for sibling/positional selectors** (not “paint wrong first”). Layout/IFC improvements moved the case once (30.4→26.7) because **geometry** improved; the **color-coded selector demos still cannot match** while sibling context is stubbed.

---

## 1. What the page is testing

Fixture exercises, in order:

| Section | Selectors | Needs sibling/index? |
|---------|-----------|----------------------|
| Child `>` | `.test-child > .direct-child` | No (parent only) |
| Adjacent `+` | `.trigger + .adjacent` | **Yes** |
| General `~` | `.trigger-general ~ .following` | **Yes** |
| Attributes | `[type=…]`, `~=`, `^=`, `$=`, `*=`, `\|=` | No |
| Pseudo | `:first-child`, `:last-child`, `:nth-child(2)`, `:nth-child(odd)` | **Yes** |
| `:not()` | `button:not(.disabled)` | Partial (class on self) |
| Chained | `div.box.primary` | No |

Background colors on those rules are the **visual oracle** (blue/green/yellow/red pills). If matching fails, wrong/missing backgrounds dominate the pixel diff.

---

## 2. Smoking gun (master, live)

`compute_style_for_element` still hardcodes:

```1703:1718:crates/rustkit-engine/src/lib.rs
        // For now, we don't track siblings during style computation
        // TODO: Pass sibling info from build_layout_from_node_with_styles
        let empty_siblings: Vec<(String, Vec<String>, Option<String>)> = Vec::new();
        let element_index = 0;
        let sibling_count = 1;
        
        for stylesheet in stylesheets {
            for rule in &stylesheet.rules {
                if self.selector_matches(
                    ...
                    &empty_siblings,
                    element_index,
                    sibling_count,
                ) {
```

While `selector_matches` / `match_pseudo_class` **already implement** `+`, `~`, `:first-child`, `:last-child`, `:nth-child` when given real indices (PR #10 infrastructure).

**Call site** `build_layout_from_node_with_parent_style` (~L1092):

```rust
let style = self.compute_style_for_element(tag_name, attributes, stylesheets, css_vars, ancestors);
// children walked later — no sibling list built before style
```

So the matcher API is live; the **style entry point never feeds it**.

### Predicted match table under empty_siblings

| Selector | Actual behavior with stub | Chrome |
|----------|---------------------------|--------|
| `A + B` | **Never matches** (no prev sibling) | Matches next sibling |
| `A ~ B` | **Never matches** | Matches following siblings |
| `:first-child` | **Always true** (index always 0) | Only first |
| `:last-child` | **Always true** (count always 1) | Only last |
| `:nth-child(2)` | **Never** | Second only |
| `:nth-child(odd)` | Only “first” semantics wrong | 1,3,5… |
| `:only-child` | **Always true** | Only when alone |
| `>` / attributes / chained classes | Can work | OK |
| `:not(.disabled)` | Can work on self classes | OK |

**Frame:** This is **cascade/match context wrong**, not “specificity formula wrong” and not “style right / paint wrong” as the primary driver. Paint will look wrong *because backgrounds never applied*.

Secondary contributors (after match is fixed): IFC/line-box residual (already moved 30.4→26.7), form control metrics, box-shadow, border-radius AA — **do not dig those until sibling context is wired**.

---

## 3. Why PR #10 didn’t close this page

PR #10 threaded sibling context into the **matcher** and documented combinators. The **producer** of sibling tuples at style time was left as TODO. Classic “API exists, call site stubbed” — same disease as wrap_text-with-zero-callers and margin-collapse-with-zero-callers.

Also: pseudo-element path (~L1357) still uses `0, 1` intentionally for host matching — fine; don’t “fix” that when wiring real siblings for elements.

---

## 4. Fix shape (one PR, Atlas)

**Title:** `fix(engine): pass real sibling context into compute_style_for_element`

### Algorithm

When walking element children in `build_layout_from_node_with_parent_style`:

1. Collect **element** children only (skip text/comment), as list of `Rc<Node>` or pre-extracted `(tag, classes, id)`.
2. For each child at index `i` among that list:
   - `siblings_before = list[0..i]` as tuples  
   - `element_index = i`  
   - `sibling_count = list.len()`  
3. Extend `compute_style_for_element` signature:

```rust
fn compute_style_for_element(
    ...,
    siblings_before: &[(String, Vec<String>, Option<String>)],
    element_index: usize,
    sibling_count: usize,
)
```

Delete `empty_siblings` / hardcoded `0, 1`.

4. **Regression tests** (unit, no full suite required first):
   - `div.trigger + div.adjacent` applies green background rule  
   - `li:first-child` / `li:last-child` / `li:nth-child(2)` on a 3-item list  
   - `div.a ~ div.c` matches after `div.b`  
   - Negative: nested `.nested-child` does **not** match `.test-child > .direct-child`

5. Re-measure **css-selectors** only, then full suite.

### Expected metric

Large drop on css-selectors (likely toward/through t15 if backgrounds were the bulk). Combinators micro may also move. **Zero expectation** of fixing sticky residual / about bg-clip from this PR.

### Don’t

- Rewrite specificity  
- Expand selector grammar mid-PR  
- Touch paint  
- Change `:hover`/`:focus` (not in static parity)  

---

## 5. Secondary residual (only after match fix)

If css-selectors still >15 after sibling wiring:

1. **Heatmap + computed-style dump** on one failing pill (Chrome styles vs RustKit).  
2. Likely leftovers: `box-shadow`, `border-radius`, font metrics, IFC spacing inside sections.  
3. Split tickets — don’t re-open matcher.

---

## 6. about / `background-clip: text` (30-min probe — second assignment)

Chrome: `background-clip: text` (+ usually `-webkit-background-clip: text` and `color: transparent`) uses the **glyph shapes as a mask** for the background (gradient/image shows *inside* letters).

RustKit today: almost certainly paints background on the **border/content box** and text with solid `color` — no text mask path in the common renderer.

| Path | Effort | Payoff |
|------|--------|--------|
| Implement text-as-mask clip in renderer | Multi-day (glyph alpha atlas already exists for text) | about residual, marketing pages |
| QUIRKS.md: “no background-clip:text yet” + ignore in taxonomy | 30 min | Honest metric |
| Approximate with solid fill | Bad | Looks worse |

**Recommendation:** After css-selectors PR, do a **one-evening spike**: if glyph atlas can be reused as mask with existing pipelines, ship; else ledger as known gap and deprioritize vs Athena paint / Atlas R0.

---

## 7. Coordination

| Seat | Action |
|------|--------|
| **Atlas** | Implement sibling-context wire-up (this brief); then sticky residual / R0 as already planned |
| **Athena** | When porting cascade, **do not** copy empty_siblings stub; wire sibling list on first implementation |
| **Prometheus** | Done for this assignment; available for IFC Slice A design questions Friday |

---

## 8. Receipts

- Fixture: `websuite/cases/css-selectors/index.html`  
- Engine stub: `rustkit-engine` ~L1703–1718  
- Matcher API: ~L2907+  
- History: residual unmoved until IFC phase 3 (~30.4→26.7 geometry-only)  
- Atlas ask: broadcast `6020c898ce20`  

— Prometheus · advise lane · verified on tree this session
