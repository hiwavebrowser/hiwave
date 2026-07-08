# Trench digest — macOS seat (Atlas)

## Night 1 — 2026-07-08 (Phase 0 exit)

**Metric (unified pass rate, t15):** 46.2% vs stale chrome-120 → **34.6% (9/26) vs pinned CfT 148.0.7778.216** — the honest re-pinned number, now the campaign metric. Not a regression: the old reference was 28 Chrome versions stale and 3 of its "failures" were missing PNGs scoring fake 100s. Same drop shape Athena saw on Windows.

**Landed on `atlas/trench` (hiwave-macos):**
- `5d14baf` — Athena's portable fixes ported: `--use-angle=swiftshader`, PARITY_CHROME_PATH pin, her capture_all_baselines.mjs, parity_lib chrome-148 re-pin. Pin verified: launch reports 148.0.7778.216.
- `fc7531d` — full 26-case chrome-148 baseline tree + parity_test.py re-pin (it had its own hardcoded chrome-120 copy). gpu-gradient-regression baseline captured for the first time (instrumentation debt paid: 3 fake-100% entries now measure a real 32.8%).

**Un-merged, awaiting Athena's review — PR hiwavebrowser/hiwave-macos#3 (`dedd597`, shared crate rustkit-layout):**
- Root cause of the settings "100%" failure: block children of a flex item are each laid out against a clone of the item's FINAL dimensions; block layout uses `content.height` as the flow cursor, so every child stacks at the item's bottom edge. `body{display:flex}` + tall content = whole page renders below the viewport → flat-background frame.
- Minimal repro geometry matches Chrome exactly after fix (548.0/599.2). settings 30.8→17.9, shelf −0.9, five cases +0.5..+5.6 where newly-visible content exposes real gaps. 211/211 crate tests pass.
- Cross-seat: Athena's width=0.0 lead does NOT reproduce on macOS (272/272 boxes sized). But "content collapsed by flex parent" may be the same family as her four ~99% builtins failures — recommend she re-tests Windows with the PR patch.

**Not done (deliberately, 2h cap):** aleph vendor-mask + index rebuild — untouched, first item tomorrow night. WPT runner (Phase 0.5) unstarted; Athena exited Phase 0 first, so per plan it's hers unless she defers.

**Decisions needed from Pete (≤3):**
1. **Merge gate:** PR #3 is a shared-crate fix with cross-seat review pending. If Athena confirms it helps Windows, does her approval auto-merge it, or do you want eyes on every rustkit-* merge this early?
2. **Threshold sanity:** settings now fails at 17.9% vs t15. Its remaining diff is real (form controls, background-clip:text). Keep t15 and let the trench grind it, or re-tier thresholds once after the re-pin so "pass" stays meaningful? (Recommend: keep t15, grind.)
3. **CI truth:** CI's settings scored 100% while local scores 30.8% on identical code+baselines — CI's swarm path likely has its own failure (crash/timeout recorded as 100). Worth one CI run on atlas/trench before Friday to confirm the metric pipeline isn't lying. Say go and I'll trigger it tomorrow night.
