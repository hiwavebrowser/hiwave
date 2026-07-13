# `line-height: normal` — the text-metrics wall has a name (and a lock)

**Author:** Atlas (macOS seat) · **Date:** 2026-07-13 (night block 14)
**Board:** campaign 24/26 @ t15 avg 7.1 — **unchanged** (engine change measured, then REVERTED)
**Tree:** hiwave-macos `master` @ `8d7264d` (PR #51 tip)
**Status:** root cause NAMED and MODELLED to 0.028px · engine fix BLOCKED on a coupling · instruments SHIPPED

---

## 0. Verdict (one screen)

| Claim | Status |
|---|---|
| "Text-metrics work is flown blind without on-seat Chrome" (last digest) | **FALSE** — Chrome's per-element rects + computed styles are committed for **all 32 cases**. No Chrome install needed. |
| RustKit resolves `line-height: normal` from font metrics | **FALSE** — it hardcodes `font_size * 1.2` (`rustkit-css` `LineHeight::to_px`), while the doc comment claims "use font metrics". |
| Chrome's real model | **`round(ascent) + round(descent) + line_gap`**, rounded INDEPENDENTLY → `normal` is always a whole pixel. Verified exact on **19/20** real font/size pairs. |
| Correcting the model improves the parity board | **NO — it REGRESSES it, 24/26 → 23/26.** Measured twice (raw floats and Blink-rounded). |
| Why | Downstream code is **calibrated on the 1.2 constant.** Form-control heights (PR #41/#42) are the proven instance. |
| Shipped tonight | Both instruments + this writeup. **Zero engine change.** |

**Do not** re-derive this. The engine patch is saved verbatim at
`trench/forensics/2026-07-13-normal-lineheight-ENGINE.patch` (248 lines, applies to `8d7264d`).

---

## 1. The blocker that wasn't

Last digest (2026-07-12) escalated to Pete: *"text-metrics fixes are currently flown blind …
that tooling gap is the real unblock"*, and asked for on-seat Chrome-148 capture.

**That premise is false.** `baselines/chrome-148/<scope>/<case>/` already carries, for every
one of the 32 cases:

- `layout-rects.json` — Chrome's `getBoundingClientRect()` for every element
- `computed-styles.json` — Chrome's `getComputedStyle()` for every element

That is Chrome's ground truth, on disk, versioned. Any text-metrics fix can be A/B'd against
per-element geometry **without ever launching a browser.** Pete's decision #2 is therefore
half-answered: the epic is *not* blocked on tooling. (On-seat Chrome is still nice-to-have for
*new* fixtures — it is not needed to grind the existing board.)

Instrument shipped: **`scripts/probe_normal_lineheight.py`**.

---

## 2. Root cause

`crates/rustkit-css/src/lib.rs`:

```rust
/// Normal line height (use font metrics, typically ~1.2).   <-- the comment lies
Normal,
...
LineHeight::Normal => font_size * 1.2,                        <-- the code
```

`normal` is the initial value of `line-height`, so this fires on ~600 elements across the suite —
essentially every line of text on every page. It is the single most-executed wrong number in the
renderer.

Chrome never uses a ratio. Blink derives `normal` from the font and — critically — rounds the
ascent and descent to whole pixels **separately** before summing (`SimpleFontData`), so a
`normal` line box always lands on an integer.

### The derivation (measured, not guessed)

Chrome's column comes from the committed rects (leaf block box, single line, no vertical
padding/border ⇒ border-box height IS the line box height). RustKit's from its own shaper.

| font | size | RK ascent | RK descent | `round+round` | **Chrome** | flat 1.2 |
|---|---|---|---|---|---|---|
| system-ui | 16.0 | 15.47 | 3.38 | **18** | **18** ✓ | 19.20 ✗ |
| -apple-system | 14.0 | 13.54 | 2.95 | **17** | **17** ✓ | 16.80 ✗ |
| system-ui | 20.0 | 19.34 | 4.22 | **23** | **23** ✓ | 24.00 ✗ |
| system-ui | 40.0 | 38.67 | 8.44 | **47** | **47** ✓ | 48.00 ✗ |
| -apple-system | 11.0 | 10.63 | 2.32 | **13** | **13** ✓ | 13.20 ✗ |

Mean |error| vs Chrome across 20 pairs:

| model | mean error |
|---|---|
| **`round(ascent) + round(descent) + gap`** | **0.028 px** |
| raw float `ascent + descent + gap` | 0.396 px |
| flat `1.2 × font_size` (master) | 0.503 px |

Instrument shipped: **`crates/rustkit-layout/tests/normal_line_height_probe.rs`** (asserts the
target model is exact on ≥18/20 and beats flat-1.2; passes on master's engine — it characterizes
Chrome, it does not assert engine behaviour).

---

## 3. Why the correct model makes the board WORSE

Both variants were fully wired (10 resolution sites: `lib.rs` layout + **paint**, `flex.rs` ×8,
`grid.rs` ×2) and measured on the full 26-case board:

| model | board | avg | what moved |
|---|---|---|---|
| flat 1.2 (master) | **24/26** | **7.1** | — |
| raw float metrics | 23/26 | 7.3 | `gradient-backgrounds` → 15.18 FAIL; `image-gallery` 12.88 → 13.45 |
| Blink-rounded (0.028px!) | 23/26 | 7.4 | `css-selectors` **10.03 → 15.14 FAIL**; `image-gallery` 12.88 → 15.04 |

A model that matches Chrome to **0.028px** scores **worse** than one that is wrong by 0.503px.
That is not noise — it is a lock, and it means something downstream is holding the 1.2.

### The proven coupling: form-control heights

`css-selectors` regressed 10.03 → 15.14. Its form controls use the UA control font
**Arial @ 13.3333px** (added by PR #42, DIG-2).

- flat 1.2: `13.3333 × 1.2` = **exactly 16.00px**
- font metrics: `round(12.07) + round(2.82) + 0.44` = **15.44px**

PR #41/#42 composed control heights (author padding + border + content) and validated them to
`200x35.0 EXACT` against Chrome — **with 16.00px in the mix**. Flat-1.2 was accidentally *exactly
right* for Arial at the UA control size. Correcting `normal` shrinks every control by 0.56px, and
`css-selectors`' sections slide down the page.

So DIG-1/DIG-2's win was resting on a coincidence. It was real (the pixels moved, and stayed
moved), but it was load-bearing on a constant we now know is wrong. This is the same shape as the
emoji verdict: *a locally-correct fix can be globally negative until its neighbours are corrected
too.*

**Caveat, stated honestly:** form controls are the *proven* coupling (Arial is the one font/size
pair where the target model misses Chrome, and it is exactly the controls' font). `image-gallery`
has **no** form controls and still worsened (12.88 → 15.04), so at least one more coupling exists
and is NOT yet identified. Do not assume controls are the whole lock.

---

## 4. What the next session should do

The model is settled; the *order* is the open problem. Land it as one atomic change, not a
property-at-a-time grind:

1. **Find the other coupling(s).** `image-gallery` regressed with no form controls — start there.
   Use the rects instrument: diff RustKit's per-element geometry against
   `layout-rects.json` under BOTH models and rank elements by |Δy|. That names the dependents
   directly instead of inferring them from page scores.
2. **Re-derive the control-height composition against the corrected `normal`** (PR #41/#42's
   formula, re-validated with the rects instrument, not against 16.00px).
3. **Land model + dependents together**, gated on the board not regressing. Expect the payoff to
   be broad — this bug is on every line of text on every page, and `about` (the last KF builtin)
   is a pure text-metrics wall.
4. **Fix the lying doc comment** even if the model waits.

The `Arial 13.3333 → 16.00` Chrome row carried a `(SPREAD)` flag in the probe — its samples are
likely polluted by form controls, whose rect height is the control box, not a line box. Before
treating Arial as a genuine 1/20 model miss, re-derive it from *non-control* Arial text.

---

## 5. Falsified along the way

- **Prometheus's dead-property sweep pinned `object-fit`/`object-position`** (Class B, "highest
  campaign leverage … → images-intrinsic + image-gallery"). Cascade *is* dead as he describes
  (`rustkit-engine` has zero `object-fit` arms; `ComputedStyle` defaults to `"contain"`, and the
  spec's initial value is `fill` — so it is wrong twice). But by his own falsification rule it is
  **not a dig**:
  - **`image-gallery` contains ZERO `<img>` elements** — it *simulates* object-fit with
    pseudo-element placeholders. The "gallery section labels" suite-pressure claim was a
    class-name match.
  - **`images-intrinsic` is 9.35% and PASSES** its t10 threshold (it is KF only against the t8 CI
    micro cap), and its diff is **79.7% text_metrics / 3.6% replaced_content** — the contributors
    are the test1–test7 *label text*, not the object-fit tests 8–10.

  Ledger it as spec-correctness debt (real, latent, will bite on real pages with `<img>`), not as
  a parity dig.
- **`ObjectFit::from_css` has zero callers** and `ObjectFit::compute_rect` is called only by its
  own unit tests — but this is a *duplicate type* in `rustkit-image`, not proof the paint path is
  dead. `rustkit-layout` has its own `images` module with its own `ObjectFit`, and it IS live.
  Dedupe candidate; not a bug.

**Everything left on this board is one bug.** `about` (16.49, text wall), `image-gallery`
(77% caption text), `images-intrinsic` (79.7% text_metrics). The campaign's last mile is
`line-height: normal` and the constants calibrated around it.
