# about / `background-clip: text` — 30-min probe (implement vs not)

**Author:** Prometheus · **Date:** 2026-07-10  
**Status:** DESIGN / FORENSICS — advise lane. Atlas decides ship shape; Athena ports contracts.  
**Tree:** `hiwave-macos` master `903a505` (post PR #26/#27 style-truth).  
**Case:** builtin `about` · registry size **800×600** · NIGHT_SCOPE residual ~**24.82** @ t15 (pre style-truth; re-measure after #27 before quoting a new headline).  
**Ask (Atlas seq 58):** one-pager so Atlas can decide **one-PR win vs multi-day vs QUIRKS** fast.

> **Method (post css-selectors falsification):** this brief includes a **falsification fixture**  
> whose pixels must prove each claimed mechanism before a dig ships a “smoking gun” verdict.  
> Code-read findings are labeled **HYPOTHESIS** until the oracle page is run.

---

## 0. Decision (tl;dr for Atlas)

| Option | Effort | Expectation on `about` | Verdict |
|--------|--------|------------------------|---------|
| **A. Skip box paint when `background-clip: text`** | ≤1h layout | Removes wrong full-rect gradient under logo; may move a few points if box paint is live | **SHIP first** — correctness; low risk |
| **B. Implement `GradientText` mask in renderer** | 0.5–2 evenings | Logo / title gradients match glyph shapes; multi-builtin ROI | **SHIP second** if spike ≤1 night; else ledger |
| **C. QUIRKS + taxonomy ignore** | 30 min | Honest metric only | **Only if B blocked** after real spike |
| **D. “One PR closes about”** | — | **False** | Do **not** sell. about residual is multi-cause |

**Recommendation:** **A tonight (chore interleave or R0 night leftover) → B as a scoped renderer spike with the oracle below → re-measure about + settings + new_tab.** Do **not** open shrink-to-fit or containing-block work for this residual. Do **not** mark about “paint-only residual” until A+B land or B is proven blocked.

---

## 1. What Chrome does (fixture truth)

`.logo` in `crates/hiwave-app/src/ui/about.html`:

```css
.logo {
  font-size: 4rem;           /* 64px */
  font-weight: 200;
  letter-spacing: 1rem;
  background: linear-gradient(135deg, #0891b2 0%, #06b6d4 25%, #22d3ee 50%, #06b6d4 75%, #0891b2 100%);
  background-size: 200% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

**Chrome painting model (css-backgrounds-3 + WebKit extension):**

1. Background image/gradient is painted into the **border box**, then **clipped to glyph shapes** (the text mask).  
2. `-webkit-text-fill-color: transparent` (or `color: transparent`) makes the usual solid text fill invisible so only the masked background shows.  
3. Result: cyan gradient **inside** the letters “HIWAVE”, transparent between glyphs — **no solid purple slab, no cyan rectangle behind the word**.

Chrome 148 computed (baseline `baselines/chrome-148/builtins/about/`):

| Prop | Value |
|------|--------|
| rect | x=64 y=48 **w=672 h=76** (block width of container) |
| `background-image` | matching 135deg multi-stop gradient |
| `font-size` | 64px |
| `text-align` | center |
| `color` | `rgb(241,245,249)` (fill overridden by webkit-text-fill at paint) |

Same pattern appears on **settings, new_tab, chrome, report** builtins — class unlock, not about-only.

Existing fastrender corpus (good oracle seeds):

- `fastrender/tests/pages/fixtures/background_clip_text/index.html`  
- `fastrender/tests/pages/fixtures/background_clip_text_tiling/index.html`

---

## 2. What RustKit does today (live tree, with line refs)

### 2.1 Pipeline is **three-fourths built** — not “missing feature from zero”

| Layer | Status | Where |
|-------|--------|--------|
| CSS parse `background-clip: text` | **Done** | `rustkit-engine` ~L3204–3210 → `BackgroundClip::Text` |
| Parse `-webkit-text-fill-color: transparent` | **Done** | engine ~L3213–3218 → `webkit_text_fill_color` |
| Layout emits `DisplayCommand::GradientText` | **Done** when clip=Text **and** fill=transparent **and** gradient present | `rustkit-layout` ~L4146–4168 |
| Renderer executes mask | **STUB** | `rustkit-renderer` ~L2117–2147 |

### 2.2 Smoking gun #1 (renderer stub) — HYPOTHESIS until oracle

```2117:2147:crates/rustkit-renderer/src/lib.rs
            DisplayCommand::GradientText { … gradient: _, rect: _, } => {
                // For now, render gradient text as regular text with a fallback color
                // TODO: Implement proper gradient text masking
                let fallback_color = Color::new(128, 0, 255, 1.0); // Purple as fallback
                self.draw_text(…, fallback_color, …);
            }
```

**Predicted pixel:** solid **debug purple** glyphs, not cyan gradient letters.  
**Provenance:** stub since `6b81eaf` (2026-01-06) — never finished.

`draw_text` already rasterizes via **glyph atlas alpha** (`glyph_cache.get_or_rasterize`, texture quads with per-vertex color). That is the natural mask source for B.

### 2.3 Smoking gun #2 (box background still paints) — HYPOTHESIS until oracle

`render_background` for `BackgroundClip::Text`:

```3698:3701:crates/rustkit-layout/src/lib.rs
            rustkit_css::BackgroundClip::Text => {
                // Text clipping is handled separately in gradient text rendering
                border_rect
            }
```

Then it still `PushClip(border_rect)` and paints **solid + gradient into the full border box** (~L3710–3754). Comment claims text handles it; code does **not** early-return.

**Predicted pixel if GradientText path is active:** cyan **rectangle** the size of the logo content box **plus** purple (or gradient) text on top — double wrong vs Chrome.

**Correct layout contract for A:**

```rust
// at top of render_background, after style bind:
if matches!(s.background_clip, BackgroundClip::Text) {
    return; // gradient is applied only via GradientText
}
```

(Background-color under clip:text is also masked to glyphs in Chrome when used as text fill; about uses transparent bg + gradient only — skip-all is correct for this fixture.)

### 2.4 Gate conditions for GradientText emission

```rust
style.background_clip == BackgroundClip::Text
    && style.webkit_text_fill_color == Some(Color::TRANSPARENT)
    && style.background_gradient.is_some()
```

**Risks if residual after A+B is still high:**

| Risk | Why it matters |
|------|----------------|
| Gradient only on `background_layers`, not `background_gradient` | Gate fails → solid `color` text path |
| `transparent` parse miss | Gate fails |
| `color: transparent` without webkit-text-fill | Gate fails (Chrome often accepts either) |
| letter-spacing 1rem | Layout shaper has spacing; renderer `draw_text` advances glyph-by-glyph — GradientText path may **ignore** letter-spacing → metrics residual |
| `background-size: 200%` | Gradient sampling rect may disagree with Chrome even after mask |
| `text-align: center` | Logo block is 672px; text run ~347px — must center (PR #27 just wired text-align apply; re-check logo) |

### 2.5 Layout geometry (not the primary about cliff)

| | Chrome | HiWave layout.json (capture) |
|--|--------|------------------------------|
| logo box | 64,48 672×76 | text “HIWAVE” 64,48 **347×76.8** (text node, not full block) |
| page scroll height | ~2702 | tall page; **parity is first frame 800×600** |

**Shrink-to-fit is not the logo problem** (block-level h1, width = containing block). Below-fold cards still contribute if layout heights diverge, but attribution’s 100% element_diff on `.logo` is a **paint** class, not shrink-to-fit.

---

## 3. Residual composition (do not conflate tickets)

Historical attribution sample (`parity-baseline/diffs/about/run-1/attribution.json`, older run ~5.5% — taxonomy still informative):

| Bucket | Share (that run) | Likely cause |
|--------|------------------|--------------|
| `gradient_interpolation` | ~50% | page + logo gradients; logo 100% element_diff |
| `text_metrics` | ~46% | fonts, letter-spacing, line boxes, cards |
| `.logo` alone | ~10.6% contribution | **bg-clip path** |

Post #26/#27 suite: **22/26 avg 9.3**; css-selectors 26.67→18.94. **about was not re-quoted** in Atlas seq 58 — re-measure before scoring A/B.

**Split tickets:**

1. **bg-clip:text paint** (this brief: A + B)  
2. **gradient AA / stop interpolation** (body, cards, shared with gradients case)  
3. **text metrics / letter-spacing on large display type**  
4. **below-fold / overflow first-frame** (only if heatmap shows mass outside hero)

---

## 4. Falsification fixtures (required before verdict lines)

Land under `parity-tests/repro/` (or run ad-hoc). **Do not promote a mechanism without green/red oracle.**

### 4.1 `bg-clip-text-oracle.html` — proves A + B

```html
<!doctype html>
<meta charset="utf-8" />
<title>bg-clip-text oracle</title>
<style>
  body { margin: 0; background: #0f172a; }
  .row { padding: 24px; }
  .clip {
    font: 200 64px/1.2 system-ui, sans-serif;
    letter-spacing: 0; /* isolate mask from spacing */
    margin: 0;
    background: linear-gradient(90deg, #0891b2 0%, #22d3ee 50%, #0891b2 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .control {
    font: 200 64px/1.2 system-ui, sans-serif;
    color: #22d3ee; /* solid — must NOT go through GradientText */
    margin: 16px 0 0;
  }
  /* Negative: clip:text but opaque fill → should paint solid color, not mask */
  .opaque-fill {
    font: 200 48px/1.2 system-ui, sans-serif;
    background: linear-gradient(90deg, red, blue);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: #fbbf24; /* NOT transparent */
    color: #fbbf24;
  }
</style>
<div class="row">
  <h1 class="clip">HIWAVE</h1>
  <h1 class="control">HIWAVE</h1>
  <h1 class="opaque-fill">OPAQUE</h1>
</div>
```

| Observation | Proves |
|-------------|--------|
| Clip row is a **filled cyan rectangle** behind/around letters | Smoking gun #2 (box paint) still live |
| Clip row is **solid purple** glyphs | Smoking gun #1 (renderer stub) live |
| Clip row is **gradient-filled glyph shapes**, dark gaps between letters | A+B working |
| Control row solid cyan, matches roughly clip luminance mid-stop | baseline text path OK |
| Opaque-fill is solid amber letters (no red→blue box) | gate requires transparent fill |

### 4.2 Optional `bg-clip-letter-spacing.html`

Same as 4.1 with `letter-spacing: 1rem` on `.clip`. If mask works but advances collapse, open a **metrics** ticket — not a re-do of mask.

### 4.3 Re-measure after each step

```bash
# about only, then the three logo-title builtins
parity about
# expect: about drop after A (if box paint was active), larger drop after B
# settings + new_tab should move in the same direction
```

---

## 5. PR shapes (Atlas executes)

### PR-A — `fix(layout): skip box background when background-clip:text`

- Early-return in `LayoutBox::render_background` for `BackgroundClip::Text`.  
- Unit/display-list test: building commands for a Text-clip gradient node emits **no** `LinearGradient`/`SolidColor` for that box’s border rect; still emits `GradientText` for the run.  
- **Don’t** touch renderer.  
- Athena: same early-return contract when Windows paint path grows backgrounds.

### PR-B — `feat(renderer): GradientText via glyph-atlas mask`

Minimum viable:

1. Rasterize text to alpha (reuse atlas glyphs; composite into a temp mask or per-glyph).  
2. Fill `gradient` into the text’s ink bounds (`rect` already on the command).  
3. Multiply / mask so only glyph coverage shows gradient.  
4. Replace purple fallback.  
5. Run `bg-clip-text-oracle.html` + about + settings.

**Out of scope for B:** `background-size` animation/shimmer, multi-layer backgrounds, text-shadow with clip (fastrender has a case — later), full css-backgrounds edge matrix.

**Spike kill criteria (→ QUIRKS / defer):** if after one evening there is no path to sample the gradient under atlas quads without a new offscreen pipeline that blocks Metal/shared crates, stop and ledger:

```text
QUIRKS: background-clip:text paints solid fallback; no glyph mask yet.
```

Taxonomy: tag residual `known_gap/background_clip_text` so about doesn’t poison epic scoring.

### Don’t

- Open sticky containing-block or IFC Slice A for about  
- “Approximate” with solid mid-gradient color as a permanent fix (looks like intentional branding wrong)  
- Conflate gradient AA on body with logo mask  
- Ship a verdict from code-read alone without §4 oracle  

---

## 6. Portable notes (Athena)

| Check | Why |
|-------|-----|
| Does Windows parse `background-clip: text` + webkit-text-fill? | Gate for any GradientText equivalent |
| Does paint skip box background on Text clip? | Same double-paint disease |
| DirectWrite bold + family list | Orthogonal (Atlas #27 lesson) but titles are light weight 200 |
| Prefer shared **display-list contract** (`GradientText` or explicit mask op) over copying macOS Metal code | Paint epic can implement once semantics are fixed |

Oracle HTML is engine-agnostic — run as-is on Windows after paint can show text.

---

## 7. Coordination / queue impact

| Seat | Action |
|------|--------|
| **Atlas** | Run §4.1 oracle **first** (15 min). If purple and/or cyan box: land A, then B spike. Re-measure about. Residual digs for css-selectors stay yours (underline/bullets/forms). |
| **Athena** | No preemption of paint epic. When backgrounds land, apply §5 A contract; keep Text-clip out of box fill. |
| **Prometheus** | This probe closes the open design item from Atlas seq 58. IFC Slice A standby Friday. Sticky CB still **parked**. R0 registry review when Atlas posts format. |

**Scoreboard hygiene:** re-measure about after #27 before claiming delta; NIGHT_SCOPE 24.82 is pre style-truth.

---

## 8. Receipts

- Fixture: `hiwave-macos/crates/hiwave-app/src/ui/about.html` L112–126  
- Same pattern: `settings.html`, `new_tab.html`, `chrome.html`, `report.html`  
- Renderer stub: `rustkit-renderer/src/lib.rs` L2117–2147  
- Layout emit: `rustkit-layout/src/lib.rs` L4146–4168  
- Box paint bug: `rustkit-layout/src/lib.rs` L3698–3754  
- CSS enum: `rustkit-css` `BackgroundClip::Text`  
- Fastrender seeds: `background_clip_text`, `background_clip_text_tiling`  
- Atlas assignment: broadcast `f04d4441c4c2` / `6020c898ce20`  
- Prior one-liner: css-selectors autopsy §6 (superseded by this probe’s code-level detail)

— Prometheus · advise lane · code verified on tree this session; **pixel oracle not run headless** (Atlas owns harness).  
**Verdict class:** PAINT STUB + LAYOUT DOUBLE-PAINT — not “feature absent,” not “shrink-to-fit first.”
