# Trench Baseline — macOS seat (Atlas)
Recorded 2026-07-07. Source: live CI metrics (github-actions, updated 2026-07-07 12:25 UTC) + metrics/parity_results.json (10:53 UTC run).

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
