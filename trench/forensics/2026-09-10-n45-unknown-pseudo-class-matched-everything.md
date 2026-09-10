# n45 — an unknown pseudo-class matched every element; `:is()`/`:where()`, the `-of-type` family, `:link`, `:empty`, `:placeholder-shown` all fell through the same arm

Night block 45, 2026-09-10. Lane: the n44 digest's option (a), taken by the standing rule (no Pete answer; the exchange carried only Argos gauge snapshots). Basis: develop `da8f413` (#191 rounded gradient clip + #192 currentColor merged 2026-09-10 01:50Z), fresh parity-capture, campaign 26/26 avg **2.6245** (25 of 26 byte-flat vs the n44 receipt; the mover is #191's `gradient-backgrounds`). Branch `atlas/n45-unknown-pseudo-class` → PR to develop. Engine only.

## The defect

`rustkit-engine` `match_pseudo_class` ended in `_ => true`. Every pseudo-class the arm list did not name matched **every element**:

- `:is()`, `:where()`, `:matches()`, `:-webkit-any()` — so `:where(ul, ol) { padding: 0 }` (every modern CSS reset) zeroed padding on every element, and `:is(h1, h2, h3) { margin: 0 }` on every element.
- `:first-of-type`, `:last-of-type`, `:only-of-type`, `:nth-of-type()`, `:nth-last-of-type()` — `h2:first-of-type` styled every h2, `tr:nth-of-type(even)` every row.
- `:link`, `:any-link` — `a:link { color }` was fine (subject is `a`), but `.nav :link` painted every descendant.
- `:placeholder-shown`, `:required`, `:optional`, `:read-only`, `:read-write`, `:valid`, `:invalid`, `:in-range`, `:default`, `:indeterminate`, `:autofill` — every input took its placeholder/invalid styling.
- `:has()`, `:lang()`, `:dir()`, `:defined`, `:fullscreen`, `:modal`, `:popover-open`, `:paused`/`:playing` — all matched everything.
- Legacy single-colon pseudo-elements `p:first-line`, `p:first-letter` styled the whole `p` (the host guard only knows `:before`/`:after`).
- Vendor pseudo-classes from other engines (`:-moz-focusring`) — Chrome drops the rule; RustKit applied it to everything.
- `:empty` was hardcoded `false`.

And the rule-level half: Selectors 4 §3.9 says a selector list with an invalid member is invalid **as a whole** — `.a:frobnicate, .keep {}` styles nothing in Chrome. The comma branch evaluated each member independently, so `.keep` got styled.

The census (`scratch_n45/census.py`, over `cases/registry.json`) shows **no board case uses any of these** — the campaign meter is blind to this lane by construction. The receipt is the repro.

## The fix

1. **Validity gate** (`selector_list_is_valid`): every `:name` outside brackets/quotes must be a pseudo-class the engine decides (`pseudo_class_is_supported`) or a legacy pseudo-element; `:is()`/`:where()` arguments are forgiving (unknown names inside are ignored, per spec). An invalid list returns false from `selector_matches` before the comma split — the whole rule is dropped, as Chrome does. The `_ => true` arm is gone (`_ => false`, unreachable by construction).
2. **`SiblingContext`** replaces the `element_index, sibling_count` pair through the build walk → `compute_style_for_element` → `selector_matches` → `simple_selector_matches_with_pseudo` → `match_pseudo_class`: adds `type_index`/`type_count` (same-tag siblings, computed in the child loop next to the existing `:nth-of-type` selector-path totals) and `has_children` (any element or text child — whitespace counts, comments do not; Selectors 4 §14.5). `create_pseudo_element` now receives the host's real sibling context instead of `(0, 1)`, so `li:first-child::before` and `.slot:empty::before { content }` match the right hosts.
3. **New arms**: the `-of-type` family; `:is`/`:where`/`:matches`/`:-webkit-any` and `:not()` take a selector list (`split_top_level_commas`; a member with a combinator under-matches — ledgered); `:link`/`:any-link` (a/area with href); `:empty`; `:placeholder-shown` (placeholder attr, no value); `:required`/`:optional`/`:read-only`/`:read-write`/`:valid`/`:invalid`/`:in-range` from attributes; `:checked` restricted to checkbox/radio/option; `:disabled`/`:enabled` restricted to form controls; `:defined` (no hyphen in the tag); `:lang()`/`:dir()` from the element's own attribute; `:root`/`:scope`; `:has()` and the document-state pseudo-classes (`:fullscreen`, `:modal`, `:popover-open`, `:playing`, …) false; `:paused` true for audio/video; `:first-line`/`:first-letter` false on the host.
4. **Tokenizer**: `tokenize_selector` now tracks parentheses — `:is(.a, .b)` used to split at the space into two tokens (`:is(.a,` and `.b)`), which is why `:is()` could never have worked even with an arm. The comma split guards against a member equal to the whole selector (an unclosed paren recursed forever — found by a stack overflow in the first test run).

