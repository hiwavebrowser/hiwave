# n44 — currentColor reaches inline SVG; `:focus-within`/`:hover` on an ancestor matched with the state off; a stroked circle was two discs

Night block 44, 2026-09-09. Lane: the n43 digest's option (a) — currentColor through the Image command — taken because every queued PR (#174–#188) landed and develop was promoted to master (#190) on 2026-09-08. Basis: develop `afd73ab`, fresh clean-tree parity-capture, campaign avg **2.6944** (matches the #188 receipt exactly). Branch `atlas/n44-svg-currentcolor` → PR to develop.

## The lane as planned: currentColor (rustkit-svg + rustkit-layout + rustkit-engine + rustkit-renderer)

`Paint::CurrentColor` existed in rustkit-svg but `as_color()` resolved it to `Color::BLACK` ("would need context"). Every `fill="currentColor"` / `stroke="currentColor"` icon — the idiom on essentially every real page's nav/buttons, and the shelf's search icon — painted black.

Fix: the CSS color is a render-time input, not an authored SVG property.
- `SvgStyle.current_color` (default black), copied unconditionally in `inherit_from`; `fill_color()` / `stroke_color()` resolve through `Paint::resolve(current)`. All 12 shape sites switched from `paint.as_color()`.
- `SvgDocument::render_with_color(x, y, w, h, current_color)`; `render()` keeps black (an `<img src=*.svg>` is its own document — initial `color`).
- `DisplayCommand::Image` gains `current_color: Color`, filled from `layout_box.style.color` in `render_replaced_content`; the engine's svg splice passes it to `render_with_color`. The raster lane ignores the field.

Receipt on `parity-tests/repro/inline-svg.html` (`.icon-wrap { color: #6b7280 }`) vs the pinned-Chrome capture (`scratch_n38/chrome-inline-svg/baseline.png`, `scratch_n44/icon_color.py`): icon-gray pixels 0 → 64 at bbox (241,25)-(252,36) vs Chrome (242,25)-(251,34); near-black pixels 149 → 80 = Chrome's 80.

## What the first colored pixels exposed

**The board read byte-flat on the currentColor fix alone (26/26) while the shelf frame had changed.** Pixel-diffing the banked before/after frames (`scratch_n44/captures_develop_basis` vs `captures_with_fix`) showed the icon at (31,68)-(41,79) had gone from black to **`#22d3ee`** — the shelf's `--accent-hover`, i.e. the `.command-input-wrapper:focus-within .command-input-icon { color: var(--accent-hover) }` rule — with a **white disc** inside the ring. The t15 meter counts a wrong-color pixel the same whichever wrong color it is; the frame crop is the only instrument that sees a color lane.

### Bug 2 — pseudo-classes on an ancestor compound were never evaluated
`rustkit-engine` `simple_selector_matches_ancestor` (every non-subject compound of a descendant/child/sibling selector) parses tag/class/id and `break`s at the first `:` or `[`. So `.wrap:focus-within .icon`, `.card:hover .title`, `a:hover span` matched with the state off on every page. Separately, `match_pseudo_class` (subject compound) ends in `_ => true` and its static-false list was `hover|focus|active|visited` only — `:focus-within`, `:focus-visible`, `:target` matched everything.

Fix: one `pseudo_class_is_static_false(name)` (hover, focus, focus-within, focus-visible, active, visited, target, target-within) consulted by both matchers; the ancestor matcher now reads the pseudo name and fails the compound on a static-false one, still skipping structural pseudo-classes and attribute selectors on ancestors (no sibling context in the ancestor tuple — ledgered). T-RED: the new engine test failed on the subject-only fix with the board's own number (`left: (34, 211, 238)`).

Board effect: shelf's whole search bar row moved (diff bbox x 16–1264, y 53–94) — the `:focus-within` border-color and the `::after` glow were also on. new_tab −0.09 from the same class of rule.

### Bug 3 — `StrokeCircle` was a colored disc plus an opaque white disc
`rustkit-renderer` drew a stroked circle as `draw_fill_circle(r, color)` then `draw_fill_circle(r − w, WHITE)` ("simplified approach"). Every `fill="none"` circle icon on a dark surface carried a white disc, and the stroke sat inside the geometry rather than centred (SVG 2 §13.4: r ± w/2). Fix: `draw_ring(cx, cy, r + w/2, r − w/2, color)` — a triangle strip between the two radii; inner ≤ 0 degrades to a disc.

Shelf icon after (row 71, x 29–42): `334155 94a3b8 94a3b8 334155 … 94a3b8 94a3b8` — ring in Chrome's `rgb(148,163,184)`, interior the toolbar background.

## Board
Campaign 26/26 avg **2.6944 → 2.6258** on `atlas/n44-svg-currentcolor` (shelf 4.6185 → 2.9264, −1.69pp; new_tab 2.6835 → 2.5924, −0.09; form-controls +0.0001; 23 of 26 byte-flat). Suites: rustkit-svg 16/16 (+1), rustkit-layout 369 (+1), rustkit-renderer 64, rustkit-engine 82/82 (+1).

## Ledger (not chased)
- Structural pseudo-classes and attribute selectors on ancestor/sibling compounds still match unconditionally (`ul:nth-child(2) li`, `[hidden] p`).
- `match_pseudo_class` `_ => true`: an unknown pseudo-class should invalidate the selector, not match it. Wide-blast change; needs its own board.
- `<g>` nesting in rustkit-svg is still flat; `color` set inside the svg (`<svg color=…>` or a CSS rule on a shape) does not override the inherited CSS color.
- Ellipse/polyline stroke widths in the renderer not audited for the same two-disc pattern.
- new_tab is 2.68 on this basis vs 2.26 on n43's — with #182 (auto-fit) and #184 (column basis) both merged. The n42 digest predicted the pair would take it below basis; it did not. Re-table it.
