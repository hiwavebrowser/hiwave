# n52 — a grid item's rem padding resolved against its own font size; a flex item's height was its children's margin-box sum (rustkit-layout)

**Date:** 2026-09-17 (night block 52, macOS seat). **Lane:** n51 option (a) by the standing rule (no Pete answer on the exchange): new_tab's last two terms — `.shortcut` 57 for Chrome's 60 on every row, and `.container` 32px taller than its content. Develop is still `da8f413`; PRs #193–#201 all open.

## The ledger lines were both mis-attributed

n51 carried them as "the two-line label's line boxes under `align-items: center`" and "the footer paragraph in flow". Neither. The footer (`position: fixed; bottom: 1rem`) already sits at Chrome's y = 769 (its x is 0 for Chrome's 571 — a fixed child of a flex container takes its static position as the sole item, so `align-items: center` applies; ledgered below). And the flex cross-size math was right all along.

**Method that found it:** a CSS bisect of `new_tab.html` itself (`scratch_n52/bisect.py`, 28 variants, each captured through parity-capture and read at `.container` / `.shortcuts` / `.shortcut`). Removing box-sizing, animations, transitions, body flex, `::before`, overflow, position, text-align, hover rules, min-height, the kbd font/weight/border, the label's `flex: 1`, `gap`, `align-items` — every one left the rows at 57/47. Converting the `.shortcut` rules from rem to px moved them to 60/50 and the grid to Chrome's 400. Twenty minutes; reading flex.rs would not have found it, because the wrong number was set before flex ran.

## Bug 1 — grid.rs placement pass: `to_px(font_size, font_size, …)`

The grid's item placement resolves each item's padding/border with `Length::to_px(font_size, root_font_size, container)` and passed the item's OWN font size as the root. Every `rem` on a grid item resolved like `em`: `padding: 0.75rem 1rem` on a 14px `.shortcut` = 10.5 / 14 instead of 12 / 16 — 3px short in height (57 for 60, 47 for 50), the first key at x 387 for Chrome's 389. The Phase-1 height estimator (`estimate_content_height`) had the same call. Both now pass 16.0, the crate's convention (`length_to_px`, `intrinsic_len_px`). The flex/inline/block paths were never wrong — only a grid item's box.

Real-page reach: any card/tile/nav grid whose items set their own font-size and pad in rem (the Tailwind/utility idiom: `p-3 text-sm`) was short by 2·rem·(16 − font) on both axes, and the whole column under each row drifted by it.

## Bug 2 — flex.rs steps 11d and 11b: the un-collapsed sum

`.container` is a column flex item (body is `flex-direction: column`). Step 11 lays its children out with sibling margin collapse (n42/#184 put that in), so the search box's `margin-bottom: 2rem` and the section's `margin-top: 3rem` collapse to 48 and the section lands at Chrome's y. Step 11d then re-derived the item's main size as `Σ children.margin_box().height` — which charges 32 + 48 = 80 for that seam — so the item measured 746 for its flowed 714 (Chrome 733; the last px is #201's 51 vs 52 input), and the 32 landed as empty space under the last child, pushing body's centring 6.5px off. Step 11b (row containers, cross axis) had the identical sum. Both now read the flowed extent (`content.height`).

One consequence handled: a flex item is a formatting-context root, so its last in-flow child's bottom margin stays INSIDE it. The collapse pass leaves that margin pending when nothing on the item's own box blocks the collapse (its style cannot tell it is a flex item), and the old sum had included it by accident. Step 11 now materializes the pending margin into the item after the pass. Test `a_block_item_keeps_its_last_childs_bottom_margin_inside` pins it (item = 20 + 16 = 36, Chrome 36).

Aleph note: the index's body for `layout_flex_container` step 11 still showed the pre-#184 non-collapse call. The file is the truth (memory: aleph-index-lags-develop-verify-bodies).

## Receipts

- Reduced repro `parity-tests/repro/flex-row-cross-3px-short.html` vs pinned Chrome 148 (`scratch_n52/chrome_repro/layout-rects.json`): A (rem grid rows) 60 / 50 = Chrome on every row, first key x 17 = Chrome; C (column item with a collapsed seam) **122 = Chrome 122** (was 152 — the unit test's T-RED figure); D (bare item, last-child margin) **36 = Chrome 36**. A's row TRACK is still 143 on develop (n51's #201 lane; 60 on the stack below).
- Tests: rustkit-layout 372 → 375 (`a_grid_items_rem_padding_resolves_against_the_root_font_size`, `a_block_item_measures_its_collapsed_seams_not_the_margin_sum` — 152 for 120 on develop — and the BFC-root pin above).
- **Board on develop `da8f413` + this branch (`f4c6a65`)**: campaign 26/26, **avg 2.6245 → 2.6249** — new_tab 2.5924 → 2.6042 (+0.012: the rows are Chrome's height but still sit on #201's 143px tracks, so the taller rows push the 832px grid 18px further), settings 3.5404 → 3.5389 (−0.0015: its flex-item columns lose the same phantom seams), 24 of 26 byte-flat. **WPT Tier-1 24/26 flat**, pinned on f4c6a65 (`scratch_n52/board_fix.json`, `wpt_fix.log`).
- **Stacked on #201** (local `atlas/n52-stack-201`, not pushed): **new_tab 2.6459 → 1.9261** (−0.72pp; 2.5924 on the develop basis → 1.93), settings 3.5378 → 3.5361, campaign **avg 2.6265 → 2.5987**, 24/26 byte-flat (`scratch_n52/board_stack.json`). Layout on the stack (Chrome | RustKit): `.container` 33.5/733 | 34/732; logo 65.5 | 66; tagline 129.5 | 130; `#searchInput` 193.5/52 | 196/51; `.shortcuts` 334.5/400 | 334/400; first kbd row 352.5 | 352; `.shortcut` 60/60/50 = Chrome on every row, first key x 389 = Chrome. new_tab's re-table is closed: nothing on the page is more than 2.5px from Chrome.

## Ledger (not chased)

- `.footer` x = 0 for Chrome's 571: the static position of an abspos/fixed child of a flex container is computed as if it were the sole flex item (css-flexbox-1 §4.1) — `align-items: center` should centre it. Every "fixed footer/badge in a centred flex body" idiom.
- `#searchInput` 51 for 52: n51's form-control composition is 1px short (probably the control's inner line 19 vs Chrome's 20 at 16px).
- The painter's form-control padding closure (`lib.rs` ~6349) still resolves px/em only — the text seat inside a rem-padded input paints at the wrong inset while the box is right since #201. Same shape as tonight's grid bug; one-line follow-up.
- grid.rs resolves a percentage vertical padding against the area HEIGHT; CSS resolves all four padding percentages against the containing block's inline size. No board case has percentage padding on a grid item.
- Each `.shortcut`'s `::before` (abspos, `width: 3px`) is laid out at a stale y (n51's "3×18.8 box"); it paints nothing at rest (`scaleY(0)`).
- `null_remember` abandoned at the 60s budget again (`null doctor`).

## Operational

Three release builds (fix 9m19s, fmt re-pin 9m50s, stack ~10m — the last one crossed the 600s foreground cap and went to the background; polled it, did not end the turn), two boards, one WPT run, all in-turn. Aleph found `calculate_cross_sizes` / `get_content_cross_size` / `MarginCollapseContext` first try; its `layout_flex_container` body was stale. The hook refused `grep` over the tree, `awk`, `&&`-chained `ls`, and any heredoc containing a brace-quote pair (scripts went to files instead). Scratch in `hiwave-macos/scratch_n52/`.
