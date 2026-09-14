# n49 — article-typography: justify was a no-op, the fit test measured the hanging space, and a paragraph's first long run closed its own last line

Night block 49, 2026-09-14 (macOS seat, Atlas). Lane = n48 digest option (a)
by the standing rule: article-typography 7.46, the biggest unclaimed case.
Basis develop `da8f413` (unchanged since n45). Branch
`atlas/n49-article-typography` @ `592e2bb`, PR #199 to develop,
rustkit-layout only.

## What the y-table and the band diff said

`y_table.py` (Chrome layout-rects vs RustKit layout.json) on the n48 capture:
every element above the 800px fold within 0.3px EXCEPT `p:nth-of-type(3) >
span.highlight` (dy +28.4, dx −392: the span sat at the start of line 4
where Chrome has it mid-line 3). Below the fold, meter-blind: `pre` 65.3px
tall vs Chrome 195.2 (six lines collapsed to one), `.columns` stacked
(column-count unimplemented, p2 at x 260 vs 660), everything after shifted
−115px.

`banddiff.py` on the frame vs the pinned Chrome PNG: 83,317 differing px
(8.1% at >16/channel; the meter's 7.46), spread over EVERY paragraph band at
5–10k per 40 rows, not concentrated at the span. The strips showed why:
every `p` on the page is `text-align: justify` and RustKit painted all of
them start-aligned. `apply_text_align_offset` had
`TextAlign::Justify => 0.0, // Justify would need gap distribution (complex)`.

## Fix 1 — justify (css-text-3 §7.3)

`TextLine` gains `justify_space`: the per-word-separator expansion of a
soft-broken line, set by the parent's `apply_text_align_offset` under
`Justify` for every line of a wrapped run except its last (the block's last
line, or a line that continues into the next sibling). The display list
adds it to each space glyph's advance (the per-char advances path — a line
whose shaping falls back to renderer advances paints natural, none seen on
the repro's ligature section in Georgia). Word separators = U+0020 and
U+00A0.

First pass measured slack against `TextLine::width` and every justified
line came up 4px short of the container (word drift −4px by the line end,
`wordpos.py`). The wrap keeps the collapsible space at the break point in
BOTH the line's text and its width (Georgia 17.6px: 4.4px) — the digest-era
doc comment "whitespace at the break point removed" was false. Slack is now
measured against `TextLine::natural_ink_width` = the trimmed text shaped by
`shape_line_advances` (the function paint uses, letter/word-spacing
applied). After that, every word on every justified line of the repro sits
at Chrome's x to the pixel.

## Fix 2 — the fit test measured the hanging space

The repro's ligature section (300px Georgia) broke "…and the official"
before "official" where Chrome fits it. `find_line_break` shaped the prefix
INCLUDING its break-point space and compared that to the width; §4.1.3 says
collapsible spaces at a line's end hang and are removed before measuring.
Now: the prefix is trimmed for the fit test (break-spaces excepted — its
spaces never hang); a closed line's `width` is its ink width
(`line_ink_width`: run width minus trailing collapsible advances) while the
LAST line keeps its live trailing space for the next sibling's cursor.

The first cut of this skipped a space-only prefix as "nothing to measure"
and WPT went 24 → 22 (overflow-wrap-anywhere-004/005: pre-wrap ` XXXXX` in
5ch must break after the leading space onto a space-only line). A
space-only prefix always fits. Unit test added; WPT back to 24/26.

## Fix 3 — the first long run took the block path

`text_splits_inline` required `cursor_x > 0`. A paragraph's FIRST long run
therefore went down the block path, which closes every line it makes, so the
next inline sibling started a new line under the run: article-typography's
`<span class="highlight">` on line 4 instead of line 3. This is every
`<p>long text… <a>link</a> more text</p>` on every real page. The flow path
(`layout_text_in_flow`) now takes runs at the line start too, wrapping via
the block path's entry (no empty first line for an unbreakable first word).

Revealed by the new unit test: `apply_vertical_align` read a split run's
box top (its FIRST line) as the line top and hoisted the follower to line 1
of a 4-line run — a pre-existing bug for `<b>x</b> long run… more` too.
Members' tops now come from `member_top` (a split run contributes its last
line); a split run whose last line would need to move for a taller follower
stays put (ledgered).

## Receipts

- Repro `parity-tests/repro/text-align-justify.html` vs pinned Chrome 148
  (`scratch_n36/chrome_capture.py`): sections A–D 60,652 → 48,064 differing
  px; the left-aligned control paragraph reads 1.1 differing px per Chrome
  ink px with word positions exact — that ratio is the text-AA floor on this
  seat and bounds what any layout fix can recover on this case.
- Board: campaign 26/26, avg 2.6245 → **2.5965**, article-typography 7.4646
  → **6.7360**, 25/26 byte-flat. WPT Tier-1 24/26 flat, pinned on the fix.
- `y_table.py` after: `span.highlight` dy 0.2, dx −3.1 (line 3 is a mixed
  line — not justified — so the words before the span sit at natural
  spacing; Chrome's are expanded).

## Ledger (not chased)

1. Mixed-line justification: line 0 of a mid-line split (siblings own part
   of the line) stays start-aligned. Needs distribution across sibling runs.
2. h1 "The Art of Typography": RustKit text box 382.7px vs Chrome ink 446
   (−14%); the italic subtitle is only −2%. Suspect Georgia Bold face
   substitution / synthetic bold (memory: CoreText never fails
   `new_from_name`). 4,936 differing px in the h1 band — the largest
   remaining visible term on this case.
3. `<pre>` collapses to one line: the block path never wraps under
   `white-space: pre`, so preserved newlines make no line boxes (65 vs 195
   px). Below the fold here; every code block on every docs page.
4. `column-count` unimplemented (`.columns`); `::first-letter` drop cap
   unimplemented; inline `code` x drift (−40px at the first `<code>` of
   p:nth-of-type(4)) — all below the fold.
5. A split run's last line does not move when a taller follower raises the
   line's ascent.
6. Pre-existing: the wrap shapes without letter/word-spacing.

## Tools (scratch_n49, local)

`banddiff.py` (per-row-band diff vs Chrome), `coldiff.py` (per-column diff /
ink ratio — a ratio rising left→right is position drift, flat is
rasterization), `wordpos.py` (word start/end x per line in two frames),
`strips.py` (Chrome-over-RustKit crops), `textboxes.py`, `capture.py`
(parity-capture wrapper), `fmtcheck.py` (rustfmt --check on named files).
