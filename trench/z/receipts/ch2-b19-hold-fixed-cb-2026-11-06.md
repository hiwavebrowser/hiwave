# CH2.B19 #935 hold: a fixed box is sized against the viewport (B15 fixed slice) — 2026-11-06

Batch 26 held #935: `consent_click_tests::a_fixed_overlay_in_a_zero_size_fixed_container`
failed ("a click at (-140, 94) on Agree was not heard"). Cause: a `position: fixed`
box took its offsets from the viewport but its **size** from the flow parent. The
consent overlay (`inset: 0; display: flex; justify-content: center`) inside a
zero-size fixed wrapper laid its items out in a 0 px line. Before #935, the clamp
put the dialog at x=0 by accident. With #935's unsafe centring it went to x −224.

## Commits on `atlas/z-ch2-b19-justify-unsafe`
- red `8bfb17f2`: `fixed_cb_width_tests` + `tools/parity_oracle/fixed_cb_width_cases.json`
  (6 pages, Chromium 143.0.7499.4, `grid_flexible_row_log.mjs --file … --write`). 5 wrong at 3e1af58c.
- fix `75a47bcd` (rustkit-layout only):
  - `fixed_sizing_block`: a fixed box is sized against the viewport width, less both
    insets when they are set with `width: auto`. It is used on both entry points
    (`layout_with_percent_base`, `layout_with_collapse_in`).
  - A fixed inset-definite flex container re-runs flex after the stretch, with the
    inset height as the row's definite cross size (`flex::layout_fixed_inset_flex_container`).
    `align-items: center` used to leave the dialog at y 0 when Chrome puts it at 226.

## Results
| case | 3e1af58c | 75a47bcd | Chromium 143 |
|---|---|---|---|
| inset0 flex overlay in a zero-size fixed wrapper | d −224,0 | d 76,226 | d 76,226 |
| inset0 block overlay, child width | 0 | 600 | 600 |
| width:50% in a 100px parent | 50 | 300 | 300 |
| padding-left:10% in a 100px parent | 30 | 80 | 80 |
| left/right 50px, child width | 100 | 500 | 500 |
| height:50% in a 50px parent | 300 | 300 | 300 |

## Gates
- rustkit-layout 896/0.
- Engine filters: consent_click 10/0 (1 ignored, iframe), `fixed_` 67/0, sticky_scroll 53/0, scroll_into_view 25/0, flex_justify_overflow 1/0.
- I stopped the remaining filters (select_popup … flex) for time; the batch runs the full suite.
- Campaign (`--profile parity`): base 3e1af58c sha256 73e44fdd…, candidate 75a47bcd sha256 782fec63…. Both 26/26, 1.1%, 0 cases moved.
- Chrome board: 42/42 rows identical, 13/42 green on both arms.
- 20-site A/B (`ch2-b19-hold-ab.txt`, base 3e1af58c vs 75a47bcd): **google is an AWAY mover.** The difference is 0.03% on all four cross pairs and 0.00% inside each arm (329 px, x 314–859, y 342–360). The search box's leading icon is a magnifier on the base and a "+" on the candidate. Pinned Chromium 143.0.7499.4 (one load, 1280x800) shows the magnifier. The likely cause is a fixed-position element in the search box that is now sized against the viewport; I did not have time to reduce it.
  - yahoo 34%, bing 24% and netflix 4.3% each have one B frame that matches A (noise inside an arm), so they are not movers. cnn: 4/4 timeouts on both arms.
  - The other 15 sites: 0.00%.
- Host: macOS seat (Darwin 25.5.0).

## Limits (disclosed)
- With both insets set, a `%` margin/padding on the fixed box resolves against the narrowed width.
- A transformed ancestor as the containing block for fixed (CH2.B13b) is not handled.
- The absolute analogue is not touched: the cross axis of an inset-stretched abspos row (flex.rs note at `container_cross_size`), and abspos children of static boxes (the rest of B15).
