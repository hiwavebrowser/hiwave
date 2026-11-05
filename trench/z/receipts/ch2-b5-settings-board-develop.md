# Chrome board — HiWave's own UI pages, RustKit vs Chromium (CH3.A1)

Run: 2026-11-05 11:40 UTC · head `e273c0bf` on develop `e273c0bf` · oracle Chromium 143.0.7499.4 · parity-capture `/Users/petecopeland/Repos/.worktrees/z-ch2-b5/target/parity/parity-capture`

Gate (PLAN-z CH0): every row ≤ 0.5% pixel diff. **0/1 rows green**, 1 over the gate, 0 not scored (a capture failed).

Pixel diff % is pixelmatch over the whole viewport (compare_baseline.mjs). Geometry diffs is the count of (box, axis) pairs more than 0.5 px from Chrome's rect on the join selector (layout_oracle_gate.compare_case). Top 3 is the attribution of the diff pixels to elements by selector; where fewer than three elements carry pixels, the worst geometry deltas fill in.

## Rows, worst first

| page | state | size | pixel diff % | geometry diffs | top 3 differing elements | notes |
|---|---|---|---:|---:|---|---|
| settings | default | 1280x800 | 1.661 | 256 | `html > body` 47.5%; `body > div.container` 4.8%; `body > div.container > div.section:nth-of-type(1)` 4.6% |  |

## Pages

| page | rows | green | worst state | worst pixel diff % |
|---|---:|---:|---|---:|
| settings | 1 | 0 | default 1280x800 | 1.661 |

## CSS census red list per page

Census 2026-11-03 (`CSS_PROPERTY_CENSUS_2026-11-03.json`, oracle 143.0.7499.4): 212 red properties. Per page, the red properties the page declares (in its `<style>` blocks and `style=` attributes).

| page | declared properties | red | red properties |
|---|---:|---:|---|
| settings | 60 | 19 | `-webkit-text-fill-color` (parse), `accent-color` (unsupported), `animation` (parse), `animation-delay` (parse), `animation-duration` (parse), `background-clip` (parse), `box-shadow` (parse), `cursor` (unsupported), `display` (computed), `flex-direction` (computed), `font-family` (computed), `letter-spacing` (computed), `outline` (unsupported), `scrollbar-color` (unsupported), `scrollbar-width` (unsupported), `text-align` (computed), `text-transform` (computed), `transition` (parse), `transition-duration` (parse) |

## States

Actions run identically by parity-capture `--actions` and chrome_board.mjs:

- `default`: `[]`
