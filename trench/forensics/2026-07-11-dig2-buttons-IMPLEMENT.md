# Implement brief: DIG-2 — button metrics + paint (css-selectors residual)

**Author:** Prometheus · **Date:** 2026-07-11 (grind tick)  
**Status:** IMPLEMENT-READY for Atlas · ~0.5–1 night · probe-first  
**Extends:** `2026-07-11-css-selectors-post-fix-HEATMAP.md` §DIG-2 · DIG-1 PR #41  
**Pinned tree:** `hiwave/hiwave-macos` @ `740656c` (master tip = #37–#41 wave; DIG-1 content `b6be5b3`)  
**Lane:** dig chore — **parallel OK with Slice C**; do **not** combine into one PR with C, DIG-3 card chrome, or matcher work  
**Non-goal:** engine work from this seat · raise KF · re-open selector matching · Slice C implement

---

## 0. Verdict (one screen)

| Claim | Status |
|-------|--------|
| DIG-1 closed text-input / select border-box composition | **TRUE** (#41) — css-selectors **18.94 → 16.65** |
| Residual still > t15 | **TRUE** — **16.65** native; headroom to clear = **~1.65 pts** |
| DIG-2 primary mechanism | **Button height still uses pre-DIG-1 blob; not on `single_line_box`** |
| Height math (fixture @ 14px) | RK blob **33** (`fs*1.5+12`); Chrome **31**; compose pad → **31** exact |
| Secondary (same PR only if probe shows it) | Width `label_w+24` vs author `padding: 8px 16px` (=32 H); paint **ignores** `border_radius`; label center uses **char×0.5** not layout measure |
| Atlas action | **Probe ≤30m → height compose on Button (+ flex twin) → re-measure; paint only if residual still S6-dense** |

Campaign: keep `css-selectors` KF until **primary VP native ≤15**. Ceiling 20 has **3.3pt** headroom post-DIG-1 — under-t15 clear is the product goal, not ceiling gaming.

---

## 1. Why DIG-2 is separate from DIG-1

DIG-1 (`b6be5b3`) introduced `single_line_box` and applied it to **TextInput + Select only**:

```rust
// layout_form_control @ master ~1415–1426
FormControlType::Button { label, .. } => {
    let label_width = measure_text_advanced(...).width;
    (label_width + 24.0, font_size * 1.5 + 12.0)  // ← height STILL blob
}
```

That is intentional isolation (DIG-1 commit message: bare blob preserved for form-controls UA look). Buttons with **author vertical padding** on css-selectors S6 never got the compose path. Heatmap S6 was already the densest section (~42% elem_diff); post-DIG-1 alignment recovery on S5–S6 reduced cascade noise but left button-local residual.

**Do not** re-open TextInput/Select. **Do not** change bare-blob path for zero-author-pb controls (form-controls case depends on it — stayed **9.91** through DIG-1).

---

## 2. Fixture + Chrome pins (instrument-first)

### Fixture (`websuite/cases/css-selectors/index.html` S6)

```css
* { box-sizing: border-box; }
body { font-size: 14px; ... }
.buttons button:not(.disabled) {
    background: #007bff; color: white;
    border: none; padding: 8px 16px; margin: 4px; cursor: pointer;
}
.buttons button.disabled {
    background: #ccc; color: #666;
    border: none; padding: 8px 16px; margin: 4px;
}
```

DOM: three `<button>` — active / disabled / active. Matcher for `:not(.disabled)` is **closed** (oracle 20/20); residual is metrics/paint.

### Chrome layout-rects (`baselines/chrome-148/websuite/css-selectors/layout-rects.json`)

| Button | x | y | w | h |
|--------|--:|--:|--:|--:|
| Active (blue) | 39 | **1118** | 148.33 | **31** |
| Disabled (grey) | 199.1 | 1118 | 164.63 | **31** |
| Another Active | 375.5 | 1118 | 155.75 | **31** |

Pre-DIG-1 heatmap: RK button row height **~33** (matches blob). Post-DIG-1: S4 height recovered; **re-pin RK button rects on tip before patch** (Y of S6 will have shifted vs 1118).

### Height formula table @ font_size=14

| Path | Formula | Result |
|------|---------|-------:|
| Current Button blob | `fs*1.5 + 12` | **33** |
| Chrome measured | — | **31** |
| DIG-1 compose with author pad (pad 8+8, border 0) | `(fs+1) + author_pb_v` | **31** |
| Bare blob (no author pad) — keep | `fs*1.5 + 12` | 33 (UA-ish) |

**Hypothesis H1 (primary):** routing Button height through the same `single_line_box` already in `layout_form_control` collapses Chrome Δ to ±1 on the probe.

**Hypothesis H2 (width, secondary):** intrinsic width uses `label_width + 24` while author horizontal padding is **32** (`16+16`). Chrome content≈width−32 under border-box. Compose: `label_width + author_pb_h` when author_pb_h>0, else `label_width + 24` blob. Probe will show if width is product residual or noise.

**Hypothesis H3 (paint, tertiary):** `draw_button` takes `border_radius` but **ignores it** (`_border_radius`); label centering uses `label.len() * font_size * 0.5` instead of layout measure — advance-contract cousin for buttons. Only open if after H1(+H2) S6 density remains high with rects aligned.

---

## 3. Probe contract (≤30 min, mandatory before production patch)

Commit a minimal fixture next to DIG-1's probe:

`parity-tests/repro/button-metrics-probe.html`

```html
<!DOCTYPE html>
<html><head><style>
* { margin:0; padding:0; box-sizing: border-box; }
body { background:#fff; font-family: -apple-system, sans-serif; font-size: 14px; padding: 20px; }
button.author {
  background: #007bff; color: white; border: none;
  padding: 8px 16px; margin: 4px;
}
button.bare { margin: 4px; } /* no author pad — UA blob path */
</style></head>
<body>
  <button class="author">Active Button (blue)</button>
  <button class="author" disabled>Disabled Button (grey)</button>
  <button class="bare">Bare</button>
</body></html>
```

**Pass bar (layout, before paint polish):**

| Control | Chrome target | RK after fix |
|---------|---------------|--------------|
| `.author` height | **31 ±1** | must meet |
| `.author` width | Chrome ±2 (label-dependent) | aim; do not block height ship if only width off by ≤4 |
| `.bare` height | leave near current blob / form-controls class | **must not regress form-controls beyond +0.5 pts** |

Dump chrome layout-rects vs RK capture layout for the three buttons. If H1 fails to move author height toward 31, **kill H1** and re-heatmap — do not ship a theory.

---

## 4. One-night steps (ordered)

### Step A — Height compose on Button (expected whole fix)

In `layout_form_control` Button arm, reuse existing `single_line_box` / `author_pb_v` (already computed above the match):

```rust
FormControlType::Button { label, .. } => {
    let label_width = measure_text_advanced(
        label,
        &self.style.font_family,
        font_size,
        self.style.font_weight,
        self.style.font_style,
    )
    .width;
    // DIG-2: same author-pad compose as TextInput/Select (heatmap DIG-2)
    let author_pb_h = { /* pad_left+pad_right + border_left+border_right, same px() helper */ };
    let width = if author_pb_h > 0.0 {
        label_width + author_pb_h
    } else {
        label_width + 24.0
    };
    (width, single_line_box(font_size * 1.5 + 12.0))
}
```

**Order preference if time-split:** land **height only** first if width needs a longer fight; height alone may be enough for the t15 clear.

### Step B — flex.rs twin (required if A lands)

`crates/rustkit-layout/src/flex.rs` still hardcodes Button cross/main intrinsics:

- ~1050: `Button => font_size * 1.5 + 12.0`
- ~1354 / ~1458: Button main/cross axes

Mirror the compose rule (or call shared helper) so flex-laid buttons do not reintroduce S4-class drift on form-elements / flex pages. **No new dual truth.**

### Step C — Unit / probe receipt

- Probe heights in PR body (rk vs chrome numbers).
- Existing layout unit suite green.
- Optional: one unit asserting Button with `padding: 8px 0` + `border: none` + fs=14 → height 31.0 (or within f32 tol).

### Step D — Re-measure (product gate)

| Case | Expect |
|------|--------|
| css-selectors native 800×1200 | **≤15** preferred; if still >15, report S6 elem_diff + button rect table before opening DIG-3 |
| form-controls | **no regress** >0.5 pts (bare blob path) |
| form-elements | stable or better (DIG-1 already 5.25→4.23) |
| holdout 6/6 | steady |

### Step E — Paint only if still needed (same PR only if small; else DIG-2b)

`rustkit-renderer` `draw_button` (~4114):

1. **`_border_radius` is unused** — either draw rounded fill when radius>0 (prefer existing `draw_rounded_rect` path) **or** stop advertising radius from layout until real. Fixture has no author radius (layout emits hardcoded `4.0` on Button command) — **hardcoded 4 vs Chrome UA square/rounded mismatch** can keep soft AA residual after rects match.
2. Label center: replace `label.len() as f32 * font_size * 0.5` with layout-measured width (pass advance sum or label_width on `DisplayCommand::Button`, same spirit as advance contract). Char×0.5 will mis-center proportional labels even when the box is correct.

**Rule:** if after A–D native ≤15, **stop** — do not paint-polish for vanity. If rects ±1 and native still >15 with S6 density, then E.

---

## 5. What not to do

| Forbidden | Why |
|-----------|-----|
| Touch matcher / `:not()` | Oracle closed; residual is metrics |
| Raise css-selectors KF or max-diff | T6 lock |
| Combine with Slice C | Different epic; C is vertical-align baseline |
| Combine with DIG-3 card shadow | Separate mechanism; own probe |
| Apply compose when `author_pb_v == 0` | Regresses form-controls bare UA blob |
| Second text shaper for button labels | Layout already measures; paint places |
| Merge from Prometheus | Advise lane only |

---

## 6. Coordination

| Seat | Action |
|------|--------|
| **Atlas** | DIG-2 from this brief (parallel to C0/C1/C2 OK as **separate** PR). Ring outside-eye when PR opens. |
| **Athena** | Portable: Button height/width must compose author padding/border the same way as TextInput after DIG-1; flex twin required if Windows form path diverged. |
| **Prometheus** | Outside-eye when open; no engine code this tick. |
| **Pete** | Dig debt on the path to clear css-selectors KF; not a design epic. |

### Sequencing vs live epics

```
Slice C  ──────────────────────────►  (IFC baseline / middle)
DIG-2    ──► (this brief)  ──►  optional DIG-3 card chrome
           parallel OK, separate PRs
```

If C blocks on probe, DIG-2 remains highest dig leverage for campaign residual.

---

## 7. Receipts / pins

- Master tip: `740656c` · DIG-1: `b6be5b3` / PR #41  
- Heatmap: `trench/forensics/2026-07-11-css-selectors-post-fix-HEATMAP.md`  
- Fixture: `websuite/cases/css-selectors/index.html` S6  
- Chrome rects: `baselines/chrome-148/websuite/css-selectors/layout-rects.json` (buttons h=31 @ y=1118 pre-shift)  
- Layout: `crates/rustkit-layout/src/lib.rs` `layout_form_control` Button arm ~1415  
- Flex twin: `crates/rustkit-layout/src/flex.rs` ~1050 / ~1354 / ~1458  
- Paint: `crates/rustkit-renderer/src/lib.rs` `draw_button` ~4114 (`_border_radius`, char×0.5 center)  
- DIG-1 probe pattern: `parity-tests/repro/input-borderbox-probe.html`  
- Post-DIG-1 scoreboard (Atlas #41): css-selectors **16.65**, form-controls **9.91** steady, holdout 6/6  

---

## 8. Outside-eye checklist (when PR opens)

1. Button height uses `single_line_box` (or equivalent); bare path unchanged when author_pb==0.  
2. flex.rs not left on the old blob for Button.  
3. Probe HTML committed; PR body has chrome vs RK numbers.  
4. form-controls not regressed; holdout still 6/6.  
5. No matcher / threshold / Slice C files in the diff.  
6. Paint changes only if justified by post-layout residual.

— Prometheus · grind tick · advise lane · no engine code · no merge
