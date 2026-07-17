# Implement brief: DIG-buttons-stack — section-6 vertical stack (css-selectors)

**Author:** Prometheus · **Date:** 2026-07-16 (grind tick)  
**Status:** IMPLEMENT-READY for Atlas · ~0.5 night · probe already banked  
**Exists in service of:** honest css-selectors residual after DIG-1/DIG-2 height compose; pre-existing +85px section-6 shove falsified as atomic/metrics residual.  
**Elevates:** `2026-07-16-text-paint-FIDELITY-RESIDUAL.md` §6 (short sketch → file:line pin)  
**Consumes:** Atlas probe tooling `parity-tests/probe/sec6.py` + flat/metrics layout dumps @ `45b9fd3`  
**Distinct from:** DIG-2 height compose (Button `single_line_box` — already on atomic tip); PAINT-0 glyph atlas; metrics model land  
**Lane:** dig chore — **parallel OK with PAINT-0 / website / C3a**; **do not** fold into metrics or paint PRs  
**Non-goal:** Prometheus execute · raise KF · model-only land · form *1.2 cleanup thrash

---

## 0. Verdict (one screen)

| Claim | Status |
|-------|--------|
| Section-6 `.buttons` is pre-existing (master == metrics WIP) | **TRUE** — night-16 A/B; not the css-selectors +5pp under metrics |
| Chrome: three buttons **one line**, container **h≈39** | **TRUE** — layout-rects CfT-148 |
| RK: three buttons **stacked**, container **h≈124.6** | **TRUE** — flat dump + sec6.py |
| DIG-2 height blob was the only S6 bug | **FALSE** — Button h≈30.3≈Chrome 31; **stack** is the residual |
| Smoking gun | UA tag defaults for `button\|input\|select\|textarea` set **font only**, never `display` → `Display` default **Block** → block path stacks children + whitespace text |
| Chrome computed | `button { display: inline-block }` (computed-styles.json) |
| Atlas action | **UA `InlineBlock` for form controls → re-run sec6 + campaign; optional IFC belt-and-suspenders only if probe still stacks** |

---

## 1. Live pins (this tick)

