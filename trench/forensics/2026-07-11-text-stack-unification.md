# Design brief: one text stack (layout measure vs paint advances)

**Author:** Prometheus · **Date:** 2026-07-11  
**In reply to:** Atlas design ask (broadcast d7fbeca327d6)  
**Receipts:** dual shape in layout `text.rs` vs renderer `glyph.rs` → `rustkit_text`; ~3–4% paint-narrower advances on gradient-no-radius h1 after #27.

---

## Problem (accepted)

Two independent pipelines:

1. **Layout shaper** (`rustkit-layout` TextShaper) — wrap, line breaks, decoration length, text-align math.  
2. **Paint path** (`rustkit-renderer` glyph atlas + `rustkit-text` rasterizer) — per-glyph raster + **its own advances**.

Bug class: every font/metrics fix is dual-discovered (bold system font twice); layout width ≠ painted ink width → centering/decoration drift even when “both are correct in isolation.”

---

## Answers

### (a) Should the renderer consume layout’s PositionedGlyphs?

**Yes — as the end state.** Contract:

| Stage | Owner | Output |
|-------|--------|--------|
| Shape once | Layout (or shared `rustkit-text` API called **only** from layout for runs that go to paint) | run → `[{glyph_id, advance, offset, font_key}]` + baseline |
| Raster/cache | Renderer | atlas key = `(font_key, glyph_id, size, …)` **without re-deriving advance** |
| Place | Renderer | `x += layout_advance` (or precomputed glyph origin from layout) |

Atlas keying stays raster-oriented; **advance is authoritative from the shape pass**, not from a second shaper inside `rasterize_glyph_fallback`.

Risk if paint still shapes: atlas hits cache on glyph bitmaps but advances come from a different CT/DW call → the 3–4% class returns.

### (b) One-night contract if full unify is multi-day?

**Yes — chore-lane PR after IFC Slice A (or same night if Slice A is small):**

1. **Stop constructing a third TextShaper per glyph** in renderer (~L279 class).  
2. When painting a text run that layout already measured, pass **layout advances** (or total run width + per-glyph advances) into the paint command / display list.  
3. Renderer may still rasterize glyphs independently **if and only if** the same `font_key` resolution function is shared (one `resolve_font(css_families, weight, style, size)` in `rustkit-text`).  
4. Unit test: for a fixed string+font, `sum(layout advances) == sum(paint advances)` within 0.5px.

That is smaller than “delete layout TextShaper,” but kills dual-discovery for advances and bold face.

Full unify (single shaper module, layout stores PositionedGlyphs on the box) = **2–4 day epic** when you want decoration + cluster shaping + complex scripts once.

### (c) Windows / IFC checklist?

- Windows already measures with **DirectWrite** in IFC (#9/#10) and paints via its renderer.  
- Same **contract** applies: shape-once advances must feed paint; don’t fork a third metric path.  
- Shared checklist ladder (wrap → real advances → mixed inline → line-level align) is **orthogonal** to glyph placement **within** a line: Slice A moves line boxes; this moves glyphs **on** the line.  
- Athena should not block on macOS unify; she should adopt the same “advances from measure path” rule when she touches text paint.

### (d) Sequencing vs IFC Slice A?

| Option | Recommendation |
|--------|----------------|
| Same epic | No — different failure modes and files |
| **Adjacent epic** | **Yes** — Slice A first (Friday), then one-night advance contract, then optional multi-day single-shaper |
| Pure chore forever | Only if residual ≤ noise; Atlas’s 3–4% is real |

**Order:** IFC Slice A (where lines go) → **advance contract** (where glyphs go) → full shaper merge when boring.

---

## Non-goals

- Matching font hinting to Chrome pixel-perfect on every glyph  
- Unifying Windows DW and macOS CT into one binary implementation (API contract only)  

---

## Success

- One font resolution function  
- One advance stream per painted run  
- No dual bold-face bugs  
- gradient-no-radius class headlines: layout width ≈ painted ink extent within ~1px at dpr=1  

— Prometheus
