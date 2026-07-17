# PAINT-0 executed: seating exonerated — the metrics residual is integer layout drift with three named terms

> **Status:** Probe RESULT, 2026-07-17 night block 17 (Atlas).
> **Consumes:** `2026-07-16-paint0-glyph-seat-IMPLEMENT.md` (probe contract §4.2), `2026-07-16-lineheight-metrics-ENGINE.patch`.
> **Supersedes (residual framing):** FIDELITY-RESIDUAL §5 / PAINT-0 pin §3 H1–H3 — the "glyph bitmaps seat a fraction off on every line" hypothesis is **FALSIFIED**. No AA/gamma epic is needed.
> **Does not supersede:** model correctness (19/20 probe), DO-NOT model-only land, #53 gallery dual-path receipt.

## 0. One-liner

P0a–P0d ran to completion on `master@5161571` (#53 merged): glyph bitmaps are **byte-identical** between flat-1.2 and metrics-normal (80/80 FNV hashes), and forcing **every baseline integral** (240/240 runs) moves css-selectors by **+0.02pp (15.14 → 15.16)** — sub-pixel seating explains **none** of the +5.11pp metrics regression. The regression is **cumulative integer-pixel layout drift** vs Chrome, fully attributed per section: **S6 +86px (block-stacked buttons, both builds — DIG-buttons-stack), S4 +5.33 (forms — the model's one known miss: 13.333px), S1 +4.00, S3 −4.00.** Metrics-normal is **EXACT vs Chrome on sections 2/5/7/8** (flat is wrong on all four).

## 1. Probe receipts (all on master+probe base, this night)

| Step | Result |
|------|--------|
| P0a instrument | `RUSTKIT_PAINT_PROBE=1` logs layout (`lh/half/y_cmd`), paint (`baseline/glyph_y/bearing_y` for x/H/g), atlas (per-glyph FNV-1a bitmap hash). Branch `atlas/paint0-seat-probe`. |
| P0b fixture | `parity-tests/probe/dense-text.html` — 80 wrapped lines, 14px+12px system-ui, no forms/buttons |
| P0c atlas A/B | **80/80 common glyphs, 0 hash mismatches** → bitmaps identical, all delta is placement |
| P0c seating A/B | mean Δhalf_leading +0.145; mean Δy_cmd **+11.0** (accumulating, max +23.1); integral y_cmd **0/80 in BOTH builds**; baseline mean frac: flat 0.506, metrics **0.621 (worse)** |
| Score repro | css-selectors 10.03→15.14, image-gallery 13.60→**6.80 PASS** — night-16 A/B reproduces exactly on merged-#53 master |
| P0d snap | Baseline `.round()` in `draw_text_with_metrics` (Chrome/Skia-style integral-Y seat), verified 240/240 integral, frac 0.0000 → css-selectors **15.16** (Δ +0.02 = noise). **Gate failed; snap trial reverted.** |

## 2. The real mechanism (per-section y/h table, `paint0_sections.py`)

| § | flat h−Chrome | metrics h−Chrome | read |
|---|--------------:|-----------------:|------|
| 1 | +2.80 | **+4.00** | residual overshoot (small) |
| 2 | −1.40 | **0.00** | model EXACT |
| 3 | −5.40 | **−4.00** | residual undershoot |
| 4 | +3.73 | **+5.33** | forms — the 13.333px model miss |
| 5 | −1.60 | **0.00** | model EXACT |
| 6 | **+85.0** | **+86.0** | block-stacked buttons — DIG-buttons-stack, both builds |
| 7 | −1.20 | **0.00** | model EXACT |
| 8 | −1.20 | **0.00** | model EXACT |

Cumulative y error at §7: flat +83.1, metrics +91.3. Sections 7–8 are ~90px below Chrome in both builds; the +5pp "diffuse dense small-text" attribution was those misaligned text rows counted pixel-by-pixel, plus the +8px flat→metrics delta from S1/S4. **Under flat the small per-section errors partially cancel S6; under metrics the exact sections stop cancelling** — correctness exposes the one big bug instead of hiding it.

## 3. What this rewrites

| Claim | Now |
|-------|-----|
| Residual = text-paint / glyph-atlas sub-pixel fidelity | **FALSIFIED** (H1 dead by direct experiment; H2/H3 moot — no flat-vs-metrics AA delta exists) |
| AA/gamma epic needed before model land | **NO** — nothing paint-side blocks the model |
| DIG-buttons-stack = "parallel layout honesty, not a gate" | **INVERTED** — S6 is the dominant css-selectors term in BOTH builds and the first land in the metrics epic's honest order |
| Model land order | 1) DIG-buttons-stack → re-measure; 2) chase S4 (+5.33, the 13.333px miss) and S1/S3 (±4) under metrics; 3) land model when css-selectors ≤ flat band. Gallery 6.80 preserved throughout (needs nothing new — #53 is merged). |

## 4. Discipline notes

- Snap trial reverted same-night (failed its own gate); probe branch carries instrumentation only, env-gated, zero cost off.
- ENGINE.patch applied only in the working tree for the A/B, never committed; still banked in forensics.
- `estimate_glyph_size`/L684 untouched, per pin §4.5.

— Atlas (macOS seat), night 17
