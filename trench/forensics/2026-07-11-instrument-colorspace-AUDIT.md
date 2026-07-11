# Instrument audit: is the parity comparison color-space honest?

**Author:** Prometheus · **Date:** 2026-07-11  
**In reply to:** Atlas tasking `db5ae823b5d9` review_2  
**Hub rev:** `hiwave/hiwave-macos` @ `1b56b01`  
**Scope:** read-only — `tools/parity_oracle/*`, `crates/rustkit-compositor` capture path, `pixelmatch@5.3.0`

---

## Verdict (one line)

**Sensor is color-space-consistent for the macOS stack (raw sRGB bytes vs Chrome sRGB PNG), but has three real biases: forced-opaque alpha, `includeAA:true` (stricter than pixelmatch default), and YIQ-on-encoded-RGB which is roughly perceptual — not systematically dark-UI-hostile the way Athena’s *render* double-encode was.**

Campaign rankings from layout/geometry bugs remain trustworthy. Do **not** re-rank the suite solely for gamma instrument fear.

---

## (a) PPM path — bytes unmodified?

| Stage | Format | Conversion? |
|-------|--------|-------------|
| Offscreen capture target | `Bgra8Unorm` (`capture_frame_with_renderer`, compositor ~L817) | Linear *texture format*; pipelines write **raw sRGB bytes** (same intentional macOS convention Atlas confirmed immune to Windows double-encode) |
| GPU readback | `copy_texture_to_buffer` → map | None |
| PPM write | P6 max=255 | **BGRA → RGB channel reorder only**; alpha **dropped** |
| Oracle load | `ppmToRgba` | R,G,B copy; **A forced to 255** |
| Chrome baseline | Playwright PNG | sRGB-encoded RGBA |

**Conclusion:** No sRGB↔linear conversion on the instrument path. Capture is “sRGB-in / sRGB-out” under the macOS linear-target convention. Matches Chrome PNG encoding for solid opaque UI.

**Not** the same stack as Windows post-#14 (linear values into `*UnormSrgb`). Cross-seat score comparison is fine only because both ends match their own display convention to Chrome.

---

## (b) Does threshold 0.1 over/under-weight dark UIs?

pixelmatch math (v5.3.0):

```
maxDelta = 35215 * threshold²   // ≈ 352.15 at threshold 0.1
delta    = 0.5053·ΔY² + 0.299·ΔI² + 0.1957·ΔQ²   // YIQ, on 0–255 channel values
```

Channels are treated as **encoded** RGB numbers (no inverse-sRGB). That is the library’s design for screenshot testing, not a linear-light ΔE.

| Claim | Assessment |
|-------|------------|
| “Dark pages systematically over-scored” | **Mostly false as instrument bias.** Equal *channel* errors produce comparable YIQ delta across luminance; pure Euclidean RGB would under-penalize darks in perceptual space — YIQ is the opposite of Athena’s render bug. |
| “Darks-worst / whites-fine suite pattern” | Still a **render** signal (Windows double-encode), not a pixelmatch artifact. macOS probe (26,26,46 exact) proves instrument can report darks correctly when the renderer is honest. |
| Threshold 0.1 | Permits ~√352 ≈ 18.8 YIQ units — roughly a few LSBs of R/G/B before counting a pixel. Geometry/color misses of tens of channels still fail. |

**Residual instrument nuance (not campaign-breaking):** sub-threshold AA fringe on dark-on-dark chrome can hide more easily than white-on-white if both sides share the error. Our `includeAA: true` *removes* that leniency (see c).

---

## (c) Silent normalizations after R0 hard-fail

| Normalization | Status | Effect |
|---------------|--------|--------|
| Dimension crop | **Hard-fail** unless `RK_ALLOW_CROP=1` | R0 closed the “cropped score reads as render” lie |
| Alpha | **Forced 255** on PPM path | Semi-transparent layers / wrong composite become opaque RGB vs Chrome’s true alpha blend — can invent or hide diffs on glass/scrim UI |
| AA handling | `includeAA: true` (both `compare_pixels.mjs` and `compare_baseline.mjs`) | **Stricter** than pixelmatch default (`false`). AA fringe counts as real diffs → slightly higher scores, better for catching edge shifts |
| Color space | None | Honest under macOS convention |
| Channel order | BGRA→RGB | Correct for capture format |

---

## Ranked residual risks (instrument only)

1. **Alpha discard** — any case with opacity / overlays (settings toggles, sticky headers with scrims) can disagree with Chrome for non-render reasons.  
2. **`includeAA:true`** — good for geometry; do not compare scores naively to external pixelmatch runs that leave AA ignored.  
3. **Cross-OS capture format drift** — if Windows parity ever dumps from `*UnormSrgb` without decoding, instrument would double-encode on the *sensor* side. Document seat capture contract in registry/pin.  
4. **Compositor format fallback** (Atlas residual): if surface falls back to an Srgb variant while capture stays Unorm, live window ≠ PPM. Low on Metal; harden prefer-non-Srgb.

---

## Falsification fixtures

| # | Fixture | Pass criterion | Fail signature |
|---|---------|----------------|----------------|
| F1 | Solid `body{background:#1a1a2e}` capture | Corner PPM RGB = (26,26,46) | (~90,90,118) or wrong channel swap |
| F2 | Two identical solid PNGs, one channel ±1 on mid-gray vs near-black | Both under threshold at 0.1 (or both over for ±5) | Only dark fails → unexpected dark bias |
| F3 | 50% black overlay rectangle vs Chrome | If scores diverge while layout rects match | Alpha-force-255 instrument lie |
| F4 | Deliberate wrong-size capture | Score 100, taxonomy `instrument/dimension_mismatch`, no crop | Soft crop or score <100 |

---

## Recommendations (no code from this seat)

1. Keep ranking by current scores for layout digs.  
2. Add F1 as a permanent instrument smoke in baseline-audit CI (cheap).  
3. Document in `cases/registry.json` pin: capture = raw sRGB bytes in Unorm target; alpha discarded.  
4. When Windows joins the same oracle, assert capture color contract in registry, not in folklore.

— Prometheus
