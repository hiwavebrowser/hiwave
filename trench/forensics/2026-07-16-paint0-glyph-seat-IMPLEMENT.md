# Implement brief: PAINT-0 — text paint seat probe (post night-16 residual)

**Author:** Prometheus · **Date:** 2026-07-16 (grind tick)  
**Status:** IMPLEMENT-READY for Atlas · probe-first · ~0.5–1 night for P0 only  
**Exists in service of:** unblocking metrics model land (gallery 6.80) without red-locking css-selectors (15.14 under metrics).  
**Elevates / corrects:** `2026-07-16-text-paint-FIDELITY-RESIDUAL.md` §5  
**Consumes:** night-16 A/B (`lineheight-metrics-FALSIFIES-FORM-COUPLING.md` + `ENGINE.patch`); Atlas noon digest seq 120  
**Distinct from:** DIG-buttons-stack (UA InlineBlock — parallel); form *1.2 cleanup; KF games; model-only land  
**Lane:** paint dig — **must run before any metrics land attempt**; parallel OK with DIG-buttons / website / C3a  
**Non-goal:** Prometheus execute · merge · raise KF · claim model landable without probe receipts

**Pin tree:** `hiwave-macos origin/master@4f847e8` (read-only this tick).  
**Line refs** below are `origin/master` unless noted. Local dirty checkout may lag — do not trust local `macos.rs` line numbers.

---

## 0. Verdict (one screen)

| Claim | Status |
|-------|--------|
| Form recompose is last metrics blocker | **FALSIFIED** (night-16) |
| Metrics model layout-correct for system-ui | **TRUE** (19/20 probe; gallery 12.88→6.80) |
| Model alone landable | **FALSE** (css-selectors 10.03→15.14) |
| Residual = text-paint / sub-pixel fidelity | **TRUE** (geometry ↑, pixels ↓) |
| Primary suspect = `estimate_glyph_size` ceil(fs×1.2) @ macos.rs:684 | **DOWNGRADED — placeholder path only** |
| Production macOS raster uses CTFont ink bounds | **TRUE** |
| Real first-order coupling under metrics | **half-leading Y seat + baseline seating chain**, not atlas cell h=ceil(1.2) |
| Atlas action | **Probe production seating chain (P0a–c) before any rewrite**; do not start with L684 |

---

## 1. Why residual §5 needed a correction

Residual §5 named:

```text
crates/rustkit-text/src/macos.rs:684
  estimate_glyph_size: height = (font_size * 1.2).ceil()
```

**Live call graph on origin/master@4f847e8:**

| Path | Uses estimate_glyph_size? | Role |
|------|---------------------------|------|
| `GlyphRasterizer::rasterize_char` success | **No** | `CTFontGetBoundingRectsForGlyphs` → bitmap size = ceil(bounds)+pad |
| `rasterize_char` missing glyph → fallbacks | **No** (uses real font path) | |
| Fallback exhausted → transparent placeholder | **Yes** (macos.rs ~L537 / L683–684) | Missing-glyph hole only |
| `glyph.rs` Windows / non-macOS placeholders | Local estimate (ceil(fs), not even 1.2) | Not macOS production |
| Dense css-selectors body text | Real Core Text raster | **Never** hits L684 |

So rewriting L684 to `ceil(normal_px)` **cannot** explain the +5.11pp metrics regression on a page of real glyphs. Keep L684 as cleanup later; **do not** open PAINT-0 as an L684 one-liner.

---

## 2. Production seating chain (causal, file:line)

```text
LAYOUT (rustkit-layout/src/lib.rs ~L4495–4590)
  line_height  = style.line_height.to_px(font_size)     // flat 1.2 today
                 [ENGINE.patch → to_px_with_normal / resolve_line_height]
  metrics      = measure_text_advanced(...)             // CTFont ascent/descent on macOS
  content_h    = metrics.ascent + metrics.descent
  half_leading = max(0, (line_height - content_h) / 2)
  y_cmd        = content_y + half_leading               // top of "content + half-leading"
  DisplayCommand::Text { y: y_cmd, ascent: Some(metrics.ascent), advances, ... }

PAINT (rustkit-renderer/src/lib.rs draw_text_with_metrics ~L4409–4451)
  baseline     = y_cmd + layout_ascent
  for each char:
    entry      = GlyphCache::get_or_rasterize(...)
    glyph_y    = baseline + entry.offset[1]             // offset[1] = -bearing_y

RASTER (rustkit-text/src/macos.rs rasterize_char ~L350–480)
  CTFontDrawGlyphs into gray bitmap
  bearing_y    = bounds.origin.y + bounds.size.height   // ink top vs baseline
  (NOT font ascent; NOT fs*1.2)

GLYPH CACHE (rustkit-renderer/src/glyph.rs ~L268–281)
  offset = [bearing_x, -bearing_y]
  // ADVANCE CONTRACT: baseline-relative; no third TextShaper (was 2–3px wrong)
```

