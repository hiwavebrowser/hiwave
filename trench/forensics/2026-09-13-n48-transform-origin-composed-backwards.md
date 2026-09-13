# n48 — the renderer composed `transform-origin` backwards: every `scale()`/`rotate()` box painted at `M·o − o` from where it belonged

Date: 2026-09-13 (night block 48). Seat: Atlas (macOS). Branch `atlas/n48-scale-clipper-paints-nothing` from develop `da8f413`.

## Lane

n47's option (a) by the standing rule: repro section E — a `transform: scale(2)` box with `overflow: hidden; border-radius` — "paints nothing at all", ledgered as a renderer or display-list lane.

## What it actually was

Not a clip bug, and not "nothing". A seven-row variant repro (`scratch_n48/scale-variants.html`: scale alone / + overflow / + radius / + both / translate control / `matrix()` / centre origin) rendered on the n47 binary and read by `scratch_n48/probe.py` put the scaled fill of row 1 at **x 330, y 60** for a 60×20 box whose layout is at (110, 20) with `transform-origin: 0 0`. That is exactly `M·(p + o) − o` with `M = scale(2)`, `o = (110, 20)`: `(220, 40) + (110, 20) = (330, 60)`. Section E's box at (110, 300) went to y = 900, off the 480px frame — hence "paints nothing".

`Renderer::current_transform` (rustkit-renderer) composed each stack entry as

```
result * T(-origin) * M * T(+origin)
```

with `multiply_matrices_2d(a, b) = a · b` in the column-vector convention (b applies first). So the origin was moved the wrong way: `T(+o)` first, then `M`, then `T(−o)`. css-transforms-1 §6 wants `T(+o) · M · T(−o)`. Translations commute with each other, so every `translate()` on every board case was unaffected and the bug sat under the whole campaign; scale/rotate/skew were all wrong by `M·o − o`. The engine's geometry oracle (`own_transform_affine`, the layout-rects export) had the correct order all along, so the exported rect and the painted pixels disagreed for every scaled or rotated box — the very drift its comment says must not happen.

n47's `clip_entry_under`/`clip_quad_under` are correct; they take the composed matrix as given. `a_scaled_clip_scales_its_corner_radius` fed a raw scale matrix with no origin, which is why it passed.

## Fix (rustkit-renderer only)

`affine_about_origin(matrix, origin)` = `T(origin) · matrix · T(−origin)`, a free function so it is testable without a GPU; `current_transform` folds the stack as `outer · inner` through it. Five tests: scale about the top-left keeps the corner fixed and doubles the far corner (the repro numbers); scale about the centre grows evenly; rotate(90deg) about (100,100) sends (100,0) to (200,100); translate ignores its origin (the campaign's translate pixels stay identical); nested translate-outside-scale composes inner first. T-RED: with the old order restored, four of the five fail with the board's own numbers (the translate test passes by construction — that is the point of it). rustkit-renderer 75 → 80.

## Receipt

`parity-tests/repro/transform-origin.html` vs pinned Chrome 148 (`scratch_n48/chrome_repro/`, captured with `scratch_n48/chrome_repro.py` = generate_baselines' `captureBaseline`), seven rows: A scale(2) origin 0 0; B scale(2) centre; C the n47 section-E shape; D rotate(90deg); E scaleX(2) origin 100% 50%; F translate control with a non-default origin; G a translated child inside a scaled clipper.

Ink by color (`scratch_n48/ink.py`), develop `da8f413` + the fix (`b32ef78`):

| color | Chrome | before | after |
|---|---|---|---|
| `#aa33aa` fill | 11592 | 3285 (bbox x 150..399, y 60..499) | 11568 (bbox x 50..227, y 20..399) |
| `#33aa33` box | 9600 | 1000 (x 180..399) | 9600 (x 110..229) |
| `#ffcc00` shine (G) | 2400 (x 110..169, y 440..479) | 0 | 4800 (x 50..169; the extra half left of the button is #197's clip-order bug) |

Differing pixels vs Chrome per 70px row (`vs_chrome.py`): total **30850 → 7823**; rows A–E 6162/6106/5397/1979/3881 → 662/406/1112/779/781; row F (control) 785 → 785 flat; the residual on A–F is the 12px label's antialiasing (the same band F carries) plus row C/D corner and edge antialiasing. Row G 5840 → 3298 is the un-clipped half of the shine bar.

Stacked on #197 (the same fix on n47's branch, local only): total 30850 → **5437**, row G 5840 → 940 with shine 2400 = Chrome, and n47's `clip-transform-order.html` section E band **5209 → 897**, every other band byte-identical to n47's after-frame.

Operational note: the first pass of tonight's work was done ON n47's branch by accident — the `git checkout -b` sat inside a refused compound and I did not notice for an hour; the first fix used n47's `IDENTITY_2D` and `map_rect_axis_aligned`, so it silently depended on #197. Re-applied on develop with no shared helpers (a local `map_box` in the tests), n47's branch reset to its pushed tip `b7aa8a6`, board and WPT re-measured on the right tree. Cost: one extra release build (~9 min) and one extra board.

## Board

Census first (`cases/registry.json` sources, `transform:` declarations with scale/rotate/skew/matrix): new_tab (`scale(0)`, `scale(4)`, `scale(1.05)`, `scaleY(0)`, `translateX(4px) scale(1.02)`…), about (`scale(1.02)`, `scaleY(0)`, `scaleY(1)`), shelf (`scale(0.8)`, `scale(2)`, `rotate(90deg)`); every other case translate-only or none. Most of those are `:hover`/animation states off at rest, and `scaleY(0)` is singular (paints nothing either way), so the board's verdict is in the digest, not predicted here.

## Ledgered, not chased

- A rotated/skewed `overflow: hidden` clipper still keeps only a bounding box (n47 fallback) — now at the right place.
- `apply_backdrop_filter` intersects a document-space rect with the screen-space clip (n47 ledger, unchanged).
- The engine's whole-page scroll `PushTransform` uses origin (0,0), so it was never affected.
