Title: fix(layout): author width/height on text inputs and textareas sizes the content box (CH2.B17)
Branch: atlas/z-ch2-b17-control-content-box @ bd881e52 (red 2af0ffab), base develop 232fca86
PR: pending the open-PR cap (16 open at 19:27 ET after #931/#932); open as a draft with this body when a slot frees.

---

## What

Chrome's UA sheet leaves text inputs and textareas at `box-sizing: content-box`. An author `width`/`height` therefore sizes the content box, and the border box adds padding and border: `width: 40px` gives an input 48 px and a textarea 46 px (Reduce, 11-05). RustKit folds a control's UA padding and border into its border box and used the author size as that border box, so it built 40.

`LayoutBox::content_box_control_extra` returns the padding + border a content-box text control adds. Per side it takes the author's value; a side the author left unset (`Length::Zero`) takes the UA value (text input `1px 2px` + `2px`, textarea `2px` + `1px`); `border-style: none` means no border. `type=search` is border-box in Chrome's UA, and every other control type is unchanged. The extra applies to px/%/em author sizes in block flow (`layout_form_control`) and to a flex item's specified size (`spec_main_to_border_box` / `spec_cross_to_border_box`).

Known limit, shared with the intrinsic-height code: a bare `padding: 0` reads as unset on develop until #921 lands (it makes `0` → `Px(0)`). Until then an input with a reset `padding: 0` and an author width still gains the UA 4 px of horizontal padding. `0px` is right today.

## Red → green (rustkit-engine, headless, Chromium 143 pins)

`form_control_author_size_tests` runs 10 pages from `tools/parity_oracle/form_control_author_size_cases.json` (`grid_flexible_row_log.mjs --file … --write`, `id:x:y:w:h`):
- author size (input 48×26, textarea 46×26)
- author padding + border (52×32 for both)
- `padding:0px; border:0px` (40×20)
- `border:none` (44×22)
- border-box input and textarea (40×20)
- seven input types (text/password/email/url/tel/number 48×26, search 40×20)
- a flex row of input + textarea + a box (x 0/48/94)

7 wrong at 2af0ffab, 0 at bd881e52. One case changed between the two commits: the last page was an inline input plus a `vertical-align: top` neighbour. That neighbour's y is a separate gap (8 vs 0, and on develop too), so the page is now the flex row, which also caught that flex had its own sizing path.

Two layout unit fixtures were brought in line with their own doc comments. `percent_height_definite_tests::input` says `border: none; padding: 0` but left both unset, so it now sets them. `flex::tests::a_control_with_a_pixel_width_is_still_measured` gets `box-sizing: border-box`, so its 200 still means a 200 border box.

## Tests (targeted; the full suite is the batch's)

- rustkit-layout --lib 896/0 (13 ignored)
- rustkit-engine --lib 709/0 (filter-free)
- headless `form` 145/0 (3 ignored), `input` 17/0

## Campaign / board (--profile parity; develop 232fca86 sha256 78895e57…, branch bd881e52 sha256 03e92ce4…)

- 26-case campaign: 26/26 on both arms, 0 cases moved.
- Chrome board: 42 rows, 0 moved (10/42 green, geometry 5470 on both).

The campaign and chrome pages don't put a content-box author width on a text control. The change shows on the pinned pages and on any live site that sizes an unstyled input. Not run: the all-site A/B (layout change; the batch's).

Toolchain rustc 1.91.0 (f8297e351 2025-10-28), aarch64-apple-darwin, macOS 26.5.2 arm64, z-cargo lease + sccache. Oracle: Chromium 143.0.7499.4 (Playwright, DPR 1).

Needs R1 (Prometheus), then a batch; land after #921.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