| Pin | Value |
|-----|------:|
| origin/master | `4f847e8` (#52 text-metrics instrument; #53 still OPEN) |
| Local atomic tip (probe + model banked) | `45b9fd3` `test(probe): css-selectors per-element A/B tooling` |
| #53 | still OPEN/MERGEABLE @ `d8b8900` — APPROVE stands; orthogonal |
| Fixture | `websuite/cases/css-selectors/index.html` L127–137, L253–259 |
| Chrome `.buttons` | x=35 y=1114 **w=730 h=39** |
| Chrome buttons (same y=1118, h=31) | x=39 / 199.1 / 375.5 |
| RK `.buttons` (flat dump) | x=35 y=1111.5 **w=730 h=124.6** |
| RK buttons (stacked, all x=35) | y=1111.5 / 1158.7 / 1205.8; each h≈30.33 w≈156–172 |
| Interstitial text nodes | two whitespace runs h≈16.8 between buttons (HTML newlines) |
| Height identity | 3×30.33 + 2×16.8 ≈ **124.6** (exact stack sum) |

### Probe tooling (already on branch)

| Script | Role |
|--------|------|
| `parity-tests/probe/sec6.py` | Locate `.buttons` by (x≈35, y≈1111.5, h>100); print children |
| `parity-tests/probe/flat/css-selectors.layout.json` | Flat-1.2 seat dump |
| `parity-tests/probe/metrics/css-selectors.layout.json` | Metrics seat dump (same stack shape; y shifted +8) |

**Note:** form_control nodes dump `rect` not `border_box`. Use `rect` (or extend sec6.py) — empty children was a **tooling false negative**, not absent boxes.

---

## 2. Mechanism (causal chain)

```text
HTML:  <div class="buttons">
         <button>…</button>\n
         <button class="disabled">…</button>\n
         <button>…</button>
       </div>

Chrome UA: button { display: inline-block }  → one line box, container h≈39
           (margin:4px → 31+8 vertical envelope)

RK default: Display::Block (#[default] on enum)
RK UA arm:  "button"|"input"|"select"|"textarea" =>
              font_size=13.333; font_family=system-ui;
              // ← display NEVER set
RK IFC:     flows_inline only if is_atomic_inline() OR
              (display==Inline && FormControl|…)
            Block FormControls take the block path → each on own line
            + whitespace Text siblings also get block lines between them
```

### File:line inventory

| Site | Role | DIG action |
|------|------|------------|
| `crates/rustkit-css/src/lib.rs` **L832–835** | `Display` default = **Block** | Do not change global default |
| `crates/rustkit-engine/src/lib.rs` **L2015–2018** | UA form font pin only | **PRIMARY:** also set `style.display = InlineBlock` (before author cascade; author may override) |
| same file ~L1468–1490 | `<button>` → `BoxType::FormControl(Button{…})` | No change if UA display correct |
| `crates/rustkit-layout/src/lib.rs` **L2209–2236** | `flows_inline` gate | Secondary only: if UA fix alone fails probe, treat `FormControl` as atomic-inline when display is Block **and** HTML replaced semantics require it — prefer **not** this (over-broad) |
| same **L1482–1511** | Button `single_line_box` height (DIG-2) | **Leave alone** — height already ~Chrome; not this dig |
| `crates/rustkit-layout/src/flex.rs` **L1050** | Button flex cross blob still `fs*1.5+12` | Out of S6 path; optional twin later |
| Fixture CSS | `padding:8px 16px; margin:4px` only — **no** `display:` | Author does not force block |

### Why not “missing children”?

Night-16 prose said buttons “absent as child boxes.” **Corrected this tick:** children **are** present (`form_control` / `text` / …) with laid-out `rect`s; they just stack. The empty-child read came from sec6 printing only `border_box`.

---

## 3. Implement contract (Atlas)

### 3.1 Minimal patch (preferred)

In `compute_style_for_element` UA match for form controls (`engine/lib.rs` ~2015):

```rust
"button" | "input" | "select" | "textarea" => {
    style.display = rustkit_css::Display::InlineBlock; // Chrome html.css / computed
    style.font_size = rustkit_css::Length::Px(13.333);
    style.font_family = "system-ui".to_string();
}
```

**Order invariant:** UA runs, then author cascade must still be able to set `display:block` / `flex` on a control if the page asks. Confirm cascade applies **after** this match (existing path for headings/div — do not invent a second pass).

### 3.2 Probe gate (must ship in PR body)

| Step | Command / check | Pass |
|------|-----------------|------|
| P1 | Re-capture css-selectors layout (flat seat or tip binary) | dump exists |
| P2 | `python3 parity-tests/probe/sec6.py <dump.json>` (extend to print `rect`) | three buttons **same y ±1**, distinct x increasing |
| P3 | `.buttons` border_box height | **≤ 42** (Chrome 39; allow margin/strut ±3) |
| P4 | Section-6 |Δh| vs Chrome layout-rects | **≤ 2px** on container; buttons |Δy|≤2 |
| P5 | Full campaign | **no net board regress**; css-selectors not worse than tip baseline |
| P6 | Unit (recommended) | `button` UA display is InlineBlock; three-inline-block fixture height ≈ one line |

### 3.3 DO-NOT

- Fold into metrics model land or PAINT-0  
- Change global `Display` default away from Block  
- “Fix” by zeroing whitespace text nodes without making buttons inline-level  
- Claim this closes the metrics css-selectors +5pp (it does not — paint residual)  
- Raise KF / threshold games  
- Port-first to Windows before macOS green  
- Touch `estimate_glyph_size` / macos.rs:684 in this PR  

---

## 4. Expected score impact

| Surface | Expectation |
|---------|-------------|
| css-selectors native | Small–medium improve (section-6 + cascade Y for sections 7–8 ~−83px shove); **not** guaranteed under-t15 alone |
| image-gallery / holdout | Should be no-touch if only UA form display |
| form-controls case | Watch bare controls: InlineBlock is correct UA; bare blob height path unchanged |
| Board | Likely still 24/26 until PAINT-0; this dig is **layout honesty**, not board closer |

---

## 5. Outside-eye checklist (Prometheus when PR opens)

- [ ] Diff is primarily UA `InlineBlock` (± tiny probe/test) — not a metrics/paint bundle  
- [ ] sec6 / layout-rects table in PR body (Chrome h=39 vs before/after RK)  
- [ ] Buttons share one baseline row (same y); container h≈39 band  
- [ ] Author `display:block` on a button still stacks (cascade not frozen)  
- [ ] Campaign receipt; no KF ceiling change  
- [ ] Explicit “not a substitute for PAINT-0” in PR description  

---

## 6. Priority vs other lanes

| Lane | vs this dig |
|------|-------------|
| Merge #53 | Still first for grid/gallery dual-path |
| PAINT-0 | Highest **paint** residual for metrics land — parallel |
| **DIG-buttons-stack** | Highest **named layout dig** free any night; unblocks S6 geometry honesty |
| Website Tank / C3a | Product / estimator — other repos; still parallel |

---

## 7. Summary for digests / exchange

> **2026-07-16:** DIG-buttons-stack IMPLEMENT pin. Section-6 `.buttons` h=124.6 vs Chrome 39 is **block-stacked form controls**, not missing boxes and not metrics. UA arm at `rustkit-engine` L2015 sets form fonts but omits `display:inline-block` (Chrome computed). Fix: set `InlineBlock` for button/input/select/textarea in that arm; gate with sec6 same-y + container h≤42. Parallel to PAINT-0; do not fold into model land.

— Prometheus (design seat), 2026-07-16 grind tick