## Receipt — `parity-tests/repro/unknown-pseudo-class.html` vs pinned Chrome 148

Five rows of 40px swatches, blue unless a rule turns them red/green (`scratch_n45/swatches.py` reads the centre pixel of each; Chrome via `scratch_n36/chrome_capture.py`, RustKit via `scripts/run_repro_capture.py`, both 400×200).

| row | rule under test | Chrome | develop `da8f413` | with fix |
|---|---|---|---|---|
| A | `#a :is(.pick, .other)`, `#a :where(.pick)` | red blue | **red red** | red blue |
| B | `span:first-of-type`, `span:last-of-type`, `div:nth-of-type(2)` | red blue red blue green | **red red red green green** | red blue red blue green |
| C | `.sw:placeholder-shown`, `.sw:link`, `.sw:any-link`, `a {}` | blue blue red | **red red red** | blue blue red |
| D | `.sw:frobnicate`, `.sw:frobnicate, #d .keep` | blue blue | **red red** | blue blue |
| E | `.sw:empty`, `.sw:required`, `.sw:read-write` | red blue red | **red red red** | red blue red |

develop: 14 of 15 swatches wrong. With fix: 15 of 15 = Chrome. Frames banked: `scratch_n45/repro_before.png`, `repro_after.png`, `chrome-repro/baseline.png`.

## Tests
rustkit-engine 82 → 87: unknown pseudo-class invalidates the whole rule (incl. `:-moz-focusring`, `:first-line`); `:is`/`:where`/`:not(list)`; `-of-type` typed index; `:link`/`:placeholder-shown`/`:empty` (whitespace-only span is NOT empty); validity + top-level comma splitting as pure functions. T-RED is the repro's develop column: the arm the tests exercise did not exist.

## Ledger (not chased)
- `:is()`/`:where()`/`:not()` members with a combinator (`:is(.dark .card)`) under-match (false) — the compound matcher has no ancestor chain. Chrome matches them; a theme rule written that way is missing, not applied everywhere.
- `:has()` is false. Same reason, needs the subtree.
- `:lang()` reads only the element's own `lang`; the inherited language (`html[lang]`) is not consulted — `:lang(en)` on a descendant is false. `:dir()` likewise reads only the own `dir` attribute.
- Structural pseudo-classes and attribute selectors on ancestor/sibling compounds still match unconditionally (n44 ledger, unchanged): `li:first-of-type > a`, `[hidden] p`. The validity gate does apply to them (an unknown name on an ancestor compound now drops the rule).
- `:checked` on `<option selected>` matches, but `<select>` rendering does not read it.
- `:valid`/`:invalid` see only `required` + empty value; `pattern`, `min`/`max`, `type=email` constraints are not evaluated. `:in-range` is true for any input carrying `min`/`max`.
