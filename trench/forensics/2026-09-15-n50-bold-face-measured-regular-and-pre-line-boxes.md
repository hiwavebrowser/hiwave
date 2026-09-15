# n50 — bold named families were MEASURED with the regular face; `<pre>` had no `white-space: pre`, no line boxes at newlines, and a block never grew past an inline child's wrapped lines

Night block 50, 2026-09-15 (macOS seat, Atlas). Lane = n49 digest option (a)
`<pre>` line boxes, with option (b)'s bold probe as the first ten minutes —
the probe said "jump the queue", so both lanes shipped. Basis develop
`da8f413` (unchanged since n45). Branch `atlas/n50-pre-line-boxes` @
`461cfa1` (+ receipts `1c41594`), PR #200 to develop: rustkit-text,
rustkit-layout, rustkit-html, rustkit-engine.

## The probe (ten minutes, decisive)

`scratch_n50/bold-probe.html` — "The Art of Typography" at 44px in Georgia
700 / 400 / 700 with `letter-spacing: -0.02em`, plus `MMMM` in Menlo 400/700
— rendered by both engines, ink width per row (`ink_rows`):

| row | Chrome 148 | RustKit before | RustKit after |
|---|---|---|---|
| Georgia 700 | 518 | 453 | **518** |
| Georgia 400 | 450 | 450 | 450 |
| Georgia 700, ls −0.02em | 500 | 435 | **500** |
| Menlo 400 / 700 | 103 / 104 | 103 / 104 | 103 / 104 |

RustKit's bold row was the regular row's width: neither the bold face nor a
synthetic bold. The frame (`bold_strip.png`) showed bold GLYPHS crammed into
regular ADVANCES — paint had the right face, layout did not. That was the
"−14% h1" of the n49 ledger: 4,936 differing px on the case's largest term.

## Root cause 1 — the layout resolver guessed names in the wrong order

`rustkit-layout/src/text.rs` `TextShaper::create_ct_font_with_traits`
built `variants_to_try = vec![family]` FIRST and appended `-Bold` /
`-Italic` guesses after it, then walked the list through `named_font`
(which accepts a face whose family or PostScript name matches). "Georgia"
is an installed family, so it answered for every weight and style. Paint's
resolver (`rustkit-text` `create_font_with_traits`) had the styled variants
before the bare name, so paint drew Georgia-Bold. Two resolvers, one order
right, one wrong: every `font-weight: 700` heading, every `<strong>`,
every `<em>` on a named family measured narrower than it painted.

Name guessing was also blind to real PostScript names: a Swift probe
(`fontprobe.swift`) showed `Arial-Bold` → Helvetica (substitute), while
Chrome's bold Arial is `Arial-BoldMT`, Times New Roman's is
`TimesNewRomanPS-BoldMT`, and Helvetica Neue / Avenir Next have full weight
ladders with no `-Bold` convention.

## Fix 1 — one resolver, the Chrome/Skia way

`rustkit_text::macos::family_face(family, size, weight, italic)`: a Core
Text descriptor with `kCTFontFamilyNameAttribute` + `kCTFontTraitsAttribute
{ kCTFontWeightTrait, [kCTFontSymbolicTrait = italic] }`, instantiated via
`CTFontCreateWithFontDescriptor`, accepted only when the answer's family
name is the one asked for (Core Text substitutes Helvetica for a family it
lacks). `fontprobe2.swift` mapped Core Text's nearest-weight answer per CSS
weight for Georgia / Arial / Times New Roman / Helvetica Neue / Menlo /
Avenir Next; two disagreements with css-fonts-4 §5.2 are corrected in code:

- weight ≤ 500 must never land on a bold face when a lighter one exists
  (Core Text: Georgia 500 → Bold, nearest to 0.23; CSS walks 500 → 400
  first) — re-lookup at 400 when the answer carries the bold trait;
- weight ≥ 600 takes the next HEAVIER face (Core Text: Helvetica Neue 600 →
  Medium; CSS walks upward → Bold, which is what Chrome draws) — re-lookup
  at 700 when the answer lacks the bold trait.

Both resolvers call it first; the name guesses stay as a fallback for
PostScript-name inputs ("HelveticaNeue-Light"), styled variants before the
bare name on the layout side now too. Tests: `family_face` per
family/weight/italic (`family_face_picks_the_css_weight_not_the_nearest`,
rustkit-text) and the layout-side width test
(`bold_named_family_shapes_with_its_bold_face`: bold > 1.10 × regular,
italic ≠ regular, `create_ct_font_with_traits("Georgia", 700)` =
`Georgia-Bold`) — T-RED by the probe's numbers.

## Root cause 2 — `<pre>`: three defects stacked

The n49 ledger said "the block path never wraps under `white-space: pre`".
True, but the FIRST defect was upstream: the engine's UA arm for `pre` set
display/margins/monospace and ended with `// white-space: pre (not
implemented)`. article-typography's `pre { … }` rule has no white-space, so
its text was collapsed like a paragraph — the repro's "before" dump showed
`'first line third line'` with the newlines already gone.

With white-space set, `layout_text_with_zero_wrap` still skipped the
wrapper (`can_wrap` false under Pre), and for pre-wrap / pre-line it only
called the wrapper when the whole run OVERFLOWED — a two-line run that fit
its container stayed one line. The wrapper's mandatory-break pass
(`break_into_lines`) has always existed; nothing reached it.

