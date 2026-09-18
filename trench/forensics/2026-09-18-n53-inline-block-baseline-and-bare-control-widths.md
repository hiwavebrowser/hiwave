# n53 — inline-block baseline, textarea bottom edge, button-type inputs, bare control widths (2026-09-18)

Seat: macOS (Atlas). Basis: develop `9272261` (#193–#202 all merged 2026-09-17;
first fresh clean-tree board tonight: campaign 26/26 **avg 2.5146**, WPT 24/26).
Lane: n52 option (a), form-controls 5.02 — the biggest unclaimed case with no
ledger line.

## Y-table first (scratch_n53/ytable.py)
RustKit vs Chrome, form-controls @ 800x1200, visible region:
- every `label { display: inline-block; width: 120px; font-size: 12px }` sat at the
  row TOP (dy −5/−6 on 12 rows); the wrapped "Checkbox 2 (checked)" label put
  its siblings at +0/+5 where Chrome hangs them at +18 off its second line.
- bare text inputs 160 wide (Chrome 149); `<input type=submit|reset>` 160 wide
  (Chrome 45.5 / 38.8) — typed as TextInput by the engine.
- textarea container 56 tall (Chrome 62): no strut descent under the textarea;
  every section below slid −6 (→ −10 by test 9). Band diff: rows 960–1200 held
  19.4k of the page's 50.5k differing px.
- select multiple 133 wide (Chrome 39); dropdown 133 (Chrome 137).

## Bugs
1. **`apply_vertical_align` skipped every inline-block that had children**
   ("non-atomic inline boxes stay top-aligned (later slice)"). CSS2 §10.8.1:
   an inline-block's baseline is its last in-flow line box's baseline; bottom
   margin edge when it has none or its `overflow` is not visible. New
   `inline_block_baseline_y()` walks the last in-flow descendant that carries a
   baseline (text: run bottom − (half-leading + descent) of one line; control:
   hang model; image: bottom); both passes of the align use it.
   - Overflow clause is inline-block ONLY: Blink's
     `ShouldIgnoreOverflowPropertyForInlineBlockBaseline` exempts flex/grid
     containers. First build applied it to inline-flex too and about's
     `a.sponsor-btn { display: inline-flex; overflow: hidden }` hung a strut
     descent under itself: about 5.2338 → 6.1796 (+0.95), whole page below
     +3.375. Narrowed; about byte-flat on build 2.
2. **Textarea baseline = bottom edge** (scroll container). Was the hang model
   (synthetic inner-text baseline), so the line never grew past the box.
3. **Engine: `<input type=submit|reset|button>` → `FormControlType::Button`**
   with the HTML default labels ("Submit"/"Reset"). Was TextInput.
4. **Bare widths at the UA control font** (ua_scale = font/13.333): text input
   149 (was 12em = 160); textarea `0.6em × cols + 18` (border + scrollbar
   gutter; 178 / 338 = Chrome); select = widest option + 2 (listbox) / + 24
   (dropdown, arrow well).
5. **Engine UA arm: control font-family `Arial`, not `system-ui`.** The pinned
   CfT-148 computes `font-family: Arial` for every unstyled control on every
   board case (census over baselines/chrome-148 computed-styles), and its label
   widths are Arial to the tenth ("Submit" 41.5). SF measured 5–8% wide (the
   dropdown "A longer option text" 146 vs 137).

## Receipts
- rustkit-layout 402 → 406 tests (`inline_block_with_text_sits_on_its_last_line_baseline`,
  `wrapped_inline_block_hangs_the_line_off_its_last_line`,
  `textarea_alone_on_a_line_hangs_the_strut_descent_below_it`,
  `bare_control_widths_match_chrome`).
- form-controls y-table after: every visible box within 1.5px of Chrome except
  the five bare buttons (+20 wide each) and the listbox row (−3, see below);
  label rows at Chrome's +5, checkbox row at +18/+18/+0, textarea containers
  62/107 = Chrome, body 1718.9 vs 1716.
- Repro `parity-tests/repro/inline-block-baseline-and-control-widths.html` vs
  pinned Chrome 148 (scratch_n53/chrome_repro): section B (checkboxes + wrapped
  label) all four members at Chrome's offsets; C textarea containers 62/107 =
  Chrome; D submit/reset/plain now buttons; E pill/tall/clipped spans at
  Chrome's +16/+3/+0 within 0.4px.
- about below the fold: card 8's `<kbd>` paragraphs moved from 1917.8 to
  1875.8 = Chrome's 1875.7 (42px; invisible to the 600px meter).

## Ledgered, not chased
- **Line box height ignores the strut when no text child carries it.**
  `layout_block_children` advances by max(child height, bottom-edge hang);
  the align pass runs after. `<label>Text:</label><input>` with no whitespace
  builds a 19px row (Chrome 24); the listbox row 50 (Chrome 53); a pill + 24px
  span + clipped span line 60 (Chrome 63). Next lane: `max_above + max_below`
  with the strut on both sides — every inline-block-only row on the board
  will move; measure first.
- **Bare button width +20**: the +24 blob assumes UA padding 6+6 + border 2+2
  + 8; under the parity reset Chrome has border only (+4); a bare page has
  +16. Neither is reachable while UA padding/border are not in the cascade
  (the reset's `* { padding: 0 }` is indistinguishable from unset). Decision:
  put control UA padding/border in the engine arm and let layout compose
  always (the bare-19 calibration path then dies).
- inline-flex baseline should be the FIRST item's (css-flexbox §8.5); the
  helper walks last-to-first. Same row on every case tonight; flag for a
  multi-line flex button.
- Text seat of a rem-padded input, `.footer` static position (n52 lines).
