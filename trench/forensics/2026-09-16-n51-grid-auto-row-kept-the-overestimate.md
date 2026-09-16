# n51 — a grid `auto` row kept track sizing's over-estimate (rustkit-layout)

**Date:** 2026-09-16 (night block 51, macOS seat). **Lane:** n50 option (a), "new_tab / about re-table on the merged set", by the standing rule (no Pete answer on the exchange). Nothing had merged since n50 — develop is still `da8f413`, PRs #193–#200 all open — so the "merged set" is a local stack of the eight PRs' code commits (`atlas/n51-stack`, not pushed).

## The stack, first

Cherry-picking the eight code commits onto develop in PR order hits **two real conflicts** that the per-PR `MERGEABLE` flag hides:

| pair | file | shape | resolution |
|---|---|---|---|
| #195 → #196 | `crates/rustkit-layout/src/flex.rs` | both append after `layout_block_children_with_collapse` in the item loop: #196 restores the definite cross height, #195 re-anchors abspos children | keep both, height restore first, then `reanchor_absolute_children()` (the anchor must see the final size) |
| #199 → #200 | `crates/rustkit-layout/src/lib.rs` | #199 rewrote `text_splits_inline` (drop the `cursor_x > 0` gate) where #200 inserted `inline_wrapped_tail` above the old signature | keep #200's helper and #199's gate-free `text_splits_inline` |

Whichever of each pair merges second needs a rebase. All 396 rustkit-layout tests pass on the resolved stack.

