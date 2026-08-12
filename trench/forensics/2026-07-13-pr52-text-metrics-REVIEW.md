# Outside-eye: hiwave-macos #52 + text-metrics atomic epic pin

**Author:** Prometheus · **Date:** 2026-07-13 (grind tick)  
**PR:** [hiwavebrowser/hiwave-macos#52](https://github.com/hiwavebrowser/hiwave-macos/pull/52) — `atlas/text-metrics-instrument` @ `09d3ab2`  
**Tree pin:** master @ `8d7264d` (PR #51 tip); local hub dirty on parity diffs only — no checkout  
**Companion:** `trench/forensics/2026-07-13-normal-lineheight-WALL.md` + `…-ENGINE.patch`  
**Board (Atlas noon):** 24/26 @ t15, avg 7.1, holdout 6/6 — engine NOT on master

---

## 0. Verdict

| Item | Verdict |
|---|---|
| **PR #52 merge** | **APPROVE** — instruments only; CI green; cannot red-lock board |
| **Chrome-without-Chrome claim** | **TRUE** — `baselines/chrome-148/*/*/layout-rects.json` + `computed-styles.json` already cover all 32 cases |
| **Target model** | **`round(ascent) + round(descent) + leading`** — sound; matches wall + ENGINE.patch body |
| **Do not land ENGINE.patch alone** | **HOLD** — measured 24/26 → 23/26; form coupling proven; ≥1 other coupling unnamed |
| **object-fit as parity dig** | **FALSIFIED** (Atlas correct) — ledger as **spec debt**, not dig |

---

## 1. PR #52 review (files only)

### Diff
- `scripts/probe_normal_lineheight.py` (+114) — derives Chrome resolved `normal` from committed rects
- `crates/rustkit-layout/tests/normal_line_height_probe.rs` (+92) — shaper A/B vs pinned Chrome table

### CI (rollup)
- pr-swarm 0–3 **SUCCESS**, audit **SUCCESS**, Parity Metrics collect **SUCCESS**, commit-gate **SKIPPED** (expected for this path)
- **0 reviews** at time of this eye — first outside-eye

### Method (sound)
1. **Leaf-block geometry filter** is the right observable: `getComputedStyle` reports `normal` literally, so border-box height of a single-line leaf block with no vertical pad/border ≈ line box. Ratio band `1.0–1.45` is a reasonable multi-line reject.
2. **Characterization-only test** asserts Chrome's model vs flat 1.2 on the shaper; never asserts engine `LineHeight::to_px`. Safe under green CI.
3. **Contract asserts** `exact ≥ 18/20` + rounded beats flat — leave as soft floor; do not harden to 20/20 while Arial 13.33 carries `(SPREAD)`.

### Live code cross-check (master @ 8d7264d)
Confirmed wall claim in `rustkit-css`:

```text
/// Normal line height (use font metrics, typically ~1.2).   // still lies
LineHeight::Normal => font_size * 1.2,                     // still ships
```

`TextMetrics::{ascent,descent,leading,height}` exist; probe uses rounded ascent/descent + leading — same formula as ENGINE.patch `normal_line_height`.

### Non-blocking nits (do not block merge)
1. **Arial 13.33 `(SPREAD)`** — wall already flags form-control pollution. Before treating 1/20 as a real model miss, re-sample non-control Arial leaves only (or drop the pair from the strict count).
2. **Chrome table is frozen in the Rust test** — after any baseline re-capture, re-run the Python probe and refresh `CHROME` constants. One-line comment in the test pointing at that refresh step would help Athena/Windows ports.
3. **`leaf_selectors` uses ` > `-prefix strings** — fine for this suite's selector vocabulary; not a general DOM leaf. Document that it is baseline-selector topology, not tree walking.
4. **Hand-formatted rust** — fine; optional `cargo fmt` when allowlist permits.

### Athena / Windows note
When Windows has the same chrome-148 rects from page-mirror, both instruments port as pure tools. No engine port this PR.

---

## 2. ENGINE.patch outside-eye (for the *next* atomic PR — not this one)

### What it does well
- Introduces `normal_line_height` + `resolve_line_height` with thread-local cache (right cost model: shape once per font key per pass).
- Formula matches the instrumented target model (Blink independent round of ascent/descent).
- Rewires the **14** live `style.line_height.to_px(...)` sites in layout/flex/grid/paint baseline paths.
- Honest fallback to `NORMAL_LINE_HEIGHT_FALLBACK_RATIO` when ascent ≤ 0.
- Doc on why raw floats lose the pixel meter (sub-pixel baseline → AA divergence) is load-bearing — keep it in the merge commit body.

### Doc drift (fix before land)
`LineHeight::to_px_with_normal` comment says `normal_px` is `TextMetrics::height` (unrounded). Callers via `resolve_line_height` pass **rounded** metrics. Align the rustdoc to "already-resolved normal px (prefer Blink-rounded)" so the next editor does not "simplify" back to raw height.

### Residual hard-coded `font_size * 1.2` (not rewritten by the patch)

These are **orthogonal twins** of the wrong constant. Leaving them after `resolve_line_height` lands keeps two parallel truths.

| Site | Role | Atomic-epic action |
|---|---|---|
| `lib.rs` FormControlType::TextArea height | `fs*1.2*rows+8` | Re-validate vs Chrome rects under corrected normal; may stay as UA blob if Chrome UA matches coincidence |
| `lib.rs` Checkbox/Radio | `fs*1.2` square | Likely independent of line-height; probe before rewrite |
| `flex.rs` twin FormControl arms (× several) | same as lib | Keep dual-loop mirror — rewrite both or neither |
| `forms.rs` caret/selection height | paint chrome | Low board impact; still twin constant |
| `rustkit-text/.../macos.rs` glyph atlas height | raster bound | Do **not** silently change without glyph tests — separate PR if needed |
| `LineHeight::as_number` → `Some(1.2)` for Normal | inheritance/serialization path | Confirm callers; may need "unresolved" semantics |

### DIG-1/DIG-2 coupling nuance
`single_line_box` for TextInput/Button/Select with author padding uses **`(font_size + 1.0) + author_pb`**, not `line_height.to_px`. So css-selectors regression under corrected normal is **not only** "control content = 16px from 1.2". Proven measurements still stand (css-selectors 10.03→15.14); mechanism may be mixed:

- surrounding label / section text line boxes shifting Y
- any path still reading `to_px(Normal)` for form-adjacent layout
- Arial UA control font interacting with inherited `normal` on non-control leaves

**Next session must not "fix button height only".** Use per-element |Δy| rank under both models (wall §4 step 1).

---

## 3. Atomic epic order (design pin for Atlas)

Land as **one multi-night PR** (or tightly stacked PR with single merge gate). Incremental model-only is measured-negative.

1. **Merge #52 first** (this PR) — instruments on master unlock offline A/B for everyone.
2. **Coupling hunt (image-gallery first):** run rects diff under flat vs rounded model; rank elements by |Δy|. Gallery has **0 `<img>`** in websuite case — caption/text stack only. Name the non-form dependent(s) before editing forms.
3. **Control re-composition:** re-measure TextInput/Button/Select/TextArea against chrome-148 under **target** normal; update `single_line_box` / blobs only if geometry requires it. Dual-update flex.rs twins.
4. **Apply ENGINE.patch** (or re-apply if master moved) + residual `*1.2` audit decisions from table above.
5. **Doc comment honesty** in rustkit-css even if any path still falls back to 1.2.
6. **Gate:** full campaign **≥24/26** and no new holdout red; css-selectors must not re-fail t15; about/image-gallery expected movers (wall: last mile is this bug).
7. **Port note:** shared `rustkit-css` + layout resolve — when macOS lands, Windows/Linux get the API; Athena ports `resolve_line_height` call sites, not a second model.

### Explicit anti-patterns
- Do not lower KF / thresholds to absorb the 23/26 regression.
- Do not land model without image-gallery coupling named.
- Do not treat object-fit cascade as the gallery dig (falsified).
- Do not rewrite `rustkit-text` atlas height in the same PR without glyph evidence.

---

## 4. object-fit ledger (accept Atlas falsification)

Prometheus dead-property sweep Class B pinned object-fit as top dig leverage. Atlas applied the probe-before-patch rule:

- `image-gallery` case: **zero `<img>`** (pseudo placeholders)
- `images-intrinsic` passes campaign threshold; residual is text_metrics-dominated labels

**Ledger:** cascade still wrong (`ComputedStyle` default `"contain"` vs spec initial `fill`; zero engine arms) → **spec-correctness debt**, not campaign dig. Reopen only when a real-`<img>` fixture fails on fit/position.

---

## 5. Pete decisions (from Atlas noon — Prometheus lean)

| # | Question | Lean |
|---|---|---|
| 1 | CfT-148 on seat for grinding existing board? | **Optional.** Committed rects suffice for current 32. Keep for *new* fixtures only. |
| 2 | Greenlight text-metrics epic as one atomic multi-night unit? | **Yes.** Instruments (#52) merge now; model+dependents as one gated unit after coupling hunt. |
| 3 | (implied) Park emoji-color-glyphs | **Stay parked** (prior measured net-negative). |

---

## 6. Next owners

| Seat | Action |
|---|---|
| **Atlas** | Merge #52; open atomic epic after coupling hunt (gallery |Δy| first); leave tank C3a on parallel private track |
| **Athena** | No action on #52; when atomic lands, port resolve path not re-derive model; Windows can run Python probe on mirrored baselines now |
| **Prometheus** | Outside-eye on atomic epic PR; standby for coupling-hunt Qs |

---

*Design/outside-eye only. No merge, no force-push, no engine land from this seat.*
