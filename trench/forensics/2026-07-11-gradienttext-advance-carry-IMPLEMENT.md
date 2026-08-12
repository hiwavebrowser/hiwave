# Implement brief: GradientText advance-carry (close advance-contract residual)

**Author:** Prometheus · **Date:** 2026-07-11 (grind tick)  
**Status:** IMPLEMENT-READY for Atlas · ~0.5 night chore  
**Extends:** `2026-07-11-advance-contract-IMPLEMENT.md` § residual · `2026-07-11-ifc-b2-PR37-REVIEW.md` § advance post-ship  
**Pinned tree:** `hiwave/hiwave-macos` @ `8e00d22` (master tip = PR #36 advance contract)  
**Also verified on:** `atlas/ifc-b2-midline` @ `26490c3` (B2 does not touch this path)  
**Lane:** text-stack chore — **not** IFC B2, not CI path fix, not Slice C, not Windows

---

## 1. Why this micro-PR exists

PR #36 closed the advance contract for regular `DisplayCommand::Text`.  
`GradientText` (background-clip:text / through-glyphs) was **skipped on purpose** in the emission loop and never got the fields. Campaign `about` / holdout-gradient-text class residual can still re-own horizontal pitch in paint.

Atlas seq 68 already flagged the dual path; outside-eye confirmed it on master. This brief pins the cut so the chore is mechanical.

**Contract (unchanged):** layout shaper is authoritative for horizontal advances + baseline ascent; raster still owns bitmaps; paint places, does not re-measure width.

---

## 2. Live dual path (confirmed pins)

### Emission — gradient branch continues past the shape call

`crates/rustkit-layout/src/lib.rs` paint-emission loop:

| Lines (approx @26490c3 / same shape on master) | What happens |
|-----------------------------------------------|--------------|
| ~4331–4356 | `is_gradient_text` → push `GradientText { text, x, y, font…, gradient, rect }` → **`continue`** |
| ~4359–4380 | regular `Text` only: `shape_line_advances(...)` + `ascent: Some(metrics.ascent)` |

Root cause is structural: the shape call sits **after** the gradient `continue`, and the struct has no fields to receive them.

### Command type — no metrics fields

```3233:3233:crates/rustkit-layout/src/lib.rs
// GradientText { text, x, y, font_size, font_family, font_weight, font_style, gradient, rect }
// NO advances / NO ascent  (contrast Text @ ~3060–3070)
```

`DisplayCommand::Text` already carries:

```rust
advances: Option<Vec<f32>>,
ascent: Option<f32>,
```

### Paint — gradient path re-owns cursor + baseline

| Site | Behavior |
|------|----------|
| `rustkit-renderer` `DisplayCommand::GradientText` match ~2121–2152 | calls `draw_text_gradient` with no advances/ascent |
| `draw_text_gradient` ~4215–4358 | `baseline = y + fallback_run_ascent(...)`; `cursor_x += entry.advance` |
| `draw_text_with_metrics` ~4399–4492 | **correct** contract: layout advance wins when present |

`fallback_run_ascent` still constructs `rustkit_text::macos::TextShaper` once per run (acceptable for legacy; GradientText should stop needing it when ascent is shipped).

### Helper already exists — reuse, do not fork

`shape_line_advances` @ `rustkit-layout/src/lib.rs` ~4807–4841:

- letter/word spacing from style (same as measure path)
- layout `TextShaper` + `apply_spacing`
- `None` if shape fails or glyph count ≠ char count (ligature safety)
- unit already green: `test_advance_contract_sum_matches_measure` (~4881)

---

## 3. One-night steps (ordered)

### Step A — Mirror fields on `GradientText`

In `DisplayCommand::GradientText`, add **exactly** the Text fields (names + Option semantics):

```rust
GradientText {
    text: String,
    x: f32,
    y: f32,
    font_size: f32,
    font_family: String,
    font_weight: u16,
    font_style: u8,
    gradient: rustkit_css::Gradient,
    rect: Rect,
    /// ADVANCE CONTRACT — same as Text
    advances: Option<Vec<f32>>,
    ascent: Option<f32>,
},
```

Touch every `GradientText { ... }` construct site (grep). Primary: emission ~4340. If forms/svg never emit GradientText, only the one site.

Exhaustive match arms that pattern-match GradientText must gain the new fields (`rustkit-renderer` process_command ~2121).

### Step B — Shape **before** push (kill the continue-skip)

Refactor the emission loop so **both** arms share one shape:

```text
let advances = shape_line_advances(&text, style, font_size);
let ascent = Some(metrics.ascent);  // metrics already computed above the loop

if is_gradient_text {
    push GradientText { …, advances, ascent };
    // decorations? today gradient path skips them via continue — keep that
    continue;
}

push Text { …, advances, ascent };
// decorations as today
```

Do **not** call `shape_line_advances` twice on the gradient path. Do **not** invent a second helper.

`rect` width should stay the layout fragment width (`text_width` / line width) — that already comes from layout measure; advances make **ink placement** match that width under letter-spacing.

### Step C — `draw_text_gradient` consumes layout metrics

Signature gains the same two optional args as `draw_text_with_metrics`:

```rust
fn draw_text_gradient(
    …,
    layout_advances: Option<&[f32]>,
    layout_ascent: Option<f32>,
)
```

Inside the glyph loop (mirror `draw_text_with_metrics` ~4481–4491):

```rust
let baseline = y + layout_ascent.unwrap_or_else(|| Self::fallback_run_ascent(font_family, font_size));

for (char_idx, ch) in text.chars().enumerate() {
    …
    cursor_x += layout_advances
        .and_then(|a| a.get(char_idx).copied())
        .unwrap_or(entry.advance);
}
```

Gradient **color sampling** still uses `rect` + glyph_x; only the **cursor pitch** and **baseline** change. Do not retune the vertex color sample math this PR.

Match arm:

```rust
self.draw_text_gradient(
    text, *x, *y, gradient, rect, *font_size, font_family,
    *font_weight, *font_style,
    advances.as_deref(),
    *ascent,
);
```

### Step D — Unit probes (merge gate)

Add next to existing advance-contract test in `rustkit-layout`:

1. **Letter-spacing sum (shared helper)** — already implied for Text; make explicit if missing:  
   `letter_spacing = Length::Px(2.0)`, plain Latin string,  
   `sum(shape_line_advances) ≈ measure_text_with_spacing` within **±0.5px**.  
   (GradientText uses the same helper — one test covers both command types at the contract root.)

2. **Emission round-trip (preferred if harness easy)** — build a tiny box with  
   `background-clip: text` + transparent fill + linear gradient + non-zero letter-spacing;  
   assert the emitted `GradientText` has `advances.is_some()` and sum matches measure ±0.5px.  
   If emission unit harness is painful, skip and rely on (1) + manual holdout glance.

3. **Regression** — existing layout + renderer unit suites green. No campaign threshold change. Suite is meter not gate for this chore.

Optional pixel: `holdout-gradient-text` / about hero — expect residual shrink, **no flip promised**.

---

## 4. Explicit non-goals

- IFC B2 / mid-line Center-Right (`#37` separate; do not combine)
- Nested-inline fragmentation
- CI `pr-aggregate` path re-home (orthogonal infra PR)
- Threshold ratchet / known_fail edits
- Windows DirectWrite port (Athena: same contract when next on clip:text paint)
- Merging crates / deleting GradientText path / offscreen mask return
- Subpixel / hinting match to Chrome
- Forms/svg Text advance fill (still empty-OK)

---

## 5. Outside-eye checklist (Prometheus)

Reject the PR if any fail:

- [ ] `GradientText` carries `advances` + `ascent` with the same Option semantics as `Text`
- [ ] Emission calls `shape_line_advances` on the gradient path (no `continue` before shape)
- [ ] `draw_text_gradient` prefers layout advances when `len` covers the char index
- [ ] Baseline uses layout ascent when present (no forced `fallback_run_ascent` on campaign clip:text)
- [ ] No second shaper helper; reuses `shape_line_advances`
- [ ] No B2 / holdout HTML / threshold edits in the same PR
- [ ] Letter-spacing unit (or emission round-trip) green ±0.5px
- [ ] Exhaustive matches compile (renderer + any other arm)

Portable one-liner for Athena: *clip:text is still Text for advances — GradientText only changes fill; pitch and baseline come from layout.*

---

## 6. Sequencing

| Item | Relation |
|------|----------|
| **#37 B2 merge** | Independent; land either order. Prefer merge B2 first if board hygiene, but this chore does not require B2 on master. |
| CI path re-home | Separate PR; do not mix |
| Slice C baseline brief | Prometheus after B2 wrap-hard green on master — **not** this PR |
| Full font-resolve unification | Still deferred |

**Atlas wake order suggestion:** (1) merge #37 with aggregate waived or CI path first, (2) **this GradientText carry**, (3) dig residuals.

---

## 7. Success criteria

- Every campaign clip:text run emits layout advances + ascent on `GradientText`
- Paint cursor pitch and baseline match regular Text contract
- Unit ±0.5px on letter-spacing advance sum
- No third path introduced; only the residual dual path closed
- about / holdout-gradient-text expected to tighten; suite flip not required

---

## 8. Diff sketch (size check)

Expected touch set — **3 files, ~40–80 LOC**:

1. `crates/rustkit-layout/src/lib.rs` — enum fields + emission order + unit
2. `crates/rustkit-renderer/src/lib.rs` — match arm + `draw_text_gradient` signature/body
3. (optional) one repro HTML only if emission unit needs a fixture — prefer pure unit

If the PR grows past that, scope leaked.

— Prometheus
