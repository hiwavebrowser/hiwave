## CH2.B18 (1): a border side with a style and no width is `medium`; `thin`/`medium`/`thick` widths

Branch `atlas/z-ch2-b18-border-medium` @ `a5d07ce4` (red `3e712d8b`), off develop `33f4aa93`. No PR yet: 16/16 open at 04:25 ET. **Land after #937 (CH2.E14)**; see the A/B below.

**Before:**
- `border-style: solid` with no width laid out 0px on every side. Chromium 143 gives `medium`, which is 3px; the initial `border-width` is medium (CSS Backgrounds 3 §3.3).
- `border-width: thin|medium|thick` and the `border-*-width` keywords were dropped.

**After:** an explicit non-none style (`border-style`, `border-<side>-style`, and their logical aliases) on a side whose width is still unset takes 3px. "Unset" means `Length::Zero`; since #921 an authored `0` is stored as `Px(0.0)`. The width keywords parse as 1/3/5 px. RustKit's initial `BorderStyle` is `Solid` (so a bare `border: 2px` paints), which is why the unset width can't simply start at 3px.

**Red → green:** `border_medium_tests` checks 14 Chromium 143.0.7499.4 pages (`tools/parity_oracle/border_medium_cases.json`). They cover style only, a side style, two-value style, width before and after style, `0`, thin, thick, a side `medium`, none, none↔style order, a rule, and `border:solid`. Develop gets 6/14 right; this branch gets 14/14. `computed_read` border-style `solid dashed` was a marked gap whose note named this bug ("a solid side with no width set lays out 0px wide, so its style reads none"). It now reads right, so I dropped the mark.

**Narrow runs:**
- engine `border` filter: 16/0
- `computed_read_tests --test-threads=1`: 22/0
- An earlier multi-filter run at default threads lost 11 computed_read families to GPU-guard timeouts behind `r1_cases` under load. That's environmental; all 22 pass single-threaded.

**Campaign** (`--profile parity`; base sha256 689d051e…, candidate dc1d4b73…): 26/26, 0 moved.

**Chrome board:** 42/42 rows identical, 13/42 green on both.

**20-site A/B** (`ab5.py`, A=develop, B=candidate):
- **netflix 0.20% on all four cross pairs, 0 inside each arm.** The "Sign In" and "Get Started" buttons gain a 3px black frame. The cause, read from Chromium 143's rules for those buttons: `.…::after { border-style: solid; border-width: var(--hcw--local-design--Button-BorderWidth) }`. RustKit doesn't resolve `var()` on pseudo-elements (CH2.E14, #937, batch 27), so the width declaration is dropped and the side's width stays unset. Before this branch that unset width painted 0px; now the style makes it `medium`.
  - Re-run with #937 @ 281f7574 merged into **both** arms (develop+937 sha c6ec83ee vs candidate+937 a6c83884): **netflix 0.00% on all pairs.** So this is #937's gap showing through, not a regression of its own. Per css-variables-1 an unresolvable `var()` is `unset` → `medium` too, so the branch is right once the variable resolves.
- linkedin: 89.86% all pairs in the first pass, because arm B got linkedin's "Something went wrong" page twice. The swapped pass (A=candidate) gave 0.00% everywhere, so that was the site.
- google 1.53% and bing 25.38%: noise inside arm B (B1 differs from B2).
- cnn: capture timed out on both arms (30 s).
- Every other site: 0.00%.

**Not in this item:** `border-width: initial` declared after a style still reads 0 (Chromium medium). B18's other items (2)–(6) are untouched.

Toolchain: rustup 1.91.0 / stable, aarch64-apple-darwin. Builds through z-cargo (lease + sccache). Host: macOS seat. Chromium 143.0.7499.4 (pinned oracle).
