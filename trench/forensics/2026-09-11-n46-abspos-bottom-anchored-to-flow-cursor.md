# n46 — an abspos child's `bottom:` anchored to the parent's flow cursor, not its final padding box

Night block 46, 2026-09-11. Lane: the n45 digest's option (a), taken by the standing rule (no Pete answer; the exchange carried only Argos gauge snapshots). Basis: develop `da8f413` (unchanged since n45; #193 and #194 still open), fresh clean-tree parity-capture, campaign 26/26 avg **2.6245** reproduced exactly, WPT Tier-1 24/26.

## What was wrong

`rustkit-layout` lays an absolutely positioned child out inside the parent's child loop against a STAND-IN containing block: a clone of the parent's dimensions with `content.height = cursor_y`. That is the static-position trick (a block positions itself at `cb.y + cb.height`), but `apply_position_offsets_absolute` also reads `containing_block.content.bottom()` to resolve `bottom:` and the `top+bottom` inset stretch — so `bottom:` measured "content laid out so far", and for a first/only child that is the parent's TOP.

The existing repair (`reanchor_absolute`, WPT overflow-wrap-anywhere-001 lane) ran inside the same loop, only when the parent's `height` was an absolute length (`definite_content_height`), and against the CONTENT box. Three shapes fell through:

1. **Parent sized by its own `inset: 0` stretch** — the settings toggle: `.toggle-slider { position:absolute; inset:0 }` gets its height in its OWN `apply_position_offsets`, which runs after its children laid out. The knob `::before { bottom: 2px; height: 20px }` was anchored to a 0px-tall stand-in: knob y 289.19 for a slider at 310.19 (the n45 revealed bug). Same for any `inset:0` overlay holding a bottom-anchored child (`.f .fill > .knob` in the repro).
2. **Auto-height positioned parent** — no definite height, no re-anchor; a `bottom:` child that precedes its siblings anchors to y=0 of the parent.
3. **Padded parent** — CSS 2.1 §10.1 says the containing block is the padding box; the re-anchor used the content box, so `bottom: 4px` in a `padding: 8px 0` parent sat 8px high.

## The fix (rustkit-layout only, PR to develop)

- `reanchor_absolute_children(&mut self)`: after a box's own `apply_position_offsets` in BOTH layout paths (`layout_with_collapse`, `layout_with_definite_height`), every abspos child is re-resolved against `abspos_containing_block()` = the parent's padding box expressed as a `Dimensions`. flex.rs calls it after re-laying out an item's block children and after a nested flex container's abspos pass (the item's flexed size is final there).
- `reanchor_absolute` now re-anchors its own abspos children when its SIZE changed (an inset stretch) — this is the chain that fixes shape 1: toggle → slider (stretched to 26) → knob.
- The in-loop re-anchor and `definite_content_height` are removed; the existing overflow-wrap-anywhere-001 test (`abspos_inset_fills_parents_definite_height_not_its_flow_cursor`) still passes through the new pass. Two new tests: the toggle idiom (knob 3px from the slider's top-left, Chrome's 25 − 2 − 20) and the padded auto-height parent (bottom/right against the padding box). rustkit-layout 372 → 374.

## Receipts

`parity-tests/repro/abspos-bottom-right.html`, 400×480, six sections, pinned Chrome 148 via `scratch_n36/chrome_capture.py`:

| section | Chrome knob y | develop | branch |
|---|---|---|---|
| A bottom in a definite-height relative | 46 | 46 | 46 |
| B right in a relative | 84 (x 366) | 84 | 84 |
| C toggle idiom, real knob | 170 | **146** | 170 |
| D toggle idiom, `::before` knob | 240 | **216** | 240 |
| E bottom in an auto-height padded relative | 330 | **322** | 330 |
| F bottom+right in an `inset:0` parent | 400 | **340** | 400 |

settings capture (fix only, develop matcher): the knob box moves 289.19 → 313.19 for the slider at 310.19–336.19 (Chrome 313.19). The board reads settings byte-flat because on develop the `input:checked + .toggle-slider::before` rule does not match (#194's lane), so the unchecked knob paints the same gray as the slider background… the stacked-#194 board (below) is the honest test of the settings term.

## The about regression is a revealed renderer bug

Campaign avg 2.6245 → **2.6832**: 25 of 26 byte-flat, about 5.2462 → **6.7731** (+1.53pp). about's layout dump is identical before/after (343 boxes, 0 changed — `scratch_n46/layoutdiff.py`); the pixel delta (`framediff.py`: 78k px, rows 240–319 dominate) is `.sponsor-btn::before { position:absolute; inset:0; transform: translateX(-100%) }`. Before the fix the pseudo box was 0px tall (inset stretch against a 0px stand-in) and painted nothing; now it is the button's size, as in Chrome — and Chrome hides it because `.sponsor-btn { overflow: hidden }` clips the translated box. RustKit paints it as a 230×50 shine bar to the LEFT of the button: `rustkit-renderer` clips in pre-transform document space (`draw_clipped_quad` collects clip pieces from the untransformed rect, then `push_color_quad` transforms the surviving pieces), so a transformed descendant is clipped against where it would be WITHOUT the transform. The same shape hits `.hero::before { top:50%; left:50%; transform: translate(-50%,-50%) }` (glow blob, rows 160–199 +1k px) and every "shine sweep" / "slide-in" idiom on real pages. Fix belongs in the renderer (clip in screen space, or transform the clip rect for axis-aligned transforms); not tonight.

## Ledgered, not chased

- Renderer clip-vs-transform order (above) — the named next lane; it closes about's +1.53 and is a real-page idiom.
- Abspos containing block is still "the parent" — a static (non-positioned) parent between a positioned ancestor and the abspos child is still used as the CB (pre-existing; the paint-side `escapable_clips` logic already models the real CB, layout does not).
- grid.rs re-lays out a grandchild's block children on width change without a re-anchor pass (`layout_block_children_with_collapse` at grid.rs:2136); no board case exercises it.
- `cargo fmt` / `rustfmt` are not on this seat's allowlist — the new code is hand-formatted in rustfmt style; a reviewer's `cargo fmt --check` on the crate is already red for unrelated regions (n40 memory).
