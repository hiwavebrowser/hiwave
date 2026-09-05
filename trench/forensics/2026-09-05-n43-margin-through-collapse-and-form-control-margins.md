# n43 — a parent's open edges never collapsed margins with its children; form controls dropped their author margins

Night 43 (2026-09-05, macOS seat). Lane: css-selectors 11.20 (the n42 digest's option (b): #174/#173 still unmerged at lane start, develop still `5b89ed8`, so the currentColor lane stayed conditional and the biggest unclaimed board case was taken from develop tip).

## What the table said
`scratch_n43/ytable.py websuite css-selectors` on the develop basis: 43 mismatched elements, first divergence `div.section:1 > div.test-child:2 > div.direct-child:1` dy +4 at Chrome y 66. Reading the subtree dump (`scratch_n43/dump.py … --tree`):

| element | Chrome y/h | RustKit y/h | term |
|---|---|---|---|
| `.direct-child:1` (mt 4) after `.section-title` (mb 10) inside unpadded `.test-child` | 66 / 33 | 70 / 33 | first-child top margin not collapsed through the wrapper: 10 + 4 instead of max(10, 4) |
| `.wrapper` > `.nested-child` (mt 4) | 103 / 33 | 111 / 33 | +4 more: the chain wrapper→wrapper→child |
| `.test-child` height | 107 | 115 | +8 inside; the LAST child's mb 4 dropped instead of adjoining the section's content (Chrome's section is 172 = 15+21+10+107+4+15; RustKit 176 = …+115+0+15) |
| §4 `div > input{margin:4px 0}` row | 43 | 37.5 | control margins never resolved: row = bare 34.3 + strut 3.2 |
| §4 `input[type=checkbox]` + `label` row | 23 | 20 | checkbox baseline should be its bottom edge (strut hangs 3 below), label text drops to it |
| §6 `.buttons` row (`button{margin:4px}`) | 39 | 33.5 | same missing margins |

Every section after §1 rode on the +4; §4's −8.5 (two control rows) then flipped the sign, ending at −9.9 by §7 — "a handful of ±4px block-flow terms" was really three bugs.

## Root causes (rustkit-layout `lib.rs`)
1. **No parent/child through-collapse, by design.** `layout_block_with_collapse` positioned itself from the parent's context, then gave its children a FRESH `MarginCollapseContext` — the comment said outright that CSS 2.1 §8.3.1 through-collapse "is not performed". At the bottom, `layout_block_children_with_collapse` materialized the last child's pending margin only when the edge was closed and dropped it otherwise ("ledgered as a smaller residual"). `should_collapse_with_first_child` existed in `margin_collapse.rs` with zero callers (Aleph: `f_1611d0 has no callers`) — same shape as n41's dead auto-fit code.
2. **`layout_form_control` never resolved `margin-*`.** The control's rect was its whole margin box; `button{margin:4px}` contributed nothing to the line.
3. **`baseline_is_bottom_edge` used the bottom-edge model for author-padded controls** because it "measured closer to Chrome" (line 39 vs 30.3) — a calibration made while (2) was true. With margins present, bottom-edge overshoots (41.5 = margin box + strut descent); the hang model builds Chrome's 39. Checkbox/radio have no inner text line: bottom-edge is right for them (Blink).

## Fix (PR #185, `atlas/n43-css-selectors-block-flow` @ 00950d4)
- `MarginCollapseContext` gains three flags: `children_are_formatting_roots` (set by flex/grid containers and by the engine for the root element), `first_child_top_adjoined`, `last_child_collapses_through`.
- Top edge: `first_child_top_margin_chain()` walks first in-flow block children while each edge is open (no border/padding-top via `should_collapse_with_first_child`, not a BFC, no inline-level/float/abspos first child) and returns their top margins; the box adjoins its own margin + the chain into the parent's context before positioning. The first child sees the flag and skips its own top margin.
- Bottom edge: when `should_collapse_with_last_child` holds and the box is not a formatting root, the child context keeps the last child's margin pending and the parent `absorb()`s it next to its own bottom margin. Closed edges AND formatting roots (flex/grid items, root) now materialize it INSIDE the box — flex/grid item re-layouts used to drop it.
- Engine: root context `children_are_formatting_roots = true` (the root element's margins never collapse with body's; body + h1 collapse under html's edge — Chrome's body.top = 21.44 on a bare page).
- Form controls resolve their four margins from style; text-line controls use the hang baseline model, checkbox/radio the bottom edge.

## Receipts
- Tests: rustkit-layout 308 → 315 (7 new, names in the commit), rustkit-engine 69/69. T-RED is the board's own numbers in the assertions (34 = summed, 32 = dropped).
- Repro `parity-tests/repro/margin-through-collapse.html` vs pinned Chrome 148 (`scratch_n43/chrome-repro`, `repro_table.py`): sections A–D (chain, padded negative control, flex item, ul) match to 0.0px on all 25 elements; E (controls) within 0.7px except the label text next to the checkbox (−6.4, ledger).
- Campaign board (n39 basis `scratch_n39/board_develop_basis.json`, develop `5b89ed8`, avg 4.0404) → `scratch_n43/board_with_fix2.json` **avg 3.6746**: css-selectors 11.2043 → 2.6694 (−8.53pp), combinators 2.4780 → 1.9466 (−0.53), form-elements 3.8742 → 3.4294 (−0.44), new_tab −0.002, form-controls +0.001; 21 of 26 byte-flat. css-selectors geometry: 43 mismatches → 1 (the label).
- WPT Tier-1: 24/26 flat (`scratch_n43/wpt_with_fix2.json`), same two fails.
- Measurement note: `scripts/parity_test.py` builds parity-capture itself; the run intended as the basis was already the fixed binary (mtime told). Basis = n39's committed develop file on the same sha; about/flex-positioning/article-typography reproduce it byte-for-byte.

## Ledger (not chased)
- Label text next to a bottom-edge checkbox does not drop to the baseline (`apply_vertical_align`, Slice C): css-selectors' last geometry mismatch (−6.4).
- Percent margins in the through-chain resolve against the top box's content width.
- Out-of-flow children are laid out against the parent's live margin context (pre-existing: an abspos first child with margins pollutes the seam).
- Control heights 30.33/34.33 vs Chrome 31/35 (line-height rounding in the composed-height contract).