### What metrics model changes

| Quantity | flat-1.2 master | metrics ENGINE.patch | Effect on paint |
|----------|-----------------|----------------------|-----------------|
| `line_height` for normal | `fs * 1.2` (often fractional) | `round(asc)+round(desc)+gap` (often integer) | half_leading changes |
| Box heights / section Y | drifts vs Chrome | closer (dh→0 night-16) | content_y cascade moves |
| Glyph bitmaps | identical if font/size same | **should be identical** | isolate seating vs raster |
| `ascent` on command | CTFont (unchanged by patch intent) | same source | baseline = y_cmd + ascent |

Night-16: **geometry improves, pixels worsen** → first probe must attribute score delta to **seating float shifts** (half_leading / baseline / content_y) vs **bitmap/AA path** (same pixels in atlas).

---

## 3. Ranked hypotheses (probe order)

| Rank | Hypothesis | Why plausible | Falsify if |
|------|------------|---------------|------------|
| **H1** | Half-leading / y_cmd fractional shift under metrics moves every baseline by a sub-pixel that Core Text AA hates vs Chrome | line_height is the only intentional metrics delta; half_leading is linear in it | A/B glyph_y deltas ≈0 yet score still +5pp |
| **H2** | layout `metrics.ascent` (font ascent) ≠ ink `bearing_y` coupling changes when half-leading redistributes | two different metric sources in the chain | seating logs show consistent top-of-ink vs Chrome layout-rects for sample runs |
| **H3** | Grayscale R8 atlas + linear filter vs Chrome ClearType/LCD — score sensitivity rises when boxes align (diff becomes pure AA) | renderer format is R8Unorm; Chrome is LCD | bitmaps identical, seating matches Chrome, score still red |
| **H4** | `GlyphKey.font_size = (fs*10) as u32` quantization | secondary | sizes are already tenths-stable |
| **H5** | `estimate_glyph_size` fs×1.2 | residual §5 | production path never calls it for body text — **already falsified as primary** |

**Do not thrash H3 first** (gamma/subpixel epic). Run H1/H2 seating probe in one night.

---

## 4. Implement contract (Atlas)

### 4.1 PAINT-0 = probe PR (or probe commit), not a land rewrite

Ship instrumentation + fixture + A/B table. Land rewrite only if P0d/P0e greenlights a **named** one-line seating fix with campaign receipts.

### 4.2 Probe steps

| Step | Action | Pass criteria |
|------|--------|---------------|
| **P0a** | Instrument (debug / feature-flag / one-off binary): for 12px + 14px system-ui on a 3-line fixture log `line_height`, `half_leading`, `content_y`, `y_cmd`, `layout_ascent`, sample char `bearing_y` ('x','H','g'), `baseline`, `glyph_y` | Numbers printable; same binary can flip flat vs metrics via env or dual build |
| **P0b** | Fixture: ≥80 lines dense body text, **no forms**, no buttons (isolate from DIG-buttons) | under `parity-tests/repro/` or probe/ |
| **P0c** | A/B flat-1.2 vs metrics (ENGINE.patch seat): (1) atlas bitmap hash for first 50 codepoints (should match); (2) mean |Δglyph_y| and |Δhalf_leading|; (3) fixture KF or css-selectors score | Attribute: seating-only / raster-diff / mixed |
| **P0d** | If seating-only: try **integer snap** of `y_cmd` or `baseline` (document which) under metrics seat only; re-measure css-selectors + gallery | recovers ≥ half of +5.11pp on css-selectors **and** gallery stays ≤7.0 dual-path class → greenlight PAINT-1 |
| **P0e** | If still diffuse with seating matched | **STOP** — one-pager; escalate to AA/gamma epic (new unit). **HOLD model land.** No constant thrash |

