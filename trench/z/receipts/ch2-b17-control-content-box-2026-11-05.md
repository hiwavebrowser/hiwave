fix(layout): author width/height on text inputs and textareas sizes the content box (CH2.B17)
Branch: atlas/z-ch2-b17-control-content-box @ c07e2d03 (red 2af0ffab, fix bd881e52, develop 70cd68c5 merged at 6361e11e, pins c07e2d03)

---

## What

Chrome's UA sheet leaves text inputs and textareas at `box-sizing: content-box`. An author `width`/`height` therefore sizes the content box, and the border box adds padding and border: `width: 40px` gives an input 48 px and a textarea 46 px (Reduce, 11-05). RustKit folds a control's UA padding and border into its border box and used the author size as that border box, so it built 40.

`LayoutBox::content_box_control_extra` returns the padding + border a content-box text control adds. Per side it takes the author's value; a side the author left unset (`Length::Zero`) takes the UA value (text input `1px 2px` + `2px`, textarea `2px` + `1px`); `border-style: none` means no border. `type=search` is border-box in Chrome's UA, and every other control type is unchanged. The extra applies to px/%/em author sizes in block flow (`layout_form_control`) and to a flex item's specified size (`spec_main_to_border_box` / `spec_cross_to_border_box`).

With #921 on develop (merged in at 6361e11e) a bare `padding: 0` is an author zero, so the earlier known limit is gone; a pin covers it. The merge also met #924's new `vw`/`rem`/`calc()` arm in `layout_form_control`: those author sizes now gain the content-box extra too (pinned with `10vw`×`5vh` = 48×36 in Chromium), and the extra's percentage base follows #924's viewport base for a fixed control.

## Red → green (rustkit-engine, headless, Chromium 143 pins)

`form_control_author_size_tests` runs 12 pages from `tools/parity_oracle/form_control_author_size_cases.json` (`grid_flexible_row_log.mjs --file … --write`, `id:x:y:w:h`):
- author size (input 48×26, textarea 46×26)
- author padding + border (52×32 for both)
- `padding:0px; border:0px` (40×20), and bare `padding:0; border:0` (40×20, added at c07e2d03)
- `width:10vw; height:5vh` (48×36, added at c07e2d03)
- `border:none` (44×22)
- border-box input and textarea (40×20)
- seven input types (text/password/email/url/tel/number 48×26, search 40×20)
- a flex row of input + textarea + a box (x 0/48/94)

7 wrong at 2af0ffab, 0 at bd881e52. One case changed between the two commits: the last page was an inline input plus a `vertical-align: top` neighbour. That neighbour's y is a separate gap (8 vs 0, and on develop too), so the page is now the flex row, which also caught that flex had its own sizing path.

Two layout unit fixtures were brought in line with their own doc comments. `percent_height_definite_tests::input` says `border: none; padding: 0` but left both unset, so it now sets them. `flex::tests::a_control_with_a_pixel_width_is_still_measured` gets `box-sizing: border-box`, so its 200 still means a 200 border box.

## Tests (targeted; the full suite is the batch's)

At c07e2d03 (after the develop merge):
- `form_control_author_size` 1/0 (12 pages)
- rustkit-layout --lib 896/0 (13 ignored)
- rustkit-engine --lib 722/0 (filter-free)
- headless `form` 147/0 (3 ignored), `input` 29/0

## Campaign / board (--profile parity; develop 70cd68c5 sha256 47241851bff16e5b…, branch c07e2d03 sha256 7c96e284459e0e72…)

- 26-case campaign: 26/26 on both arms, 0 cases moved.
- Chrome board: 42 rows. The only rows that differ are the three `chrome/focus_mode` sizes, which flip between two states on develop itself (the cursor-timer artifact; two develop reruns gave both states, see #935). 0 attributable.
- Before the merge (develop 232fca86 vs bd881e52): campaign 0 moved, board 0 moved.

The campaign and chrome pages don't put a content-box author width on a text control. The change shows on the pinned pages and on any live site that sizes an unstyled input. Not run: the all-site A/B (layout change; the batch's).

Toolchain rustc 1.91.0 (f8297e351 2025-10-28), aarch64-apple-darwin, macOS 26.5.2 arm64, z-cargo lease + sccache. Oracle: Chromium 143.0.7499.4 (Playwright, DPR 1).

Needs R1 (Prometheus), then a batch.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
