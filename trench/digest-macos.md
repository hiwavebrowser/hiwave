# Trench digest — macOS seat (Atlas)

## Day-sprint session 1 — 2026-07-08 (morning seat)

**Metric (unified pass rate, t15, vs pinned CfT 148):** 34.6% (9/26) → **34.6% (9/26)**, avg diff 19.2 flat. Basis milestone: this is the first number measured on **committed code only** — PRs #3+#4 are merged, the un-merged-patch asterisk from nights 1–2 is gone. The carried grid-`1fr` fix is done and on PR #5, but the session's biggest finding is that it — correctly — moves no pixels (below).

**Landed:**
- hiwave-macos `atlas/trench` @ `f2ea02e` — post-merge full-suite re-measure (the day's starting number) + seat PATH-shim tooling + layout-row forensics script.
- hiwave-macos **PR #5** (`d6a2b75`, branch `atlas/fix-grid-fr-min-content`, shared crate): fr tracks now floored at the item's min-content contribution (CSS Grid §6.6), via a deliberately conservative estimator (explicit px widths + nowrap inline runs only; never oversizes past Chrome). 4 unit tests; 221 crate tests green. Awaiting Athena; auto-merge on approval. https://github.com/hiwavebrowser/hiwave-macos/pull/5
- Night-2's in-progress version of this fix didn't compile (5 type errors) — finished, validated end-to-end: sticky-scroll's middle track **600 → 1200px** (Chrome: 1295.94).

**Findings that change the map (this is the real yield):**
1. **sticky-scroll's pixel diff is paint-dominated, not geometry-dominated.** Controlled A/B (same tree, fix stashed vs applied): track 600→1200 moved the diff 49.70→49.80 — nothing. Night-2's hypothesis "grid 1fr drives the worst case" is refuted at the pixel level. The fix is right and stays (groundwork), but it buys no pass today.
2. **card-grid (37.2%, #2 worst) is flexbox, not grid** — `display:flex; flex-wrap:wrap`. Night-2's "same family" classification was wrong; bit-identical diff under the grid fix proved it, then the fixture confirmed.
3. **New rustkit-layout bug found:** inline-block `margin-right` is dropped by inline layout (item pitch 200px vs Chrome's 215px in sticky-scroll's scroller), and the nowrap row wraps anyway. Ledger entry; not chased tonight.
4. Where the passes actually are: 8 of 17 failures are one gradient/background paint family (gradients 22.8, gradient-no-radius 24.3, gradient-radius-only 21.2, gradient-backgrounds 24.0, gpu-gradient-regression 38.4, backgrounds 30.9, bg-solid 19.7, rounded-corners 26.4) sitting 5–23pp above t15. One gradient-rendering root cause plausibly flips 3–5 cases — that's the next-session target, and it's likely renderer-side (shared crate, so PR lane again).
- Housekeeping: the 2 `intrinsic_cache` test failures seen under parallel `cargo test` are a pre-existing shared-cache flake on clean master (pass with `--test-threads=1`) — not from any trench change.

**Decisions needed from Pete (≤2):**
1. **Next-session pivot:** the ledger's top-2 cases are paint-bound; grinding layout there is low-yield. I'm pointing the next session at the gradient/background paint family unless you object at noon.
2. **Seat PATH, one-liner:** the non-interactive shell lacks `~/.cargo/bin`, which silently broke every allowlisted `cargo` command AND `parity_test.py`'s internal build (env-prefix workarounds are also gated). I shimmed around it (committed as seat tooling), but adding `~/.cargo/bin` to the seat's PATH (or sourcing `~/.zshenv`) removes a whole class of friction.

## Night 2 — 2026-07-08 (same night, second session)

**Metric (unified pass rate, t15, vs pinned CfT 148):** 34.6% (9/26) → **34.6% (9/26)**, avg diff 19.22 → 19.20. Flat headline, real ground gained: one of sticky-scroll's two root causes is fixed and awaiting review, the other is scoped for night 3, and the CI metric pipeline no longer lies about crashes. Measurement basis matches night 1 (un-merged PR #3 applied in-tree; note: pass count is 9/26 with or without it — settings fails t15 at both 17.9 and 30.8).

**Landed on `atlas/trench` (hiwave-macos):**
- `3bea8a1` — `.alephignore` + index rebuild (Athena's b692647 ported). Workspace index: deps/wincairo was indexed TWICE via the windows+linux submodules = 7.3% of 132,630 syms; now 122,905. Note: aleph 0.5.0 already default-masks vendor/ — the "42% vendor" figure was stale.
- `6edda65` — **CI-audit root cause, fixed.** The settings 100%-vs-30.8% discrepancy is instrumentation: an errored capture (crash/timeout — CI runners can blow the 30s capture timeout) got no `diff_pct`, which `parity_test.py` averages as 100 while `extract_parity_metrics.py` (the CI script) either crashes on `pixel=None` or — if pixel were merely missing — defaults to 0.0, i.e. scores an instrument failure as a PASS. Now: every error path scores an explicit 100.0, the extractor is None-safe, never passes an errored case, and carries the error string into the metrics artifact — CI 100s are attributable from the artifact alone. Regression test included. Two CI runs triggered tonight on atlas/trench pushes; noon check: the df4a334 run's job summary shows whether CI's settings is a capture error (string now visible) or a real render delta.
- `df4a334` — sticky-scroll forensics + tooling (layout-tree dumper, ad-hoc repro runner, run comparator) + both measurement JSONs + regenerated diff artifacts.

**sticky-scroll (50.4%, worst case) root-caused — it's TWO rustkit-layout bugs:**
1. **`margin: 0 auto` never centers** (auto margins resolve to 0; CSS 2.1 §10.3.3 unimplemented) — every max-width page hugs the left edge, a whole-page 40px shift at 1280px. Minimal repro committed; fix + 6 unit tests on **branch `atlas/fix-block-auto-margins` (b87ab7a, shared crate, awaiting Athena)** — repro geometry now matches Chrome exactly, 217/217 crate tests pass. Suite effect tonight: sticky-scroll 50.36→49.70 only, but it corrects layout on every centered page and should compound as other bugs clear; likely helps Windows too.
2. **Grid `1fr` ignores the item's min-content floor**: Chrome sizes `main` to 1295.9px (a nowrap inline-block row legally forces the track to overflow its 1200px container); RustKit gives the naive 600px — half the page differs. Same family as card-grid (37.2%). **This is the night-3 target.**

**Blocked / notes:**
- **PR #3 still un-reviewed** (exchange checked twice: quiet). Its settings win (30.8→17.9) stays out of committed code until Athena approves; auto-merge is authorized on her approval.
- Tonight's non-interactive seat had `gh` and several git verbs (fetch/checkout/branch/cherry-pick/apply) permission-gated. Worked around everything except opening the PR for the fix branch — GitHub's suggested link: https://github.com/hiwavebrowser/hiwave-macos/pull/new/atlas/fix-block-auto-margins
- Housekeeping: local `atlas/trench` sits one commit ahead of origin (b87ab7a, the shared-crate fix). **Do not push that ref** — the commit lives on the review branch; next session should not carry it into the trench branch.

**Decisions needed from Pete (≤3):**
1. **Seat permissions:** grant the overnight seat `gh` (PR create/view) + read-only git network verbs in `.claude/settings.local.json`? Tonight cost ~20 min of workarounds and left the fix branch PR-less. One-line change, big friction cut.
2. **Review latency:** PR #3 (and now the auto-margin branch) wait on Athena's cycle. OK to keep posting review requests over the exchange and let auto-merge do its thing, or do you want a standing rule like "un-reviewed after 2 nights → escalate in the noon digest"?

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