Third: the tree builder kept the newline right after `<pre>`. HTML
§13.2.6.4.7 ("pre", "listing": if the next token is a LINE FEED, ignore
it). Once newlines became line boxes every `<pre>\n…` would have gained an
empty first line.

## Fix 2

- rustkit-engine UA: `pre` → `white_space = Pre` (also `listing` / `xmp` /
  `plaintext`).
- rustkit-layout `layout_text_with_zero_wrap`: `has_segment_breaks` (pre
  family AND a `\n`/`\r` in the run) forces the wrapper path; the wrap width
  is the container's where soft wrapping applies and `f32::INFINITY` under
  `pre` / an unresolved width, so only the forced breaks split; a
  single-segment run with a trailing newline still takes the line-box path
  (the break character never reaches the single-line measurement); the
  unresolved-width clamp mirrors the single-line path.
- rustkit-html: `ignore_lf` armed by a `pre`/`listing` start tag, consumed
  by the next token in `handle_in_body`.

Receipt `parity-tests/repro/pre-line-boxes.html` (640×560) vs Chrome 148:
A `pre > code` six lines, B `<pre>` with leading newline / blank line /
trailing newline, C pre-line with a wrapping middle line, D pre-wrap, E
normal control. **179,023 → 14,526 differing px**; B/C/D/E rows at 186 /
299 / 437 / 551 = Chrome's rects; B is three line boxes (leading newline
dropped, blank line kept, trailing newline not a line) at Chrome's 83px.

## Root cause 3 (revealed) — a block did not grow past an inline child's wrapped lines

The first fixed capture put A's `code` text at 126px tall but the NEXT
row's label at y 81 (Chrome 186). `scratch_n50/inline-wrap-probe.html`
made it plain on develop's own semantics: `<p style="width:300px"><span>long
text</span></p>` laid out **24px tall for 72px of text**; the following
`<p>` painted over lines 2–3. Both block child loops
(`layout_block_children`, `_with_collapse`) advanced the flow by one
line-height for a non-atomic inline child, whatever its text had wrapped
to (the inline's own rect is deliberately its content area, §10.6.1, and
nothing else looked inside it). Every `<p><a>…</a></p>`, every
`<li><span>…</span></li>` longer than a line on real pages overlapped its
successor.

Fix: `inline_wrapped_tail(inline, container_left)` walks the inline's
descendants for the last text box with `text_lines.len() > 1` and reports
`(n, end x of the last line, line height)`; the loop then does exactly what
the phase-5 text split does — closes the current line box, advances
`(n − 2)` full lines, and leaves the last line open at `cursor_x = last_end`
for following inline content. Test
`a_block_grows_past_an_inline_childs_wrapped_lines` (normal + pre).

## Board

Basis develop `da8f413` (n46 clean-tree board, 26/26 avg 2.6245). On
`461cfa1`: **26/26 avg 2.5774**, 23/26 byte-flat — article-typography
**7.4646 → 6.1844** (h1 text box 382.7 → 444.5px vs Chrome's 446 ink; h2
417 → 482; the `<pre>` block 50.7 → 152px = six line boxes at Chrome's y
1252; every `<strong>` label in the lists widened and its sibling text
moved right by the difference), css-selectors 2.6694 → 2.6689, **new_tab
2.5924 → 2.6490**. new_tab, honestly: layout dump identical (0 of 157
boxes moved); the 3,265 changed px are the four rows of `<kbd>` keys —
`font-weight: 600` in `monospace`, which Chrome paints in **Menlo-Bold**
(the kbd strip: basis regular, after bold, Chrome bold). The count vs
Chrome rises because bolder ink sits at the keys' pre-existing wrong y
(RustKit row y 289, Chrome 352 — a 63px offset that is not tonight's). WPT
Tier-1 24/26 flat, pinned on `461cfa1`.

## Ledger (not chased)

1. `family_face` runs per `shape()` call (as `named_font` did); a
   per-(family, size, weight, italic) cache if board wall time moves.
2. Weight 900 on families with a Black/Condensed face (Helvetica Neue 900 →
   `CondensedBlack`; Skia also matches width) — enumerate the family's
   faces and run the full §5.2 walk instead of nearest + corrections.
3. `text-align: center/right` on a block whose inline child wrapped: the
   closed lines are one alignment record (widest line), not per line.
4. A pre-wrap / pre-line run starting mid-line with a newline that FITS the
   remaining width does not split (the flow path splits only on overflow).
5. `<textarea>` leading-newline rule (RCDATA path) not wired.
6. new_tab's kbd rows sit 63px above Chrome's; article-typography's
   `column-count`, `::first-letter`, inline `code` x drift (n49 ledger).

## Tools (scratch_n50, local)

`capture.py` / `chrome_repro.py` (RustKit / pinned-Chrome captures of an
ad-hoc file), `pre_receipt.py` (stacked strip + Chrome rects + RustKit
text boxes + per-band diff), `dumpboxes.py` / `dumptext.py` (layout dump
walkers), `fontprobe.swift` / `fontprobe2.swift` (CoreText name and
descriptor answers per CSS weight; run through a python3 subprocess
wrapper — `swift` is not allowlisted), `boardcmp.py` (per-case basis →
new), `fmt_mine.py` (rustfmt --check restricted to this branch's hunks —
both crates carry pre-existing fmt debt), `kbdstrip.py`.
