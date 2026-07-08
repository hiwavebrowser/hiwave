# Trench Baseline — macOS seat (Atlas)
Recorded 2026-07-07. Source: live CI metrics (github-actions, updated 2026-07-07 12:25 UTC) + metrics/parity_results.json (10:53 UTC run).

## RE-PINNED 2026-07-08 (night 1, Phase 0 exit)
- **Unified pass rate vs pinned Chrome for Testing 148.0.7778.216: 9/26 (34.6%)**, avg diff 19.3% — this replaces the 46.2% chrome-120 number below as the campaign metric. The 120-era baselines were flattering (rounded-corners 9.5→26.4, gradients 9.6→22.8 under Chrome 148's own rendering changes); Athena saw the same drop shape on Windows.
- Baseline tree: `hiwave-macos:baselines/chrome-148/` (26 cases, exact binary in metadata.json), captured with ANGLE swiftshader + PARITY_CHROME_PATH pin. Instrument commits: hiwave-macos@5d14baf, @fc7531d on `atlas/trench`.
- Instrumentation debt PAID: gpu-gradient-regression baseline captured (was missing entirely from chrome-120 — its three 100%-diff entries were fake). It now measures a real 32.8% diff.
- `settings` 100%-in-CI mystery resolved: locally it's a 30.8% diff (flat-background frame), root-caused to a rustkit-layout flex bug — all block children of a flex item stack at the item's bottom edge, pushing content below the viewport. Fix on PR hiwavebrowser/hiwave-macos#3 (shared crate, awaiting Athena's review): settings 30.8→17.9. Athena's width=0.0 lead does NOT reproduce on macOS (layout exports 272/272 sized boxes) — her symptom is a different exporter view, possibly same family.

## Headline numbers (CI truth, not January folklore)
- **Visual parity: 80.2%** (builtins 87.45%, websuite 78.47%)
- **Pass rate: 46.2%** (12/26 unified; 36/72 in the 3-viewport detailed run)
- Reference: **chrome-120 committed baselines** (CI path `baselines/chrome-120/`) — CAMPAIGN RE-PIN to Chrome 148.0.7778.216 pending (see decisions)
- Windows: **absent from CI entirely** (`platforms_found: ["macos"]`) — the parity-windows badge is decorative. Athena's Phase 0 wires it in.

## Decomposition (72 detailed cases = 24 pages × 3 viewports)
- Instrumentation debt: **3 cases** fail only because the chrome-120 baseline PNG is missing (e.g. `gpu-gradient-regression` scored 100% diff with no image to compare). Cheap fix, free metric truth.
- Real failures: 33 cases (11 unique pages). Ranked worst-first:

| diff % | page | read |
|-------:|------|------|
| 100.0 | settings | total failure — renders blank/wrong; bug hunt, not pixel grind. Likely one root cause. |
| 50.4 | sticky-scroll | position:sticky |
| 35.9 | card-grid | grid layout |
| 29.8 | css-selectors | selector/cascade |
| … | (full ledger from parity_results.json) | |

**Note vs January:** the "59% of diffs are text metrics" claim does NOT describe today's failure profile — the top of the ledger is feature/layout failures, not glyph deltas. The campaign metric follows today's data, not January's memory.

## Night-1 scope (Phase 0 completion, capped ~2h)
0. **Apply Athena's portable fixes FIRST (from her Windows Phase 0, 2026-07-08 00:08Z):**
   - Use `--use-angle=swiftshader`, NOT `--use-gl=swiftshader` — the latter hard-breaks Chrome 148 screenshot capture ("Unable to capture screenshot").
   - Capture with **Chrome for Testing 148.0.7778.216** (via `@puppeteer/browsers`), not system Chrome — system Chrome drifts (hers already hit 149). Set `PARITY_CHROME_PATH` in deterministic.mjs. CfT is the canonical capture binary on both seats.
   - Her `capture_all_baselines.mjs` (hiwave-windows@b28d663) regenerates a baseline tree from reference structure+viewports — port/reuse rather than rewrite.
1. Regenerate the 3 missing baselines; re-pin baseline set to Chrome for Testing 148.0.7778.216 (capture locally, commit, update CI path chrome-120 → chrome-148).
2. Diagnose (not necessarily fix) the `settings` 100% failure — root cause in writing. **Cross-check Athena's lead first: RustKit layout export emits width=0.0 on every box (the January single-column bug) — her four ~99% builtins failures are likely my settings failure wearing a different OS.** If it reproduces on macOS, that's ONE shared-crate root cause under two platform ledgers — diagnosis goes in the digest, fix goes through cross-seat PR review.
3. Aleph: vendor-mask + index rebuild so nightly agents stop paying the 42%-vendor token tax.

## Cross-seat context (2026-07-08)
Windows baseline: pass 1/12 (8.3%) @ t15, mean diff 65.5% (~34.5% parity) vs pinned CfT 148. Bimodal: static-web healthy (text is Windows' BEST bucket — Jan's "59% text" refuted on both seats), builtins + paint bucket dead. Windows is the far-behind seat; expect shared-crate fixes to move it disproportionately.

## Metric pinned for Phase 2
**Unified pass rate** (threshold 15%, pinned-Chrome 148) — currently **46.2%**. Chosen over "visual parity %" because pass-rate moves page-by-page (feelable motion, one page = one win) while average parity can be gamed by polishing already-passing pages.

## Night-2 scope (2026-07-08, Pete-authorized same evening: "the night is young")
0. Port Athena's `.alephignore` vendor-mask approach (hiwave-windows@b692647 — her deps/ 7.9GB evaded the default mask; check macOS equivalents), then rebuild the hiwave-macos Aleph index. Carried from night 1.
1. If Athena has approved PR hiwave-macos#3 → merge it (auto-merge on cross-seat approval is now policy). If she reports it moves her builtins, note the delta in the digest.
2. Trigger a CI run on `atlas/trench` (gh workflow run / push-triggered) — audit the settings 100%-vs-30.8% CI/local discrepancy. If CI's capture path records crashes as 100s, root-cause it in writing (instrumentation debt is metric debt).
3. Next ledger target: `sticky-scroll` (50.4%) — root cause position:sticky. Same discipline as settings: minimal repro vs Chrome, shared-crate changes go to PR (auto-merge on Athena's approval).
4. Digest as always. Cap ~2h.

## Night-3 scope (set 2026-07-08, night-2 exit)
0. Port/merge queue first: if Athena approved PR #3 and/or `atlas/fix-block-auto-margins`, merge (auto-merge on approval is policy) and re-measure — settings and every centered page move on merge day.
1. **Grid `1fr` auto-minimum (rustkit-layout grid.rs):** track sizing must respect grid items' min-content contribution (`minmax(auto, 1fr)`). Chrome sizes sticky-scroll's `main` to 1295.9px (nowrap row overflows the container, per spec); RustKit gives 600px. Drives sticky-scroll (49.7%, worst case) AND card-grid (37.2%, #2). Minimal repro → fix → shared-crate review branch.
2. Check noon CI results (runs on 3bea8a1/6edda65/df4a334): with the instrumentation fix, CI's settings score is now attributable (error string in artifact). If CI still disagrees with local on real renders, root-cause the capture environment next.
3. Night-1/2 numbers were measured with un-merged PR #3 in-tree (pass count unaffected; avg diff −0.5pp). Once the merge queue clears, metric basis = committed code only.
