# Cross-crate duplication audit (bug-risk focus)

**Author:** Prometheus · **Date:** 2026-07-10  
**Tree:** hiwave-macos master ~`c305ef0`  
**Method:** same-name scan across crates + semantic search (color/length/font/flex).  
**Goal:** find copies that **diverge and cause real bugs**, not rename every `new()`/`clear()`.

Same-name scan found **179** names in 2+ crates; most are benign (`get`, `clear`, trait methods). Below is the **dangerous subset**.

---

## Severity legend

| Sev | Meaning |
|-----|---------|
| **P0** | Already caused or will cause suite/bugs when one copy is fixed and the other is not |
| **P1** | High drift risk; fix soon as chore PRs |
| **P2** | Structural debt; schedule after trench green day |
| **OK** | Same name, different domains — leave alone |

---

## P0 — Fix or you will re-hit campaign bugs

### 1. CSS value parsing: engine vs css (and a toy layout copy)

| Location | What |
|----------|------|
| `rustkit-css::parse_color` | Full named/hex/rgb/hsl (~canonical after #6) |
| `rustkit-engine::parse_color` ~L4290 | **Private full reimplementation**; **9** call sites still use it |
| `rustkit-css::parse_length` | min/max/clamp/calc + units |
| `rustkit-engine::parse_length` ~L4627 | Parallel implementation (calc/min/max/clamp again) |
| `rustkit-layout::parse_length` ~L2016 | **Third** copy — only `px` / bare number; returns `f32` not `Length` |

**Why it bites:** PR #6 fixed “coral dropped” by teaching **css** more names. Engine’s private list can still drop names on paths that call local `parse_color`. Length: engine may accept `calc()` while layout’s toy parser returns `None` for `%` → silent wrong layout if used.

**Fix:**  
1. Engine: `use rustkit_css::{parse_color, parse_length, …}` and delete private island (~L4290–5370, ~**1080 lines**).  
2. Layout: delete or rename toy `parse_length`; call css + resolve, or take `Length` only.

### 2. Color interpolation: three different physics

| Location | Behavior |
|----------|----------|
| `rustkit-animation::interpolate_color` | Linear sRGB bytes + float alpha |
| `rustkit-canvas::interpolate_color` | Same idea, slightly different lerp |
| `rustkit-renderer::interpolate_color_gamma` | **Linear-light** via `srgb_to_linear` (correct for gradients) |

**Why it bites:** Gradients look “spec-ish” in renderer; CSS animations / canvas ramps look different for the **same stops**. Night digs on gradient pages can “fix” paint while animation still wrong (or the reverse).

**Fix:** One `Color::lerp(a, b, t, Space::{Srgb | Linear)` on `rustkit-css` (or small `rustkit-color` if you prefer). Animation + canvas + renderer all call it. Default gradients → Linear; animations can stay Srgb until you care.

### 3. Content-box placement formula (many sites, one bug class)

Repeated:

```text
content.x = cb.x + margin.left + border.left + padding.left
```

#22 was exactly “one path forgot border+padding.” Still appears in float L/R, absolute, block, collapse paths.

**Fix:** `LayoutBox::place_in_containing_block(&mut self, cb: &Dimensions)` — single definition.

### 4. Flex §11b vs “definite size” (no field, wrong comment)

Comment claims “only if fallback”; code grows any item with taller children. No `has_explicit_cross_size`. Axis arm can assign **height-sum → width**.

**Fix:** definite cross from `style.height`/`width`; Axis helpers (see CODE_REVIEW_SLIM.md). This is the **settings** dig.

---

## P1 — High drift, schedule chore PRs

### 5. Core Text / glyph path duplicated (layout vs rustkit-text)

`CTFontGetGlyphsForCharacters` appears in:

- `rustkit-layout/src/text.rs` (FFI + usage)
- `rustkit-text/src/macos.rs` (**four** separate `extern` blocks alone)

**Why it bites:** Font metric / shaping fixes land in one crate; the other keeps old metrics → wrap width ≠ paint width (classic “layout vs paint disagree”).

**Fix:** layout **must not** speak Core Text. Only `rustkit-text` APIs (`shape`, `measure`, `line_metrics`). Pure move PR when green.

### 6. `resolve_length` / used-value math only half-shared

- `flex.rs::resolve_length(Length, container, viewport)` for flex items  
- `lib.rs` repeated `match style.height { Px, %, Vh, Em, Rem }` in width/height/min paths  

**Why it bites:** Support `rem` in one path, forget in another → intermittent %/em bugs.

**Fix:** `Length::resolve(pct_base, font_size, viewport) -> Option<f32>` once on css or layout util.

### 7. Gradient / image color-stop parsing in engine

Engine still owns `parse_linear_gradient`, `parse_radial_gradient`, `parse_color_stop` next to the private color parser. Renderer owns corner-ellipse radii (#19 fixed **renderer** only).

**Why it bites:** Spec radii fixed in paint; style-side radial parse can still feed wrong rx/ry if duplicated.

**Fix:** Gradients are CSS values → parse in **css**, paint only samples stops. Inventory with `rg parse_.*gradient`.

### 8. Display-list / hit-test local coords boilerplate

`HitResult` / similar: `abs = border_box + local` repeated (lib.rs ~L1528–1544 twice for padding vs border hit bands).

**Fix:** tiny helpers `fn abs_point(&self) -> (f32,f32)` on hit structs.

---

## P2 — Structural / name collision noise

| Item | Notes |
|------|--------|
| HTML tree sink duplicated (`append_child`, `create_element`, …) in dom + html + tests | Often **trait impls** for different sinks — OK if one trait; bad if two trees. Prefer one `DomSink` trait. |
| `can_go_back` / navigate in app + core + engine | Facade layering; OK if thin wrappers only. Audit for divergent history logic. |
| `from_css` in image + layout | Different types (object-fit vs style mapping) — rename for clarity, not merge. |
| Generic `get`/`clear`/`parse` across crates | Ignore. |

---

## “Repeated functions that cause issues” — short list for Atlas

If you only do **three** consolidations this campaign:

1. **Engine → css for all value parsing** (color, length, gradient, shorthand_4 where possible) — max bug prevention per line deleted.  
2. **Single content-box placement + flex Axis / definite cross** — layout ghosts + settings.  
3. **Single color lerp + single text metrics owner** — paint vs animation vs wrap consistency.

---

## Suggested verification when consolidating

```bash
# After deleting engine parse_color:
rg 'fn parse_color' crates   # only css
cargo test -p rustkit-engine -p rustkit-css
# parity smoke: bg-solid, gradients, settings
```

```bash
# After text ownership move:
rg 'CTFontGetGlyphs' crates/rustkit-layout  # should be empty
```

---

## What not to merge blindly

- Two functions named `layout` in different crates — fine.  
- Cache `get`/`put` in net vs idb — fine.  
- Don’t “unify” fastrender + rustkit parsers mid-campaign.

---

## Related docs

- `CODE_REVIEW_SLIM.md` — PR-sized shrink stack  
- `forensics/2026-07-10-settings-11b-PATCH.md` — concrete flex fix  

— Prometheus
