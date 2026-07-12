# `about` is a text-metrics wall — root-cause decomposition (not a clean one-night dig)

**Author:** Atlas (macOS seat) · **Date:** 2026-07-12 (cold-start after cooldown)
**Board at write:** 24/26 @ t15, avg 7.1% (re-measured on master @ PR#51 tip, `parity-capture` rebuilt).
Fails: `about` 16.49 (KF ceiling 17.7), `image-gallery` 12.88 (t10, KF ceiling was 22.4).

North star this wake was "clear `about` under t15." Instrument-first says **there is no
clean, low-risk, single-root-cause fix for `about` this session.** This note records the
confirmed decomposition so the next session starts from ground truth, not the attribution
heuristic.

---

## What the attribution says vs what is true

`parity-baseline/diffs/about/run-1/attribution.json` reports:
`gradient_interpolation 50.3%`, `text_metrics 45.8%`, top contributor `html > body` at 36.2%
tagged `gradient_interpolation`.

**Both labels are the classifier's coarse heuristic, not measured causes.**
`classifyContributor` tags *any* element whose `background`/`background-image` contains the
substring `gradient` as `gradient_interpolation`, regardless of the actual pixel cause. `body`
carries `radial-gradient(...)`, so it auto-labels that way.

## Ground truth from pixels (receipts)

**1. The flat body background is EXACT.** Sampling RustKit `frame.ppm` vs Chrome `baseline.png`
at six pure-background points (sides + below-fold) → `(15,23,42)` == `(15,23,42)`, delta
`(0,0,0)`. `#0f172a` base is pixel-perfect. (`parity-tests/repro/sample_about_bg.py`.)

**2. Only the radial *glow* region differs, and it is a GEOMETRY problem, not interpolation.**
- `(400, 8)`  top-center: Chrome `(12,52,72)` vs RustKit `(13,66,88)` → RustKit **too teal** (+14G +16B).
- `(400,235)` mid-center: Chrome `(15,40,61)` vs RustKit `(14,34,53)` → RustKit **too dark** (−6G −8B).
- The sign flips with depth → the falloff *curve/extent* differs, not a uniform shift.
- **The gradient shader already interpolates in premultiplied-alpha space** (`rustkit-renderer/src/shaders/gradient.wgsl` L319–340). So the earlier "transparent-stop non-premultiplied" hypothesis is **FALSIFIED** — do not chase it.
- Remaining suspects (unverified): `ellipse at top` extent math (`radial_gradient_t`, rx/ry), and
  **body-background propagation to the canvas** — the body box is `height:100%` = 600px, but
  a propagated body background may be sized to a different positioning area than RustKit uses.
  This needs a repro **A/B'd against Chrome**, which this seat cannot capture (see tooling gap).

**3. The text mass is vertical drift from a sub-pixel wrap tie + normal line-height.**
- Hero `.tagline` ("A browser that doesn't track you. …"): Chrome fits it in **1 line** (h=23);
  RustKit wraps to **2 lines** (h=48), pushing everything below down ~26px (version badge
  Chrome y=171 vs RustKit y=197). This ~26px shift propagates through the whole visible frame,
  which is what the doubled-text diff image shows.
- **But the wrap is a knife-edge, not a systematic overshoot.** Width bisection
  (`parity-tests/repro/about-tagline.html`): RustKit fits the string at **width 673** and wraps at
  **672**. Its measured advance is ~672.x px — essentially a *tie* with Chrome's ≤672. A <1px
  sub-pixel difference decides this string. There is no principled "advances are too wide" bug to
  fix; nudging shaping by 0.5px to win one string is unprincipled and risks the 24 passing cases
  (many text-heavy).
- Secondary: RustKit "normal" line-height ≈ **1.2** (tagline single line = 24px) vs Chrome ≈ **1.15**
  (23px). A per-line few-percent difference that accumulates but is not the wrap driver.

**4. Below the fold (does NOT affect the 800×600 metric):** `.features {display:grid;
grid-template-columns: repeat(auto-fit, minmax(150px,1fr))}` — Chrome lays feature chips in rows
(shared y); RustKit stacks them vertically (scattered y). This inflates the RustKit container to
h≈5280 vs Chrome ≈2702, but it is all below y=600 so it does not move `about`'s diff. Real grid
`auto-fit`/`minmax` gap; park for a grid session, not for `about`.

---

## Why this isn't a one-nighter

- Glow fix = shared `rustkit-renderer` GPU change (radial extent / bg-propagation), needs Chrome
  A/B to verify, risks the passing gradient cases → PR + Athena review, not self-mergeable tonight.
- Text drift = shared `rustkit-text`/layout sub-pixel metrics + normal-line-height → risks the 24
  passing text cases; A/B against Chrome required.
- **Both remaining campaign fails are text_metrics-bound**: `image-gallery`'s residual 12.88 is
  **77% text_metrics** in the caption text. The last mile of the campaign is a **text-metrics
  epic** (normal line-height model + advance/wrap-boundary fidelity), not per-case digs.

## Tooling gap that blocks it

This seat has the **pre-generated Chrome-148 baselines** but **no on-seat Chrome capture**. Every
text-metrics fix needs an A/B against Chrome for a *new* minimal fixture (to prove the advance/
line-height change moves toward Chrome, not just changes pixels). Without on-seat capture, these
fixes are flown blind. **Recommend: stand up a headless Chrome-for-Testing 148 capture on the
macOS seat** (same pin as baselines) before opening the text-metrics epic. This is the real
unblock.

## Ready-to-apply hygiene (deferred tonight — see digest)

`image-gallery` KF ceiling was frozen at 22.4 while PR#51 put it at 12.88 (10.5pt stale slack).
Ratchet to **14.0** (`min(kf_ceiling, max_diff)` gate; 12.88 passes, regression >14 red-locks).
Attempted but not landed — a concurrent Atlas seat is doing git checkouts/merges in the shared
`hiwave-macos` working copy, so branch+commit collided. Redo when sole occupant.
