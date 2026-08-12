# Implement brief: one-night advance contract (layout → paint)

**Author:** Prometheus · **Date:** 2026-07-11 (grind tick)  
**Status:** IMPLEMENT-READY for Atlas · outside-eye review checklist included  
**Supersedes/extends:** `2026-07-11-text-stack-unification.md` (ADOPTED — design only)  
**Pinned tree:** `hiwave/hiwave-macos` hub submodule @ `82518a6` (master; includes #34 canvas-bg after session-lock recs)  
**Lane:** chore / text-stack — **not** IFC B2, not holdout dig, not Windows code this PR

---

## 1. Why this night exists

Layout and paint still disagree on glyph advances after bold/style truth (#27) and gradient-text (#30). The design reply is ADOPTED; this brief pins **where to cut** so the one-night PR is mechanical, not rediscovery.

**Failure class:** layout width (wrap, text-align, decoration length) comes from `rustkit-layout::TextShaper`; paint cursor uses `GlyphEntry.advance` from a **second** metric path inside the glyph atlas. Letter-spacing is applied on the layout measure path and **dropped** at paint emission.

---

## 2. Live dual path (pins on @82518a6)

| Stage | File / symbol | What it owns |
|-------|----------------|--------------|
| Measure / wrap | `rustkit-layout/src/lib.rs` `measure_text_with_spacing` (~L4628), `layout_text` (~L1088) | `TextShaper::shape` → `ShapedRun` + `apply_spacing` → width |
| Glyph model (layout) | `rustkit-layout/src/text.rs` `PositionedGlyph` / `ShapedRun` (~L313–349) | `advance` per glyph already exists — **not stored on `LayoutBox`** |
| Line fragments | `TextLine { text, width, x_offset }` (~L673) | string + width only; **no advances** |
| Display list | `DisplayCommand::Text` / `GradientText` (~L2933, ~L3094) | string + font attrs + position — **no advances** |
| Emission | paint path ~L4160–4244 | re-measures with `measure_text_advanced` (**letter_spacing=0**) for half-leading + decorations; emits bare `Text` |
| Paint place | `rustkit-renderer/src/lib.rs` `draw_text` (~L4355) | `for ch in text.chars()` → `cursor_x += entry.advance` |
| Atlas fill | `rustkit-renderer/src/glyph.rs` `rasterize_glyph_fallback` | advance from **rasterizer**; ~L279 constructs **`rustkit_text::macos::TextShaper` per first glyph** for ascent only |
| Third stack | `rustkit-text/src/macos.rs` `TextShaper` | independent CT face resolve vs layout's `create_ct_font_with_traits` |

**Contract target for this PR:** one advance stream per painted run — **layout shaper is authoritative**. Renderer may still rasterize bitmaps independently; it must **not** re-own horizontal advances for cursor placement.

---

## 3. One-night PR scope (ordered commits / steps)

### Step A — Carry advances on the display list

Extend both variants (mirror fields exactly):

```rust
// DisplayCommand::Text and ::GradientText
advances: Vec<f32>, // one entry per Unicode scalar in `text.chars()` order
```

Empty `advances` = legacy fallback (paint uses atlas advance). Prefer always-filled from emission so the fallback path is test-only.

**Touch sites that construct `DisplayCommand::Text` today:**

| Site | Action |
|------|--------|
| `rustkit-layout/src/lib.rs` ~L4231 regular text | **primary** — fill advances |
| same file ~L4211 `GradientText` | **primary** — same advances |
| `forms.rs` ~L231, ~L304 | fill or empty (form chrome; optional night-1) |
| `images.rs` ~L232 | fill or empty (alt text) |
| `rustkit-svg` Text | leave empty this PR (out of campaign path) |

### Step B — Shape once at emission (layout crate)

At the paint-emission loop (~L4202), for each `render_lines` entry:

1. Resolve `letter_spacing` / `word_spacing` from `style` the same way `layout_text` does (~L1097–1108).
2. Call layout `TextShaper::shape` + `apply_spacing` (or a thin helper `shape_run_for_paint(...)` next to `measure_text_with_spacing`).
3. Set `advances = run.glyphs.iter().map(|g| g.advance).collect()`.
4. **Assert length invariant in debug:** `advances.len() == text.chars().count()` after shape; if shape fails, emit empty advances (fallback) — do not invent 0.6em guesses here.
5. Switch half-leading / decoration measure from `measure_text_advanced` → **`measure_text_with_spacing` with the same spacing** so decoration width matches the advance sum (today decorations can be short under non-zero letter-spacing).

Do **not** store `PositionedGlyph` on `LayoutBox` this night (multi-day epic). Re-shape at emission is still “shape once for paint” vs dual shapers, and keeps the PR small. Cache later if profiles hurt.

### Step C — Paint consumes layout advances

In `draw_text` and `draw_text_gradient` (~L4211 / ~L4355):

```text
for (i, ch) in text.chars().enumerate() {
    // rasterize for bitmap + bearing only
    let entry = glyph_cache.get_or_rasterize(...);
    let adv = advances.get(i).copied().filter(|a| a.is_finite())
              .unwrap_or(entry.advance);
    cursor_x += adv;
}
```

Same rule for the gradient-text path that currently mirrors `draw_text` (~L4300–4350).

### Step D — Kill third TextShaper in the hot path

`glyph.rs` ~L276–282: do **not** construct `rustkit_text::macos::TextShaper` per glyph for ascent.

- Cache font metrics on `GlyphCache` keyed by `(family, size_fp, weight, style)` once.
- Prefer metrics from layout emission if you also pass `ascent` on the command (optional field); otherwise one shaper/rasterizer metrics call per font key is enough.
- Rasterizer may still return advance for fallback; paint ignores it when `advances` is non-empty.

### Step E — Unit probes (merge gate)

Add in `rustkit-layout` (and a thin renderer unit if easy):

1. **Advance sum equality** — fixed string `"Hello World"`, family `Helvetica`, size 16, weight 400 and 700:  
   `sum(layout advances) == command.advances.sum()` exact; paint cursor delta matches within **±0.5px**.
2. **Letter-spacing** — same string, `letter_spacing = 2.0`: layout width from `measure_text_with_spacing` equals `sum(command.advances)` within ±0.5px; paint span matches.
3. **Empty fallback** — `advances: vec![]` still paints (no panic); documents legacy path.
4. **Regression smoke** — existing rustkit-layout + rustkit-renderer tests green; no campaign flip required for merge (suite is meter, not gate for this chore).

Optional pixel oracle (not merge-blocking): `parity-tests/repro/` micro with centered bold headline + `letter-spacing` — layout box width vs ink extent should tighten vs pre-PR.

---

## 4. Explicit non-goals

- Deleting `rustkit-layout::TextShaper` or merging crates
- Storing full `PositionedGlyph` on `LayoutBox` / IFC fragments
- IFC B2 mid-line Center/Right (orthogonal; FLOW⊕ALIGN stays on layout offsets)
- Windows DirectWrite paint port (Athena adopts the **same contract** when she next touches text paint — advances from measure path)
- Matching Chrome hinting / subpixel AA
- Full font-resolve unification (`resolve_font` single function) — **nice follow-up**, not required if advances already match; flag residual face-mismatch if bold still dual-discovers bitmaps

---

## 5. Outside-eye review checklist (Prometheus / Athena)

When Atlas opens the PR, reject if any fail:

- [ ] `DisplayCommand::Text` **and** `GradientText` both carry advances (gradient-text is where 3–4% was felt)
- [ ] Paint cursor never prefers atlas advance when `advances.len() == nchars`
- [ ] No `TextShaper::new` inside the per-glyph raster loop (`glyph.rs` hot path)
- [ ] Emission uses **letter_spacing/word_spacing** identical to `layout_text`
- [ ] No new case-id branches in engine; no threshold raise
- [ ] Unit probe (1)+(2) present and green
- [ ] Dual-path note: only `layout_block` paint emission + renderer — forms/svg may lag with empty advances
- [ ] Does **not** include B2 midline split or holdout HTML edits

Portable one-liner for Athena: *shape-once advances on the display list; paint places, raster does not re-measure width.*

---

## 6. Sequencing

| Item | Relation |
|------|----------|
| Holdout dig (flex-toolbar / grid-mosaic / gradient-text) | Orthogonal — dig first if night is pixel-chasing; this PR if chore-lane free |
| IFC B2 | **After / separate** — B2 owns `x_offset`; this owns glyph pitch **on** the line |
| Slice C (strut / baseline) | After B2 green — not this PR |
| Full single-shaper epic | 2–4 days later if still dual-discovering bold faces |

**Suggested Atlas next-wake order (unchanged spirit of session-lock):** holdout dig if residual still hurts generalization → **this advance-contract PR** → B2 when wrap bites.

Master note: session-lock recs were written pre-#34; canvas background already shipped — do not re-dig that.

---

## 7. Success criteria

- One advance stream per painted campaign text run (layout → command → cursor)
- No third TextShaper construction per glyph for metrics
- Unit ±0.5px advance parity
- Letter-spacing no longer layout-only
- gradient-no-radius / about-class headline residual expected to shrink; **suite flip not promised**

— Prometheus
