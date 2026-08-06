# WPT Tier-1 runner: three fails were never engine failures — and one gap explains the rest

Night block 20 (macOS seat, 2026-08-06). Instrument work, no engine change.
Base: `hiwave-macos` master `427390c`. Branch `atlas/wpt-slice0`.

## Why the night went here instead of the wrap lane

Night 19's exit pointed at "the 18 Tier-1A fails (overflow-wrap / word-break /
line-break `anywhere`)". Pre-flight found two things that re-scoped it:

1. **There are two W0b runners.** Master carries one (PRs #74/#77, 14-case
   seed, 6/12), and this seat's `atlas/wpt-w0b` (PR #99, 30-case seed, 8/26)
   carries a different one. They were built in parallel lanes and they
   conflict on `scripts/wpt_tier1.py` + `trench/wpt/last-run.json`.
   **Each has a guard the other lacks.** Tonight ports master's missing
   guards onto master; the seed reconciliation is a decision for Pete.
2. **Master's runner was scoring unrunnable tests as engine failures.**
   Three of its six fails could not reach the state they assert about.

Instrument-first rule held: master's 6/12 receipt was reproduced bit-exact
(same six ids, same statuses) before anything was touched.

## Finding 1 — reftest-wait / script-driven tests were counted as FAIL

`empty-span-height`, `empty-span-size-001`, `empty-text-node-001` all carry
`<html class=reftest-wait>` and a `<script>` that mutates the DOM into the
state under test (`empty.style = ''`, `appendChild(createTextNode(""))`).
`empty-span-scroll` needs `scrollTarget.scrollIntoView()`.

The parity-capture path has no script host. So those documents never reach the
asserted state, and the frame comparison measures "no JS", not line-box
behaviour. Upstream WPT reports TIMEOUT for a reftest-wait test that never
signals — not FAIL.

Charging the renderer for the harness's missing capability is the
decorative-instrument class this campaign keeps finding (2026-07-24: empty
captures scored 100.0). These are now **SKIP with the reason recorded**.

`empty-span-scroll` had additionally been hidden behind the blank-frame ERROR
guard — the guard fired correctly, but on the second-order symptom.

## Finding 2 — the Ahem font was never in the tree, and @font-face is dead code

`wpt_sync.sh` materialises tests and refs only. WPT tests reference shared
support files by root-absolute URL (`/fonts/ahem.css`), which wptserve maps to
the WPT root and `file://` does not map at all. Fifteen of the seed's
candidate cases declare Ahem; **not one of them ever got it.**

Fixed both halves:
- `MANIFEST.support_paths` now lists `fonts/ahem.css` + `fonts/Ahem.ttf`;
  `wpt_sync.sh` materialises them; `scripts/wpt_fetch_support.py` does the same
  on this seat (no `git clone` on the allowlist).
- The runner stages root-absolute references against the WPT root, recursively
  for referenced CSS, so `url('/fonts/Ahem.ttf')` inside `ahem.css` resolves too.

**Result: exactly zero pixels changed.** `overflow-wrap-001` stayed at 0.7054%
and `overflow-wrap-002` at 2.495% — byte-identical diffs before and after the
font became reachable on disk. That is the receipt for the root cause:

> **`@font-face` is unimplemented.** `rustkit-layout::FontLoader::load_font`
> fetches nothing and registers nothing (its body is a comment describing what
> a real implementation would do), and `queue_font_face` has exactly one caller
> in the whole tree — `tests::test_font_loader`, its own unit test.
> `FontFaceRule` is populated by no parser.

This is the **eighth** parsed-but-dead behaviour found this campaign (n18 found
the seventh: `should_collapse_with_last_child`, also fully unit-tested with zero
call sites). The pattern is now strong enough to be a standing check, not a
recurring surprise: *a type with a test and no non-test caller is decoration.*

**These cases stay in the denominator.** A browser that cannot load web fonts
is non-conformant, and WPT is right to fail it. They are tagged `blocked_by`
so the digest can name one capability gap instead of counting N text bugs.

## Finding 3 — the more dangerous direction: green cases not measuring anything

Three cases **PASS** while their declared font never loaded
(`overflow-wrap-004`, `br-font-size`, `br-line-height`). At least one is
near-tautological: `overflow-wrap-004`'s reference is the same document minus
`overflow-wrap: normal` — the *initial value*. Any engine passes it, Ahem or
not. The runner now emits these as `attribution.suspect_passes` and prints them
under the rate.

## Board

| | before | after |
|---|---|---|
| scored | 6/12 (50.0%) | **6/9 (66.7%)** |
| fail | 6 | 3 |
| skip | 0 | 4 |
| error | 2 | 1 |

**The rate went up because unrunnable cases left the denominator, not because
the engine improved. No engine code was touched tonight and the two numbers are
not comparable.** 6/12 was wrong in the pessimistic direction; 6/9 is measured
against tests that can actually probe their assertions.

Of the 3 remaining fails, **2 are one capability gap** (@font-face). The only
unattributed fail on the landed seed is `css-inline/empty-span-size-002`
(0.6658%) — a real, script-free, font-free line-box case. That is the honest
head of the queue.

Remaining ERROR: `css-flexbox/align-items-baseline-overflow-non-visible`
renders blank on both sides — a real render refusal, still unattributed.

## What this did NOT do

- No threshold moved. `WPT_MAX_DIFF_PCT` is still 0.0 (exact match).
- No case was removed from the manifest.
- No engine code changed. The soft-wrap lane (night 19's target) is untouched
  and still the next engine night — but it now has a prerequisite with a name.
