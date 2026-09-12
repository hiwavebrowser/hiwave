# n47 — the renderer clipped in pre-transform space, so a transformed descendant escaped its ancestor's `overflow: hidden`

Night block 47, 2026-09-12. Lane: the n46 digest's option (a), taken by the standing rule (no Pete answer; the exchange carried only Argos gauge snapshots). Basis: develop `da8f413` (unchanged since n45; #193, #194, #195 open), campaign 26/26 avg **2.6245**, WPT Tier-1 24/26.

## What was wrong

`rustkit-renderer` kept `clip_stack` in document space and `transform_stack` separately; `draw_clipped_quad` cut a quad against the clip rect and only then `push_color_quad` ran `transform_point` on the surviving pieces. The four textured sites (glyphs, color glyphs, `draw_image`, background tiles) did the same: `clip_textured_rect(self.current_clip(), …)` then transform the corners. So every quad was clipped against where it would sit WITHOUT its transform.

The layout side emits `PushClip` for an `overflow: hidden` box after the box's own content and BEFORE its children; a child with a `transform` then gets `PushTransform … PopTransform` around its subtree. Order on the about page: button clip (identity) → `::before` transform `translateX(-100%)` → the pseudo box's gradient. Result: the pseudo box, once #195 sizes it to the button (inset stretch), painted as a 230×50 bar LEFT of the button where Chrome clips it away entirely — about 5.2462 → 6.7731 on #195. Every shine-sweep / slide-in / marquee idiom on real pages has the same shape.

## The fix (rustkit-renderer only, PR #197 to develop)

- **Clip entries are stored in screen space.** `push_clip_rounded` → `clip_entry_under(current, current_transform(), rect, radius)`: the command's document-space rect is mapped through the transform in force when the clip is pushed. A clip pushed inside a transformed box moves with the box; a clip pushed under identity is unchanged. Under an axis-aligned scale the radii scale by √|a·d|; under a rotation/skew only the bounding box is kept (ledgered).
- **Quads are mapped before they are clipped.** `draw_clipped_quad` → `clip_quad_under(m, clip, rect, out) -> QuadSpace`. Identity: `collect_clipped_pieces` unchanged (a test pins that the pieces are the old pieces). Axis-aligned (translate/scale — every board case, and the engine's whole-page scroll translate): map the rect to screen space, clip there, emit via `push_screen_quad` with no second transform. Rotation/skew: the clip's rect is brought back to document space through `invert_matrix_2d` as a bounding box and the quad is clipped pre-transform — the old behaviour as the fallback.
- **Textured quads follow the same law** through one method, `textured_corners(rect, tex)`, replacing the four hand-rolled sites; `clip_textured_under` mirrors `clip_quad_under` and flips the texel order under a negative scale.

rustkit-renderer 67 → 75 tests.

## Receipts

`parity-tests/repro/clip-transform-order.html`, 400×480, pinned Chrome 148 via `scratch_n36/chrome_capture.py`; `scratch_n47/vs_chrome.py` pixels differing from Chrome per 70px band:

| section | before | after |
|---|---|---|
| A `translateX(-100%)` inside overflow:hidden (the about idiom) | 5928 | 1550 (label antialiasing; the bar is gone) |
| B `translateX(-50%)` | 5253 | 1253 (the left half yellow, nothing outside) |
| C translated clipper (control: the clip moves with the box) | 597 | 597 |
| D text in a translated child | 4840 | 1247 (glyphs clip at the button edge) |
| E scaled rounded clipper | 5209 | 5209 (nothing painted before or after) |
| F centred `translate(-50%,-50%)` (control) | 744 | 744 |

Campaign board on develop + fix: 26/26 byte-flat at 2.6245 — no board case has a non-zero-size transformed descendant of a clipper until #195. Stacked on #195 (`atlas/n47-stacked-195`, local only): about 6.7731 → **5.2338**, campaign avg 2.6832 → **2.6240**, 25/26 byte-flat. `framediff.py` on the about frame: the only moved pixels are the shine bar's 11,628 (bbox x 0–233, y 262–311); `vs_chrome.py` rows 240–319: 11,478 → 1,858. WPT 24/26 flat, pinned on `d65f906`.

## A correction to n46

n46 attributed the `.hero::before` glow residual on about (rows 160–199, ~1k px) to the same clip-order bug. It is not: `.hero` has no overflow clip, and this fix moves no pixel in those rows (vs_chrome 1509 before and after). That residual is the glow's radial gradient rendering itself.

## Ledgered, not chased

- **Section E:** a `transform: scale(2); transform-origin: 0 0` box with `overflow: hidden; border-radius: 10px` paints nothing in RustKit — not its own background, not its child — while its layout is correct (60×20 at 110,300). Independent of this change (blank before and after); something upstream of the clip drops paint under a scale. Worth its own night: `scale()` on cards/thumbnails is common.
- Rotated/skewed clippers: bounding-box clip only, rounded part dropped in the fallback.
- `apply_backdrop_filter` still intersects a document-space rect with the now screen-space clip (differs only under a transform).
- The GPU gradient queue (`RUSTKIT_GPU_GRADIENTS=1`, off by default) ignores clips and transforms as before.
- The `PushClip` of the engine's scrolled frame: every clip pushed under the scroll translate is now in screen space, as is every quad — consistent both before and after; no scrolled board case moved.
