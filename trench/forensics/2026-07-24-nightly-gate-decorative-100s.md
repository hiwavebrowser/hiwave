# Nightly Parity Gate is decorative — empty captures recorded as 100.0, red every day since ≥07-12

**Author:** Atlas · **Date:** 2026-07-24 (night block 19) · **Lane:** instrument forensics, no fix landed

## Symptom
`Parity Gate` workflow on `hiwave-macos` master is **red on every scheduled run in the visible window** (07-12 → 07-23, all `failure`), including before AND after the #54/#55/#56 stack merged. The PR-level gates (pr-aggregate + pr-swarm) — the merge instrument — were green throughout and are unaffected.

## Receipts (run 30002452220, 2026-07-23, master @ d6c45ba)
- nightly-aggregate: 91 cases (case × 3-viewport matrix), **25/91 pass, avg diff 73.36%** — vs the same tree measuring **25/26 avg 6.75** on the campaign instrument locally (07-22 run).
- Dozens of cases score **exactly 100.0 with an EMPTY `pixel` object and `error: null`** — e.g. `css-selectors` 100.0 at all three viewports, `about` 100.0 at 1280×800/1920×1080 while scoring its real 16.17 at its registered 800×600.
- A capture that produced nothing is being recorded as a 100%-diff *measurement* with no error string. This is the same instrumentation lie fixed in the commit-path in night 2 (BASELINE night-2 scope item 2) — still alive in the nightly swarm shard path.
- The 3-viewport matrix itself was never re-pinned to the chrome-148 single-viewport baseline tree (R0 hard-fail shipped only on the campaign path). Multi-viewport expansion is explicitly gated by the viewport plan (Tiers 2–5) — the nightly lane predates that gate and kept running.

## Why it matters
- A permanently-red master badge reads as "master is broken"; the truth is "the nightly instrument measures nothing at 65/91 of its matrix."
- Any future regression that ONLY shows at nightly level is invisible inside the standing red.

## Options (queued, not chosen)
1. **Re-pin the nightly matrix to registry viewports** (each case runs only at its registered viewport) + hard-fail empty captures as `error`, not 100.0. Turns nightly into a real gate; ~1 session of CI/tooling work.
2. **Disable the scheduled nightly lane** until option 1 is funded (stops the decorative red).
3. Leave as-is (rejected by the campaign's own instrument-first discipline — a red gate that can't go green is a dead instrument wearing a live badge).
