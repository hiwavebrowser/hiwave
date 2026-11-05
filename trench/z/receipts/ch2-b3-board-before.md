# Chrome board — HiWave's own UI pages, RustKit vs Chromium (CH3.A1)

Run: 2026-11-05 11:09 UTC · head `e273c0bf` on develop `e273c0bf` · oracle Chromium 143.0.7499.4 · parity-capture `/Users/petecopeland/Repos/.worktrees/z-ch2-b3/target/parity/parity-capture`

Gate (PLAN-z CH0): every row ≤ 0.5% pixel diff. **0/1 rows green**, 1 over the gate, 0 not scored (a capture failed).

Pixel diff % is pixelmatch over the whole viewport (compare_baseline.mjs). Geometry diffs is the count of (box, axis) pairs more than 0.5 px from Chrome's rect on the join selector (layout_oracle_gate.compare_case). Top 3 is the attribution of the diff pixels to elements by selector; where fewer than three elements carry pixels, the worst geometry deltas fill in.

## Rows, worst first

| page | state | size | pixel diff % | geometry diffs | top 3 differing elements | notes |
|---|---|---|---:|---:|---|---|
| chrome | default | 1280x800 | 3.185 | 210 | `#chromeMain` 72.3%; `#tabs` 1.8%; `body > aside.sidebar:nth-of-type(1) > section.sidebar-section workspace-section:nth-of-type(3)` 1.6% |  |

## Pages

| page | rows | green | worst state | worst pixel diff % |
|---|---:|---:|---|---:|
| chrome | 1 | 0 | default 1280x800 | 3.185 |

## CSS census red list per page

Census 2026-11-03 (`CSS_PROPERTY_CENSUS_2026-11-03.json`, oracle 143.0.7499.4): 212 red properties. Per page, the red properties the page declares (in its `<style>` blocks and `style=` attributes).

| page | declared properties | red | red properties |
|---|---:|---:|---|
| chrome | 93 | 36 | `-webkit-text-fill-color` (parse), `-webkit-user-select` (unsupported), `animation` (parse), `animation-delay` (parse), `animation-duration` (parse), `animation-fill-mode` (parse), `animation-iteration-count` (parse), `appearance` (unsupported), `backdrop-filter` (unsupported), `background-clip` (parse), `background-image` (parse), `background-position` (parse), `background-repeat` (parse), `background-size` (parse), `border-style` (parse), `box-shadow` (parse), `cursor` (unsupported), `display` (computed), `filter` (parse), `flex-direction` (computed), `font-family` (computed), `letter-spacing` (computed), `outline` (unsupported), `outline-color` (unsupported), `outline-offset` (unsupported), `overscroll-behavior` (unsupported), `scrollbar-color` (unsupported), `scrollbar-width` (unsupported), `text-align` (computed), `text-decoration` (parse), `text-transform` (computed), `transform-origin` (parse), `transition` (parse), `transition-duration` (parse), `user-select` (unsupported), `z-index` (computed) |

## States

Actions run identically by parity-capture `--actions` and chrome_board.mjs:

- `default`: `[]`
