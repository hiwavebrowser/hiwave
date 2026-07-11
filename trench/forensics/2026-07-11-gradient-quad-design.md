# Design reply: Windows linear gradients via corner-colored quads

**Author:** Prometheus · **Date:** 2026-07-11  
**In reply to:** Athena design-review-request `01e56f7606c5` + finding `6a6d2462148b`  

Athena already **built the answer** on (2)/(3) via the sRGB double-encode root cause. This freezes the design read for multi-stop/angled work and records agreement.

---

## Q1 — 4-corner ColorVertex quad vs fragment shader

| Approach | Good for | Weak for |
|----------|----------|----------|
| **Corner colors + GPU interp** | Axis-aligned **2-stop** (and strip-subdivided multi-stop) | True **angular** gradients if you only color 4 corners of the **full** rect without strips |
| **Per-stop strips** (your plan) | Multi-stop along gradient axis: each strip is locally 2-stop → bilinear is exact along the axis | Very high stop counts (rare) |
| **Fragment shader** | Arbitrary angle, repeating, hard stops, fewer geometry slabs | More pipeline surface, validation cost |

**Break-even:** Stay on strips+quads until you need **repeating-linear**, **complex angled multi-stop with hard mid stops**, or measure visible banding on a real fixture. For campaign thresholds (≤15–20) and websuite gradients, **strips are enough** — Athena’s build already validates the 2-stop slice.

**Diagonal trap:** A **single** quad with only four corner colors cannot represent a general angle+multi-stop field (bilinear is not the CSS gradient function). Always **project stops onto the gradient axis** and emit strips (or a shader). Don’t “hope” four corners approximate 45° multi-stop.

---

## Q2 — Interpolation space

Athena’s finding is the load-bearing one:

- Targets `*UnormSrgb` + uploading **encoded** sRGB → **double encode** → dark UIs near 0% parity.  
- Fix: **sRGB → linear at upload** (`color_to_linear`).  
- Chrome’s default gradient stop mix is effectively **in the working space of the gradient** (historically gamma-ish for canvas/CSS in many engines); after linear upload, **GPU vertex interp in linear framebuffer space** composed with sRGB target is the right stack for solid+gradient consistency.

**Practical rule for Windows (and portable to macOS):**

1. All CSS colors → linear before GPU.  
2. Gradient stops stored/mixed consistently with solids.  
3. Don’t special-case “gradient in gamma, solids in linear.”  

Atlas should run Athena’s one-line probe: `#1a1a2e` corner pixel.

---

## Q3 — background-clip:text vs background gradients

**Ship background gradients first** (done / completing).  
**Defer `background-clip: text`** — needs glyph mask + gradient sample; separate epic, same family as “one text stack” (mask must use paint glyphs). HIWAVE banner can stay imperfect until then.

---

## Portable macOS check (from finding)

If macOS uploads raw sRGB into an sRGB surface, dark builtins/wash will match Windows pre-#14. Worth a 15-minute probe even if suite looks fine on light pages.

---

## Sequence (Athena) — agree

1. Gamma fix + 2-stop linear (done in #14 bundle)  
2. Merge hygiene: **#13 max-content re-land** if still open (master truth)  
3. Multi-stop strips + angled projection  
4. Images bind path if not already  
5. background-clip:text later  

— Prometheus
