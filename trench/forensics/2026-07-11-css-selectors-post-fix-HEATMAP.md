# css-selectors post-fix heatmap — residual still ~19, not a matcher problem

**Author:** Prometheus · **Date:** 2026-07-11 · **Seat:** advise only  
**Case:** `css-selectors` · registry **known_fail** · primary VP **800×1200**  
**Pin:** PR #37 run `29141476634` / B2 head `26490c3` · native **18.965%** (still > t15)  
**Supersedes as dig map:** Atlas falsification of empty_siblings autopsy (`exchange` atlas#58) + this instrument read  
**Non-goal:** new matcher brief · specificity rewrite · threshold specials · engine code from this seat

---

## 0. Verdict (one screen)

| Claim | Status |
|-------|--------|
| Matcher / sibling combinators are the residual | **FALSE** (Atlas selector-oracle 20/20; leave closed) |
| Residual still >15 after style-truth digs | **TRUE** — **18.97%** @ native on #37 |
| Primary driver | **Form-control box metrics + cascade Y-drift** (S4 under-height → S5+ slides) |
| Secondary | Card chrome (radius/shadow AA), button paint density, list markers if any, genuine font residual |
| Atlas action | **Dig tickets below** — split, probe-first; **do not** re-open matcher |

Campaign scoreboard should keep this as `known_fail` until a dig lands under t15 on **primary VP only**. Exploit VPs (800×600 / 1280×800 = 100%) are the multi-VP gate problem already pinned in `2026-07-11-ci-gate-honesty-IMPLEMENT.md` — not this page's product residual.

---

## 1. Evidence pin (PR #37 swarm, shard-0)

| Viewport | diff% | Role |
|----------|------:|------|
| **800×1200** | **18.965** | **Native / campaign truth** |
| 800×600 | 100.0 | Exploit / non-primary |
| 1280×800 | 100.0 | Exploit / non-primary |

Attribution (native only):

- `diffPercent`: **18.965**
- Taxonomy label: 100% of attributed mass tagged `text_metrics` — **treat as instrument catch-all**, not a causal diagnosis (corner ratios 0.002–0.024 → not corner-AA dominated).
- Nested `contribution_percent` values **double-count** parent/child rects; use **section `element_diff_percent` + Chrome↔RK Y table** for ranking.

Receipt paths (CI artifact `parity-shard-0` / run `29141476634`):

- `css-selectors/800x1200/iter-1/diff/attribution.json`
- `…/diff/heatmap.png`, `diff.png`, `overlay.png`
- `…/capture/layout.json`

Local twins (may be slightly older, same ~18.97 number observed):

- `hiwave-macos/parity-baseline/diffs/css-selectors/run-1/attribution.json`

---

## 2. Section residual map (Chrome layout-rects vs RK capture layout)

Chrome body height **1545**; RK root/body **~1497** (Δ **−48 px** overall shorter).  
Sections 7–8 sit mostly **below the 1200 fold** on Chrome (S7 y=1183) — residual that can still move the meter lives in **S1–S6**.

| Sec | Content | Chrome y / h | RK y / h | Δy (RK−C) | Notes |
|----:|---------|-------------:|---------:|----------:|-------|
| 1 | Child `>` | 20 / 172 | 20.0 / 174.8 | +0 / +2.8 | Slightly tall; leaf pills 100% elem_diff under chrome rects |
| 2 | Adjacent `+` | 207 / 175 | 209.8 / 173.6 | +2.8 | High density (~32% elem_diff) |
| 3 | General `~` | 397 / 195 | 398.4 / 189.6 | +1.4 | High density (~31%) |
| **4** | **Attributes / forms** | **607 / 195** | **603.0 / 176.6** | **−4 / −18.4** | **Structural under-height** |
| 5 | Pseudo list | 817 / 236 | 794.6 / 234.4 | **−22.4** | Drift inherited from S4; list itself ~height-OK |
| 6 | `:not()` buttons | 1068 / 100 | 1044.0 / 93.4 | −24 / −6.6 | Highest local density (~42% elem_diff) |
| 7 | Chained boxes | 1183 / 160 | 1152.4 / 158.8 | −31 | Mostly below fold |
| 8 | Complex chains | 1358 / 152 | 1326.2 / 150.8 | −32 | Below fold |

**Read:** matching colors can be correct and the page still fails t15 because **form row metrics steal ~18 px of section height**, then **every later section is ~22–32 px early**. Attribution then reports 100% `element_diff` on chrome rects that no longer line up with RK paint — classic shift residue, not “selector still broken.”

---

## 3. Smoking gun detail — text `<input>` box

Fixture CSS (`websuite/cases/css-selectors/index.html`):

```css
input[type="text"] {
    border: 2px solid #4a90d9;
    padding: 8px;
    margin: 4px 0;
    width: 200px;
}
```

| | Chrome | RK (B2 capture) |
|--|-------:|----------------:|
| Input / wrapper height | **35** | **~29** (S4 child row) |
| Width | 200 | width rule present (fixture) |

Engine pin (`rustkit-layout` `layout_form_control`, TextInput arm):

```text
intrinsic_height = font_size * 1.5 + 8.0
```

On this page `body { font-size: 14px }` → **14×1.5+8 = 29**. That matches the measured RK row and **does not** reproduce Chrome’s border-box for `padding:8` + `border:2` + content (~35).

**Hypothesis (probe before patch):** form control height is treated as a single “intrinsic content” number and **does not compose CSS padding + border the way replaced/form UA boxes do**, or padding is double-booked wrong. Either way, **S4 is the first section where cumulative page height diverges hard**.

Cross-check: `form-controls@800x1200` on the same run is **9.91%** (under t15). That case is not a free pass for css-selectors — different chrome/density — but it says form work is **partially** paid and the **text-input border-box** on this fixture is still the cascade fuse.

Checkbox: fixture forces 20×20; Chrome `#check1` is 20×20. RK checkbox intrinsic is `font_size * 1.2` (**~16.8**) unless width/height CSS wins — confirm on probe; secondary to text-input height.

---

## 4. Ranked dig tickets (Atlas) — split, probe-first

**Do not combine with B2 merge, CI-1, GradientText, or Slice C.** One dig PR per mechanism when possible.

### DIG-1 — Text input border-box (highest leverage)

- **Symptom:** S4 −18 px height; S5+ Y −22…−32.
- **Probe (≤30 min):** minimal page with one `input[type=text]` + same border/padding as fixture; dump chrome vs RK border/content rects; print whether height is content-box or border-box.
- **Pass bar:** input border-box height within **±1 px** of Chrome on the probe; css-selectors S4 height within **±2 px**; re-measure native css-selectors.
- **Expected meter:** drop residual via **alignment recovery** on S5–S6, not by “fixing selectors.”
- **Code neighborhood:** `rustkit-layout` `layout_form_control` TextInput arm (~L1376–1380) + how padding/border enter `dimensions` for form controls.

### DIG-2 — Button replaced metrics / paint (S6 density)

- **Symptom:** S6 elem_diff ~42% despite small area; buttons row exists (RK h≈33 vs Chrome button h=31).
- **Probe:** three bare buttons (active / disabled / active) no card chrome; score + rect dump.
- **Pass bar:** probe under ~5% or rects ±1 px and fill colors match; then re-check S6 on full page.
- **Note:** Button width already uses measured label (`label_width + 24`); height still `font_size * 1.5 + 12` — verify against Chrome UA + author padding.

### DIG-3 — Card chrome (box-shadow + radius) — page-global soft residual

- **Symptom:** every `.section` has `border-radius: 8px` + `box-shadow: 0 1px 3px rgba(0,0,0,0.1)`.
- **Support:** `DisplayCommand::BoxShadow` + `draw_box_shadow` exist — residual may be blur sigma / alpha, not “missing feature.”
- **Probe:** one white card on `#f5f5f5` with only radius+shadow, no text.
- **Pass bar:** probe diff dominated by AA ring only; full page re-measure for soft edge contribution.

### DIG-4 — List markers / `ul` padding (Atlas ledger item)

- **Symptom:** default `ul` discs; Chrome `ul`/`li` widths are full 730 (markers in padding gutter).
- **Support:** no first-class `list-style` / `::marker` hits in a quick crate search — may still be “no markers” paint gap.
- **Probe:** 5-item `ul` with colored `li` backgrounds only; compare left gutter pixels.
- **Pass bar:** markers present or explicit `list-style: none` + matching padding if UA default deferred to QUIRKS (Pete call — prefer paint if cheap).

### DIG-5 — Font / text residual (last)

- Advance contract is live for `Text` (#36). Remaining ink delta is **single-stack font** territory.
- Only dig after DIG-1…4 if native still >15.
- No second shaper.

---

## 5. What is closed / do not reopen

| Item | State |
|------|--------|
| empty_siblings / matcher wiring | **Falsified** — oracle 20/20 (Atlas#58) |
| Inheritance / text-align / bold system font | **Shipped** #27 |
| Underline offset | **Closed** post-#27 re-probe |
| New selector grammar / specificity | **Out of scope** for this residual |
| Raising threshold for css-selectors | **Forbidden** (T6 / Pete lock) |

---

## 6. Falsification discipline (method receipt)

Previous autopsy’s “smoking gun” was a stale call-site read. This brief is **instrument-first**:

1. Swarm native number (18.97)  
2. Chrome `layout-rects.json` vs RK `capture/layout.json` Y table  
3. Form intrinsic formula reproduced at 29 px  

Every DIG ticket carries a **minimal probe** before a production patch. If a probe fails to show the claimed Δ, **kill the ticket** and re-heatmap — do not ship a theory.

---

## 7. Coordination

| Seat | Action |
|------|--------|
| **Atlas** | After #37 merge (or in dig lane parallel to CI/GradientText chores): **DIG-1 first**. Ring when PR opens for outside-eye. |
| **Athena** | Portable: form control height must compose author padding/border; Windows builtins/forms will show the same S4-class cascade if under-boxed. |
| **Prometheus** | Heatmap complete. Outside-eye on DIG PRs; no matcher brief; no merge from this seat. |
| **Pete** | Residual is dig debt, not campaign-blocker design. Holdout remains sacred; css-selectors stays KF until native ≤15. |

---

## 8. Receipts

- PR #37 Parity Gate run `29141476634` · native css-selectors **18.965%**
- Chrome layout-rects: `baselines/chrome-148/websuite/css-selectors/layout-rects.json` (body h=1545)
- RK layout: swarm capture `css-selectors/800x1200/iter-1/capture/layout.json` (body h≈1497)
- Fixture: `websuite/cases/css-selectors/index.html`
- Form intrinsic: `crates/rustkit-layout/src/lib.rs` `layout_form_control` TextInput
- Prior autopsy (historical, matcher claim falsified): `2026-07-10-css-selectors-AUTOPSY.md`
- CI multi-VP 100s: `2026-07-11-ci-gate-honesty-IMPLEMENT.md`

— Prometheus · grind tick · advise lane · no engine code · no merge
