# line-height:normal metrics — the form-recompose blocker is FALSIFIED; the wall is dense-text paint

> **Night 16 (2026-07-16), macOS seat (Atlas).** Instrument-first close of the atomic
> text-metrics epic's central premise. Companion patch: `2026-07-16-lineheight-metrics-ENGINE.patch`
> (248 lines, the full model wired into every `line_height.to_px` site).
> **Supersedes the blocker framing in:** `2026-07-15-text-metrics-ATOMIC-KICKOFF.md` §3–4 and
> `2026-07-13-text-metrics-ATOMIC-IMPLEMENT.md` §4.4 ("form recompose = last blocker").

## TL;DR

Built the metrics model into the engine (`resolve_line_height` = Blink-rounded
`round(ascent)+round(descent)+leading`, memoized) and **measured the real board on
an identical binary base**. Result:

- **image-gallery 12.88 → 6.80 PASS** — the atomic payoff is real and confirmed.
- **css-selectors 10.03 → 15.14 FAIL** — the regression is real and reproducible.
- **Board net-flat: 24/26, avg 7.1** (gallery +1, css-selectors −1).

The three-night assumption that **form-control recomposition** is the last blocker is
**falsified by per-element geometry.** The css-selectors regression is **diffuse dense
small-text sub-pixel paint divergence**, not form controls. The atomic epic *as scoped*
(model + form recompose) **cannot reach 25/26**. The remaining wall is a **text-paint
fidelity** problem — a different, larger lane.

## What was measured (clean A/B, same binary base)

Rebuilt `parity-capture` twice from the same tree (`d8b8900`, #53 tip): once with the
248-line metrics patch, once with it stashed (master flat-1.2). Same sensor, same
baselines. Delta is *only* the 4-file engine diff.

| Case | master (flat 1.2) | metrics WIP | Δ |
|---|--:|--:|--:|
| image-gallery (t10) | 12.88 | **6.80 PASS** | −6.08 |
| css-selectors (t15) | 10.03 PASS | **15.14 FAIL** | +5.11 |
| board | 24/26 | 24/26 | 0 |

## Why it is NOT form controls (the falsification)

1. **The model is exact on css-selectors' body font.** `#52`'s engine-driving probe
   (`tests/normal_line_height_probe.rs`) run under the WIP: **19/20 exact**, including
   every `-apple-system`/`system-ui` pair css-selectors uses (14px→17.00, 12px→15.00).
   The *only* miss is `Arial 13.33 → 15.44 vs Chrome 16.00 (−0.56)` — the form-control
   default face. So general text is modeled correctly; controls are the only miss, and
   they are a small minority of the page.

2. **`layout_form_control` is already decoupled from line-height.** Control heights come
   from `(font_size + 1.0) + author_pad_border` (the DIG-1/DIG-2 author-pad branch) or a
   blob constant `fs*1.5+8/12` — **never** `line_height.to_px`. The metrics change does
   not move control border-boxes. Night-13's "controls shrink 0.56px" coupling was closed
   by the author-pad recompose that shipped *after* it.

3. **Per-element geometry: the WIP IMPROVES css-selectors' section heights.** Section
   heights vs Chrome (`parity-tests/probe/csssel_compare.py`):

   | section | master Δh | metrics Δh |
   |--:|--:|--:|
   | 1 | +2.8 | +4.0 |
   | 2 | −1.4 | **0.0** |
   | 3 | −5.4 | −4.0 |
   | 4 | +3.7 | +5.3 |
   | 5 | −1.6 | **0.0** |
   | 7 | −1.2 | **0.0** |
   | 8 | −1.2 | **0.0** |

   Geometry got *closer* to Chrome, yet the pixel score got *worse*. That is the night-13
   paradox, now localized: **the divergence is in text paint, not box layout.**

4. **Attribution is identical in shape, larger in magnitude.** Both master and WIP:
   `text_metrics 45.76%`, same top contributors (`html>body` 13.7%, each section 3–5%).
   The diff is **diffuse across all text**, not a hotspot. Correct line boxes shift every
   glyph baseline onto a sub-pixel offset that antialiases *differently* from Chrome
   across ~100 small-text lines → +5pp. image-gallery (large text, few lines) aligns
   better under the same model, so it flips to PASS.

**Named suspect for the paint wall:** the glyph atlas rasterizes cells at
`ceil(font_size*1.2)` (`rustkit-text/.../macos.rs`, ATOMIC-IMPLEMENT §4.3, marked
OUT OF SCOPE). With layout now using metrics `normal` (e.g. 17.0) while the atlas cell
still assumes 1.2 (16.8), the glyph bitmap's vertical seat inside the line box is off by a
fraction on every line. This is consistent with "geometry improved, pixels diverged" and
is the honest next dig — but it is glyph-rendering work (glyph tests required), not a
capped-session constant tweak.

## Second, separate finding: section-6 `.buttons` is 3.5× too tall (PRE-EXISTING)

Section 6 (":not()", three inline-block `<button>`s, `padding:8px 16px`) renders
`.buttons` at **h=124.6 vs Chrome ~35**, inflating the section +85px and shoving
sections 7–8 down ~83px. **This is identical on master and WIP (±1px)** — a pre-existing
layout bug, not the atomic regression. In the RustKit box tree the three buttons are
**absent as child boxes** under `.buttons`, yet the container carries 124.6px of height —
the form-control path is mis-laying them. Real bug, worth its own dig, but it does **not**
unblock the epic: fixing it helps master and WIP *equally*, so it does not close the +5pp
gap (which is spread across all text, not concentrated in section 6).

## Decision

**Do NOT ship the model-only atomic PR.** It flips a passing case to failing (gate §5
violation; the night-13/14 anti-pattern). Board would stay 24/26 with css-selectors red.
The kickoff's land-order step 4 (form recompose) is a no-op for the actual coupling.

**Preserved, not thrashed** (per KICKOFF §5 "named residual → stop, one-pager, no constant
thrash"): the 248-line model is banked as `.ENGINE.patch` and as a DO-NOT-MERGE checkpoint
on `atlas/text-metrics-atomic`. It is verified-correct (0.028px), just not landable until
the text-paint lane closes.

## For Pete / seats (≤3)

1. **The text-metrics epic's blocker is re-named, with receipts:** not form controls
   (falsified) — **glyph-atlas / text-paint sub-pixel fidelity**. That is a larger lane
   (touches all text rendering, needs glyph tests). Greenlight it as its own epic, or park
   the metrics model until a paint-fidelity session?
2. **PR #53 (grid span gutters) is still OPEN, approved, mergeable** — this seat can't
   `gh pr merge`. It is the honest prerequisite for the gallery win. Merge it?
3. **`.buttons` inline-block stacking** (section 6, +85px, pre-existing) is a real,
   isolated layout bug surfaced tonight — queue it as a normal parity dig?

— Atlas, macOS seat, 2026-07-16
