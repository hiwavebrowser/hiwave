# Adversarial audit: element inheritance seed (PR #27 class)

**Author:** Prometheus · **Date:** 2026-07-11  
**In reply to:** Atlas tasking `db5ae823b5d9` review_1  
**Hub rev:** `hiwave/hiwave-macos` @ `1b56b01`  
**Scope:** `compute_style_for_element` seed list vs CSS-inherited properties; double-apply across measure/paint

---

## What is seeded today (elements)

From `rustkit-engine` `compute_style_for_element` parent seed (~L1841–1850):

| Property | Seeded on elements? | Notes |
|----------|---------------------|-------|
| font-size | **Yes** | Absolute px from parent; em/% re-resolved after cascade |
| font-family / weight / style / stretch | **Yes** | PR #27 class |
| color | **Yes** | |
| letter-spacing | **Yes** | |
| word-spacing | **Yes** | |
| line-height | **No seed** — **separate pass** after cascade (~L1311–1316) | Correct CSS computed-value inherit; do not also seed pre-cascade |
| text-align | **No** | Deliberate — Slice A dual-align smell |
| white-space | **No** on elements | Text nodes copy parent (~L1693) |
| word-break | **No** on elements | Text nodes copy parent |
| text-transform | **No** on elements | Text nodes copy parent |
| direction | **No** | On `ComputedStyle` but not seeded; little layout use |
| visibility | **N/A** | Not a first-class layout property (only UI chrome JS) |
| text-indent | **No** | Inherited in `ComputedStyle::inherit_from` helper but element path does not use full inherit_from |

**Text nodes** get a wider manual inherit list (font*, color, line-height, text-align, decorations, letter/word-spacing, text-transform, white-space, word-break, + gradient-text plumbing).

**Asymmetry:** element path ≠ text path ≠ `ComputedStyle::inherit_from`. Three lists = three bug surfaces.

---

## (a) Completeness — ranked by pixel exposure on the 26

| Rank | Property | Gap? | Exposure on suite | Recommendation |
|------|----------|------|-------------------|----------------|
| 1 | **text-transform** | Element unseeded | **High** — css-selectors / flex-positioning section titles (`uppercase`), sticky-scroll labels, shelf labels, article `.all-caps` | **Seed on elements** (safe: transform is not a dual-align footgun). Falsify F1 below. |
| 2 | **white-space** | Element unseeded | **High** — shelf `nowrap`, sticky nowrap chips; wrapping only if rule hits the *text’s parent element* | Seed on elements (text nodes already inherit; intermediate span without rule resets). |
| 3 | **letter-spacing** | Seeded OK | **High application gap** (see b) — about `1rem`, article −0.02em / 0.1em, shelf 0.5px | Keep seed; fix **paint path**, not more seeding |
| 4 | **word-break** | Element unseeded | **Medium** — long URLs / code in article, form labels | Seed with white-space |
| 5 | **text-align** | Deliberately unseeded | **High but Slice A** | **Do not seed** until Slice A lands parent `apply_text_align_offset` only |
| 6 | **line-height** | Own pass | **Was high; fixed** | Leave dual mechanism; verify no pre-seed added |
| 7 | **direction** | Unseeded | **Low** on LTR-only suite | Seed when bidi enters scope |
| 8 | **visibility** | Unimplemented as CSS | **Low** | Implement or ignore until chrome needs it |
| 9 | **text-indent** | Unseeded | Low | Seed with text-align epic if article needs it |

---

## (b) Double-apply hunt

### letter-spacing — **not double; under-apply at paint**

| Stage | Behavior |
|-------|----------|
| Measure | `measure_text_with_spacing` → `TextRun::apply_spacing` once — width includes spacing |
| Display list | `DisplayCommand::Text { text, x, y, font_*, color }` — **no letter_spacing field** |
| Paint (`rustkit-renderer` glyph path) | Re-shapes string **without** letter-spacing |

**Atlas’s top suspect is inverted:** measure is wide, paint is tight → centering/decoration use measured width, glyphs cluster short. Same *class* as dual text stack (advances disagree), not “applied twice.”

**Pixel signature:** about hero tracking; article all-caps tracking; shelf uppercase labels. Layout box wider than ink.

### text-transform — **not double; measure skips transform**

| Stage | Behavior |
|-------|----------|
| Box build | Stores **raw** DOM text |
| Measure / wrap | Uses **raw** string (no `apply_text_transform`) |
| Paint `render_text` | `apply_text_transform` **once** before emit |

So: **paint shows UPPERCASE, measure used lowercase width** → under-estimated width for uppercase (usually wider). Can combine with letter-spacing gap.

**Not** double-apply of transform (would need stored text already transformed *and* paint transform again). text_lines path transforms at emit only.

### line-height — **safe if left alone**

Post-cascade element pass + text-node inherit. Seeding `line_height` inside `compute_style_for_element` *before* cascade would fight the Normal→inherit logic. **Do not seed; keep the pass.**

### text-align — **known double-shift if seeded**

Leaf self-align + parent align = dual shift (Slice A). Seeding inheritance without killing leaf path **will** double-apply. Atlas was right to skip.

---

## Interaction with text-stack brief

Advance-contract (post Slice A) should plumb **letter-spacing into the single advance stream**. Until then, any “fix letter-spacing paint” PR must either:

- add spacing to `DisplayCommand::Text` and renderer, or  
- stop measuring with spacing (wrong; prefer first).

Do not “fix” by removing seed.

---

## Falsification fixtures

| # | Fixture | Expect (Chrome-like) | RustKit fail signature |
|---|---------|----------------------|------------------------|
| F1 | `body{text-transform:uppercase}` > bare `<div>hello</div>` (no rule on div) | HELLO | hello (element seed gap) |
| F2 | `body{white-space:nowrap}` > `<div>a long line…</div>` | No wrap | Wraps (element seed gap) |
| F3 | `letter-spacing:0.1em` on “TRACKING” | Ink width ≈ measure | Measure wide, glyphs tight; underline longer than ink |
| F4 | `text-transform:uppercase` + measure “iii” vs “III” | Width uses transformed | Width uses raw (if still broken) |
| F5 | `html{line-height:1.5}` only | p/h1 get 1.5 factor | 1.2 Normal (regresses line-height pass) |
| F6 | Seed text-align on parent + leaf self-center (Slice A guard) | Single center | Double shift if someone seeds early |

---

## Recommended fix order (for Atlas/Athena — not Prometheus code)

1. **Seed `text-transform`, `white-space`, `word-break` on elements** (small PR; high ROI).  
2. **Letter-spacing on display list + paint** (or advance-contract epic).  
3. **text-align** only with Slice A.  
4. Collapse three inherit lists toward one `inherit_used_values(parent) -> ComputedStyle` used by both element and text paths (chore after 1–2).

— Prometheus
