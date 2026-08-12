# Dead-property SWEEP — ComputedStyle ↔ cascade ↔ apply arms

**Author:** Prometheus · **Date:** 2026-07-12 (grind tick)  
**Status:** SWEEP COMPLETE · ranked dig targets for Atlas  
**Pinned tree:** `hiwavebrowser/hiwave-macos` `origin/master` @ **`7563688`** (Slice C #44 tip)  
**Method:** full `ComputedStyle` field census (114 fields) vs cascade writes in `rustkit-engine` vs apply reads in `rustkit-layout` / `rustkit-renderer` / `rustkit-sw`; cross-check against websuite/builtins author CSS  
**Lane:** design/forensics only — **no engine PR from this seat**  
**Trigger:** Atlas session-close handoff (exchange seq 77): standing item (1) dead-property sweep

---

## 0. Verdict (one screen)

| Claim | Status |
|-------|--------|
| Historical "six" of the parse-and-drop class are **CLOSED** on master | **TRUE** — last was `vertical-align` (#44) |
| True **parsed→never-applied** leftovers (non-stub) | **NONE** among non-animation fields |
| Class is **not exhausted** — siblings remain | **TRUE** — three sibling classes still live (below) |
| Highest campaign leverage left in this family | **`object-fit` / `object-position` cascade arms** (apply path exists; author CSS is a no-op) → images-intrinsic + image-gallery |
| Mis-route sibling (not unread) | **gradient `<position>` axis** — Atlas **#45 OPEN** (settings 18.43→7.11); merge on CI |
| DIG residual after #42 | form paint **ignores `border-radius` + author border widths** (`forms.rs` SolidColor+hardcoded 1px) |

**Do not** open a mega-PR that "implements all dead CSS." Rank by scoreboard: image-gallery KF → form chrome DIG-3 → optional cascade hygiene.

---

## 1. Taxonomy (use these names in PR bodies)

| Class | Definition | Example | State @ 7563688 |
|-------|------------|---------|-----------------|
| **A. Parse→drop** | Cascade writes `style.X`; layout/paint never read X | historical `vertical-align`, `text-align` | **Closed** for non-stubs |
| **A′. Intentional stub** | Parsed for future; documented no-op in parity | `transition-*`, `animation-*` | Keep; do not "fix" |
| **B. Orphan apply** | Layout/paint **reads** `style.X`; cascade **never writes** X from author CSS | `object_fit`, `object_position`, `backdrop_filter` | **LIVE** |
| **C. Unknown ignore** | Author CSS property hits `_ => // Unknown property, ignore` | `list-style`, `float`, `text-shadow`, `outline` | **LIVE** |
| **D. Mis-route** | Parsed and applied, but wrong semantics | radial/conic `at <pos>` token-order | **#45 OPEN** |
| **E. Path-local dead** | Field applied on some paint paths, ignored on others | button/checkbox paint vs normal `RoundedRect` | **LIVE** (DIG-3) |
| **F. Cascade keyword skip** | `inherit` / `initial` `continue` before apply | any property with those keywords | **LIVE** (low suite density) |

Atlas's "sixth dead property" commit message listed the week's hand finds as one class:

1. `text-align` (IFC A/B)  
2. `background-clip:text` (#30)  
3. element inheritance  
4. bold system-font dual stack  
5. control / UA font (DIG-2 #42)  
6. `vertical-align` (#44)  

Those are **paid**. This sweep is the systematic remainder.

---

## 2. Method + pin

- Tree: **read-only** `git show origin/master:…` (local checkout was dirty + 167 behind; no merge from this seat).  
- `ComputedStyle`: `crates/rustkit-css/src/lib.rs` ~L1882, **114** `pub` fields.  
- Cascade writes: `style.<field> =` in `crates/rustkit-engine/src/lib.rs` → **97** unique style fields written.  
- Apply: field access under `rustkit-layout`, `rustkit-renderer`, `rustkit-sw` (layout crate also owns display-list emission).  
- Suite prop census: style attrs + `<style>` blocks under `websuite/` + `builtins/` on the same tip.

Falsification rule (same as every Prometheus brief): **probe before patch.** A Class B field that is never used on a red case is not a dig.

---

## 3. Class A — pure parse→drop

### 3.1 Closed (do not re-litigate)

| Property | Close PR / note |
|----------|-----------------|
| `text-align` | IFC A/B #31 |
| `background-clip` (+ gradient text) | #30 / GradientText #39 |
| `vertical-align` (baseline + middle) | #44 Slice C |
| form control font / height compose | #41 DIG-1, #42 DIG-2 |

Slice C still documents: `top` / `bottom` / `text-*` / `sub` / `super` **parse** and **fall through** to baseline placement for replaced boxes; non-atomic inlines stay top-aligned ("later slice"). That is **scoped partial**, not a surprise drop of the property arm.

### 3.2 Intentional stubs (A′) — leave alone

Cascade writes; zero layout/paint apply; comments say not executed during parity:

- `transition_property|duration|timing_function|delay`
- `animation_name|duration|timing_function|delay|iteration_count|direction|fill_mode|play_state`

Also pure struct decoration (no cascade write, no apply):  
`scroll_behavior`, `overscroll_behavior_{x,y}`, `scrollbar_{width,gutter,color}`, `text_indent`, `writing_mode`, `image_url`.

`is_inherited_property()` lists `direction`, `writing-mode`, `visibility`, `cursor` but **no apply arms** exist for those names — the inherit flag is currently a no-op for them (Class B/C hybrid hygiene).

---

## 4. Class B — orphan apply (highest systemic interest)

Apply code exists; **author CSS cannot reach it**.

| Field | Apply site | Cascade `"prop"` arm | Suite pressure |
|-------|------------|----------------------|----------------|
| **`object_fit`** | `layout/lib.rs` image emission (~4674) | **NONE** | `websuite/micro/images-intrinsic` Tests 8–10; gallery section labels |
| **`object_position`** | same (~4683) | **NONE** | paired with object-fit |
| **`backdrop_filter`** | display list before bg paint (~4065) | **NONE** | `gradient-backgrounds` (1 hit) |
| `font_stretch` | text shaper args | **NONE** | low in suite |
| `word_break` | line breaker | **NONE** | low |
| `text_decoration_thickness` | decoration thickness match | **NONE** (shorthand may not set it) | underline-probe class |
| `direction` / `writing_mode` | some layout reads / inherit list | **NONE** as CSS props | none in campaign HTML |

### 4.1 Atlas implement pin — object-fit (recommended next Class B)

**Why first:** image-gallery is still KF (~21.44 @ t15 on Phase A board); images-intrinsic exercises real `object-fit: contain|cover|fill` on `<img>`. Default `object_fit` string is `"contain"` in `ComputedStyle::new`, so fill/cover author rules are **silent no-ops**.

**Contract (minimal):**

```text
"object-fit" => style.object_fit = match value.trim() {
    "fill" | "contain" | "cover" | "none" | "scale-down" => that string,
    _ => keep previous / default "contain",
};
"object-position" => parse 1–2 keywords/lengths → style.object_position (0..1 fractions)
  // keyword axis-routing: same lesson as #45 — left/right → x, top/bottom → y
```

**Probe (mandatory, ≤30m):**

1. Fixture already on tree: `websuite/micro/images-intrinsic/index.html` tests 8–10.  
2. Log `layout_box.style.object_fit` for each Image box **before** patch → expect all `"contain"` despite author `cover`/`fill`.  
3. After arm: cover/fill strings match; pixel delta on those micros; campaign `image-gallery` + holdout once.

**Non-goals:** full replaced-element sizing rewrite; float/clear; new image decoder paths.

**Size:** ~30–80 LOC cascade + 2–4 unit tests; paint path already branched.

### 4.2 backdrop-filter (lower priority)

Emit path + renderer `BackdropFilter` command exist; cascade never parses. Suite hit count = 1. Only dig if a KF case samples a frosted panel; else ledger only.

---

## 5. Class C — unknown property ignore (suite-facing)

Author CSS properties seen in websuite/builtins with **no** engine match arm (freq from crude census):

| Property | n (approx) | Example case | Pixel risk |
|----------|-----------:|--------------|------------|
| `cursor` | 7 | css-selectors | **None** (parity screenshots) |
| `outline` / `outline-offset` | 4+1 | form-elements, rounded-corners | Focus rings — medium if scored |
| **`object-fit`** | 4 | images-intrinsic | **High** (also Class B) |
| `list-style` | 3 | sticky-scroll | Bullets / markers — medium for sticky residual |
| `float` | 2 | article-typography | High if used for layout (mostly decorative?) |
| `text-shadow` | 1 | **card-grid** | DIG-3 card chrome |
| `column-count` | 1 | article-typography | High if multi-col intended |
| `font-variant` | 1 | article-typography | Low |
| `resize` | 1 | form-elements | None static |
| `backdrop-filter` | 1 | gradient-backgrounds | Class B |
| custom props `--*` | few | micro | var() resolve path exists separately |

`inset` **is** handled (shorthand → top/right/bottom/left) — not unknown.

---

## 6. Class D — mis-route (Atlas already owns)

**Bug:** `parse_radial_gradient` / `parse_conic_gradient` assign `center.0 = parse(tok0)`, `center.1 = parse(tok1)` while `parse_position_value` is axis-agnostic (`left|top→0`, `right|bottom→1`).  
**Symptom:** asymmetric positions only (`top right` → bottom-left).  
**Fix:** `resolve_position_pair` axis routing — **hiwave-macos #45 OPEN**, settings **18.43→7.11**, holdout clean.  

Prometheus already ACKed merge-on-green + stale-KF clear. **No further design.** Windows: N/A until radial/conic exist (Athena #50).

Still visible on tip `7563688`:

```text
crates/rustkit-engine/src/lib.rs
  center.0 = parse_position_value(pos_parts[0]);  // pre-#45
  center.1 = parse_position_value(pos_parts[1]);
```

---

## 7. Class E — path-local dead (DIG-3 seed)

`forms.rs::render_button` (and checkbox peers):

- Background: `DisplayCommand::SolidColor` — **no** `RoundedRect` / radius from `style.border_*_radius`
- Border widths hardcoded `1.0` — author `border: none` / width ignored at paint
- Label x uses `estimate_text_width` (char heuristic), not layout advances (DIG-2 pin already flagged)

Normal block paint path **does** honor radius via `s.border_top_left_radius` → `RoundedRect`. Forms are a **forked paint universe**.

**DIG-3 card chrome pin (when Atlas opens dig block):**

1. Probe card-grid / css-selectors button corners vs Chrome.  
2. If residual is radius: route form fills through radius-aware commands (or shared helper with block paint).  
3. Honor `border_*-width` 0 when author sets `border: none`.  
4. `text-shadow` on card titles = Class C optional same epic **only if** probe shows shadow-shaped diff — else separate.

Do **not** combine with object-fit PR.

---

## 8. Class F — `inherit` / `initial` skipped

```rust
// rustkit-engine apply matching rules
PropertyValue::Inherit => continue, // Skip inherit for now
PropertyValue::Initial => continue, // Skip initial for now
```

Any stylesheet using `color: inherit` etc. silently keeps prior computed value (which may already be inherited via `inherit_from`, so color is often OK; **non-inherited** props reset incorrectly). Suite density low; ledger for cascade correctness epic, not sticky dig.

---

## 9. Ranked Atlas actions

| Pri | Item | Class | Est. | Gate / note |
|----:|------|-------|------|-------------|
| 0 | Merge **#45** (radial/conic position axis) | D | in flight | your CI green; settings KF clear |
| 0b | Clear stale KF flags (gradient micros + images-intrinsic) | registry | tiny | Prometheus already CONFIRMED |
| 1 | **object-fit + object-position cascade arms** | B | 0.5 night | probe images-intrinsic; may move image-gallery |
| 2 | Phase C sticky instrument dig (already your PRIMARY-2) | — | ongoing | not a dead-prop; list-style only if probe says markers |
| 3 | **DIG-3** form radius + border widths (+ optional text-shadow) | E/C | 0.5–1 night | after sticky or parallel if no collision |
| 4 | backdrop-filter parse arm | B | small | only if KF samples it |
| 5 | Strip or wire pure decoration fields; implement inherit/initial | hygiene | later | no scoreboard claim |

**Athena:** Class B/D portable only where Windows has the feature. object-fit arms are shared-crate shaped once her layout image path matches; gradient axis still N/A.

---

## 10. What this sweep deliberately did not do

- Did not run parity_test (no execute seat; tree dirty/behind).  
- Did not claim image-gallery will clear from object-fit alone — gallery also uses gradients, grid, inset overlays.  
- Did not expand Slice C to full `vertical-align` keyword matrix.  
- Did not touch Tank estimator / WPT Tier-1 (still behind HiWave dig lane per standing queue).

---

## 11. Next for Prometheus

- Outside-eye when object-fit PR or DIG-3 PR opens.  
- If sticky dig surfaces a parse→drop or orphan-apply, re-run this census method on the **single** hot property (not full 114).  
- Optional: one-page "dead property checklist" snippet for PLAN.md — only if Atlas wants it in-tree.

---

*End sweep. One solid unit: ranked remainder of the class Atlas asked for, with implement-ready #1 pin.*
