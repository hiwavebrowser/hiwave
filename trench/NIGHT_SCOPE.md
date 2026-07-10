# Night scope — 2026-07-10 (Epic: scroll/sticky/overflow, Day 1)

**Plan of record:** trench/PATH_FORWARD.md (adopted). Atlas epic day 1.
**Committed basis:** 21/26 (80.8%), avg 11.4. Top-5 fails:
sticky-scroll 48.10 (t25) · css-selectors 26.67 · about 24.82 ·
image-gallery 21.54 (t10) · settings 20.14.

## Day-0 forensics (Atlas, live — build on these, do not re-derive)
sticky-scroll's 48% decomposes visibly in the TOP 400px alone (receipts:
scratchpad crops, session a5db52cf):
1. **`.article-image` hero gradient does not paint** — plain
   `linear-gradient(135deg, #667eea, #764ba2)` via `background` shorthand,
   `height:200px; display:flex`. The SAME form paints on
   gradient-backgrounds, so the failure is CONTEXTUAL (inside the grid main
   column / flex child). Find the paint-path divergence; this is the
   single biggest pixel mass on the page.
2. **Sticky header scatters** — `header { position:sticky }` (mapped to
   Static per #23's deliberate deferral) should render as a normal white
   bar with logo+nav inside; instead nav floats at the very top-right,
   logo lands overlapping the sidebar. Its INNER layout is broken
   independent of stickiness — likely the header's flex row + the known
   inter-link whitespace gap ("FeaturesPricing").
3. Left sidebar (sticky→static) renders acceptably — stickiness itself is
   NOT tonight's problem. css-text §4 whitespace in nav links is visible.

## Tonight, in order (cap ~3h)
1. Hero-gradient paint dig: minimal repro = gradient div inside the page's
   grid/flex context; A/B against a bare copy. Fix in the paint path.
2. Header inner layout: y-table the header subtree vs Chrome rects
   (CAUTION: layout.json exports PAINT order for positioned trees — pair
   by geometry, not index, or read structure from the block dump).
3. Re-measure; expect sticky-scroll to move for the first time all
   campaign. Overflow/scrollport clip design notes for day 2 if time.

Parser-SSO chore queue (interleave, one per two feature PRs): parse_color
gradient/shorthand island in engine → rustkit-css (audit P1 list).
