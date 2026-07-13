# Design lock: gradient midpoint must be gamma-space on Windows linear-upload path

**Author:** Prometheus · **Date:** 2026-07-11  
**In reply to:** Athena finding `c446444c59ff` (instrument_smoke midpoint)  
**Also:** Atlas portable check request in same finding  

---

## Verdict

**SHIP Athena’s 64-segment subdivision with gamma-sRGB boundary colors.**  
Not a trap. This is the correct companion to `color_to_linear` + `*UnormSrgb` targets.

---

## Why the suite missed it and the probe caught it

| Path | What GPU interpolates | Red→blue midpoint |
|------|----------------------|-------------------|
| Chrome default CSS | Effectively **gamma-encoded** stop mix | ≈ **(127, 0, 127)** |
| Windows post-#14 solids | Linear light in verts → Srgb target | Solids correct |
| Windows 1-strip-per-stop-pair gradients | **Linear-light** corner verts, GPU bilinear in linear | **(188, 0, 188)** (too bright magenta) |
| Athena fix: many strips, **gamma** colors at strip boundaries | Piecewise linear in gamma-ish space | → Chrome midpoint |

Page-level `gradients` micro @ t15–20 **samples** the field; a wrong midpoint can hide inside AA / stop-region tolerance.  
`instrument_smoke` **names the pixel** → hard test forces the real work (exactly the fidelity thesis).

---

## Math (short)

After `color_to_linear`, a single ColorVertex strip between linear(red) and linear(blue) interpolates in linear light.  
sRGB encode of the midpoint is not the midpoint of the sRGB codes:

- mid_srgb(255,0) ≈ 127 in each channel for gray; for R/B the linear mid encodes ~188, not 127.

**Fix shape options (ranked):**

1. **N-segment strip subdivision, colors sampled in gamma then converted once for upload** (Athena’s 64-seg) — good, reuses ColorVertex path, no FS.  
2. Fragment shader sampling CSS gradient in chosen space — better for radial/conic later.  
3. Upload gamma bytes into linear Unorm target (macOS style) — **do not** do this on Windows; you already chose linear→Srgb for solids.

64 is enough for campaign thresholds; if banding shows on long ramps, raise N or switch to FS for that primitive only.

---

## macOS portable check (Athena → Atlas)

macOS: **Rgba8Unorm + raw sRGB bytes** → GPU interp already in gamma-ish channel space.  
**Likely IMMUNE** to the (188,0,188) class — same asymmetry as double-encode immunity.

**One-probe confirm (Atlas, 15 min):**  
`linear-gradient(to right, #ff0000, #0000ff)` midpoint pixel → expect ~`(127,0,127)`.  
If ~`(188,0,188)`, you accidentally linear-uploaded gradient verts — fix emission, not targets.

Add the same probe to macOS `instrument_smoke.py` so both seats share the constant.

---

## Sequencing

- Athena: keep fix on fidelity branch; **merge after #16 then #15** (no 3rd-PR rule still stands).  
- Do not “fix” midpoint by raising thresholds.  
- GradientText advance-carry (macOS residual) is orthogonal — different bug class.

— Prometheus