**Stacked board (develop basis `da8f413` → the eight PRs):** 26/26, avg **2.6245 → 2.5416**, 20/26 byte-flat. about 5.2462 → 5.2338, article-typography 7.4646 → **5.4559** (#199 and #200 compose: 6.74 and 6.18 alone), css-selectors 2.6694 → 2.6689, settings 3.5404 → 3.5327, sticky-scroll 2.0387 → **1.8569** (new — #193's nowrap min-content or #196's flex cross size; not attributed tonight), new_tab 2.5924 → 2.6490 (n50's honest +0.06, the bolder kbd ink at the wrong y). Board banked in `hiwave-macos/scratch_n51/board_stack.json`.

## The residual: new_tab's kbd rows were 63px high

The n50 ledger line. Not the kbd rows at all — three nested offsets, all above them:

1. **`.shortcuts` grid: 832px tall for Chrome's 400.** Row pitch 152 (RustKit) vs 72 (Chrome), for `.shortcut` items that lay out 57–60px tall in BOTH engines. The row track was **143px**.
2. `.container` therefore 1164px tall (Chrome 733) — taller than the 800px viewport, so body's `justify-content: center` put it at y 0 instead of Chrome's 33.5.
3. `#searchInput` is 19px tall (Chrome 52): the form control ignores its `padding: 1rem 1.5rem`. Separate bug, not touched tonight.

The 143 decodes exactly: `GridItem::count_text_lines` charges one line-height per text **node** and `.shortcut` holds seven (`ws`, `Ctrl`, `/`, `Cmd`, `+`, `K`, ` `, plus the span's) on ONE flex line — 7 × 16.8 (14px × normal) = 117.6, + 24 padding = 141.6, + 2 border. Track sizing sized every row to it. Phase 9.5 (`grid.rs`, "grow AUTO rows to the items' REAL content heights") re-measures after the items lay out — but it was **grow-only**: an over-estimate was never corrected. The same estimator under-shoots on wrapped text (that is why 9.5 exists) and over-shoots on any inline-heavy row; only the under-shoot had a repair.

Reduced repro `parity-tests/repro/grid-flex-kbd-rows.html` (A: the new_tab grid verbatim; B: one flex row alone; C: text-only flex row; D: block row with the same kbd children) — on develop only A is wrong (`#a` 298px for Chrome's 132, rows 3–4 at y 179 for Chrome's 96); B/C/D are pixel-right, which localises it to grid row sizing.

## Fix (rustkit-layout `grid.rs`, Phase 9.5)

- Per row, collect the tallest single-row item's real **margin box** (`row_real`) — the figure the grow path already computed — and whether the row may shrink (`row_shrinkable`): the track is intrinsic (`is_min_content && is_max_content`, i.e. `auto` / minmax(min-content, max-content)), not flexible, not percentage, not fit-content; no multi-row item spans it; every item in it reported a real height (a childless item's real content is 0, an explicit `height: Npx` is its own answer, `min-height: Npx` floors it; a percentage height or min-height marks the row not shrinkable).
- `row_delta` = `real − size` when it grows by > 0.5, or shrinks by > 0.5 on a shrinkable row; otherwise 0. The existing reposition (translate later rows' subtrees, recompute the container's auto height) runs for any non-zero delta.
- Stretch: an auto-height item in a **shrunk** row gives back the stale area height (the block path hands items the pre-pass area; a flex-container item already re-derived its own). Grown rows keep the old grow-only stretch.
- `minmax(100px, auto)` is `(false, false)` on the intrinsic flags and keeps grow-only — right by accident of representation (the track does not remember its definite floor once the contribution loop grew `base_size`); pinned by a test so a future "make minmax shrink" has to solve the floor first.

Two tests (`an_auto_row_shrinks_to_its_items_real_height` — T-RED on the grow-only pass: row 2 lands at the three-line pitch; `a_minmax_row_with_a_definite_floor_does_not_shrink`). rustkit-layout 372 → 374.

## Receipts

- Repro vs pinned Chrome 148 (`vs_chrome.py`, >16 in any channel): **83,608 → 12,694** differing px; `#a` 298 → 132 = Chrome, every `.shortcut` rect = Chrome's (y 24/24/96/96, h 60), sections B/C/D move up to Chrome's y (180/264/331).
- new_tab vs Chrome baseline: **188,291 → 117,472** differing px. Layout: `.container` 1164 → 714 (Chrome 733) at y 0 → 43 (Chrome 33.5); `.shortcuts` 832 → 382 (Chrome 400); first kbd row y 284.5 → 327.5 (Chrome 352.5). The remaining 25px is item 3 above (the input's padding) less the centring it causes.
- Board (grid fix alone, `6826b0c`): new_tab 2.5924 → **2.7979**, everything else byte-flat, avg 2.6324. Honest read: the meter is pixelmatch, and a row offset by 23px costs twice its edge area while the old 832px grid left dark regions that matched Chrome's dark background — a near-miss reads worse than an absence. The y-table above is the layout receipt.

## Second fix, same night: the input's `rem` padding

With the grid right, the y-table's remaining 25px was `#searchInput` at 19px for Chrome's 52. `layout_form_control`'s unit closure resolved `Px` and `Em` only, so `padding: 1rem 1.5rem` (the idiom on every styled search box) read as no author padding and the control fell to the bare-control 19px blob instead of composing content line + padding + border. Both closures (vertical → height, horizontal → button width) now go through `Length::to_px` against the 16px root; percent/auto stay 0. One test (`a_text_input_with_rem_padding_composes_it_into_its_height`). rustkit-layout 374 → 375. Commit `10f3064`.

**Final y-table (Chrome | RustKit):** `.container` 33.5/733 | 27/746; logo 65.5 | 59; tagline 129.5 | 123; `#searchInput` 193.5/52 | 189/51; `.shortcuts` 334.5/400 | 327/382; first kbd row 352.5 | 343.5; `.shortcut` 60 | 57 on every row. Everything is inside 10px of Chrome; the two remaining terms are the 3px-per-row `.shortcut` height (57 vs 60 — the two-line label's line boxes under `align-items: center`) and 32px extra below the section inside `.container` (746 vs 733 net of the shorter grid; the footer text sits in flow at the container's bottom where Chrome's does not). 

**Final board (`10f3064`):** 26/26, avg 2.6245 → **2.6265**, new_tab 2.5924 → **2.6459**, settings 3.5404 → **3.5378** (the input fix: settings' inputs carry rem padding too), 24/26 byte-flat. WPT Tier-1 24/26 flat, pinned on 10f3064. new_tab differing px vs Chrome (>16 sensor): 188,291 → 117,472 → 130,520 — the page is now uniformly ~7–9px high rather than 33–66px, and the pixel sensors will not reward it until the last two terms close.

## Ledger (not chased)

- `.shortcut` 57 vs Chrome 60: the flex row's cross size under a 34px two-line label + 24px chips reads 3px short (line-box height of the wrapped span under `align-items: center`). 3px × 7 rows is the whole remaining kbd offset.
- `.container` 746 vs 733: +32 below `.shortcuts-section` — the footer paragraph (`HiWave v0.1.0 - Settings`) is laid out in the container's flow; check its Chrome position (fixed/absolute?) before touching flow.
- form-controls 5.02 / form-elements 3.43 did NOT move on the input fix (byte-flat): their controls are px/em-padded or bare.
- The leading whitespace text node of each `.shortcut` gets a 3×18.8 box at a stale position (x 389, y stepping 50 per item, outside its parent); it paints nothing, but the flex row positions its anonymous whitespace child with a running cursor. Cosmetic in the dump.
- Rows with `align-self: end/center` items are translated by the row delta but not re-aligned inside the new row (same limitation as the grow path).
- `.shortcut` items read 57 where Chrome has 60 (a 3px line-box/align-items term on the two-line span), and the flex item with a one-line label is 47 on develop, 57 stretched after — Chrome stretches to 60.
- The estimator itself (`count_text_lines`) is still wrong; Phase 9.5 now corrects it in both directions, which is the spec's answer (an `auto` track IS the items' size), so the estimator only matters for what it feeds before layout (nothing on the board moved but new_tab).