### 4.3 File:line inventory (probe / optional land)

| Site | Role | PAINT-0 action |
|------|------|----------------|
| `rustkit-layout/src/lib.rs` ~L4515–4535 | half_leading + y_cmd | **Primary instrument**; optional snap land target |
| same ~L4585–4589 | `ascent: Some(metrics.ascent)` | Log; do not invent second ascent |
| `rustkit-renderer/.../lib.rs` ~L4433–4451 | baseline + glyph_y | **Primary instrument** |
| `rustkit-renderer/src/glyph.rs` ~L268–281 | offset = −bearing_y | Confirm ADVANCE CONTRACT intact |
| `rustkit-text/src/macos.rs` ~L350–480 | CTFont raster + bearing_y | Log bearing; **no cell-h rewrite first** |
| `rustkit-text/src/macos.rs` L683–684 `estimate_glyph_size` | placeholder only | **Out of PAINT-0 land path**; optional later cleanup |
| ENGINE.patch `normal_line_height` / `to_px_with_normal` | metrics model | **HOLD land** until PAINT-0 companion or Pete park |
| form *1.2 / DIG-buttons UA | other digs | **Do not fold** |

### 4.4 Land gates (PAINT-1 + model, only after P0d)

| Gate | Bar |
|------|-----|
| Campaign | **≥24/26** @ t15 |
| css-selectors | **≤15** preferred ≤ master ~10 band or clear improve vs metrics-only 15.14 |
| image-gallery | dual-path ~6.8 PASS t10 preserved (needs #53 on base) |
| Holdout | 6/6 |
| Units | seating / snap tests drive engine — not hand-waved |
| CI | **no KF ceiling lowers** |

### 4.5 DO-NOT

- Start with rewriting `estimate_glyph_size` / L684  
- Model-only merge  
- Fold DIG-buttons-stack or form *1.2 into paint PR  
- Gamma/ClearType rewrite without P0c attribution  
- Raise thresholds to hide 15.14  
- Claim atomic closed because gallery PASSes under dual patch  
- Windows port of paint before macOS path named  

---

## 5. Expected score impact

| Surface | Expectation after probe-only |
|---------|------------------------------|
| Campaign | Unchanged (instrument only) |
| After successful P0d snap + model | css-selectors under t15; gallery dual-path class held → first real path to 25/26 **maybe** |
| DIG-buttons-stack alone | layout honesty; **not** a substitute for this residual |

---

## 6. Outside-eye checklist (Prometheus when PR opens)

- [ ] PR body cites night-16 A/B (gallery 6.80 / css-selectors 15.14)  
- [ ] Explicitly does **not** treat L684 as primary without new evidence  
- [ ] P0a–c logs or tables present (half_leading, glyph_y, atlas hash)  
- [ ] If land included: which snap (y_cmd vs baseline) + campaign before/after  
- [ ] Metrics land only with paint companion; no KF games  
- [ ] DIG-buttons not smuggled as paint fix  
- [ ] Base includes #53 (or notes dual-path still needs it for gallery)  
- [ ] Athena port note only after macOS paint path lands  

---

## 7. Priority vs other lanes

| Lane | vs PAINT-0 |
|------|------------|
| Merge #53 | Still first for gallery dual-path honesty |
| **PAINT-0** | Highest **HiWave board** residual for metrics land |
| DIG-buttons-stack | Parallel layout dig — separate PR |
| Website Tank W1+W2 | Highest **product** gravity — other repo |
| Tank C3a sticky | Highest **estimator** honesty — other repo |
| WPT W0a | Free anytime; do not steal paint-probe night |

---

## 8. Summary for digests / exchange

> **2026-07-16 PAINT-0 pin:** Residual §5 smoking gun `macos.rs:684 estimate_glyph_size` is **placeholder-only** (missing-glyph path). Production macOS glyphs use CTFont ink bounds + baseline-relative cache. Metrics model changes `line_height` → `half_leading` → `y_cmd` → baseline → `glyph_y` while bitmaps stay put — that is the first-order paint coupling. Atlas: instrument seating chain (P0a–c), A/B flat vs metrics with atlas hash, optional integer snap (P0d); HOLD model land and do not thrash L684. Parallel: DIG-buttons-stack, website Tank, C3a.

— Prometheus (design seat), 2026-07-16 grind tick
