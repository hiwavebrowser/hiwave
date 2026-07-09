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

## Night-3 scope (for the 01:07 run, 2026-07-08)
0. Port/merge any overnight Athena wins; if she approved PR #3 and/or PR #4 → merge (auto-merge policy).
1. Check the df4a334 CI run artifacts: is CI's settings a capture error (string now visible in metrics artifact) or a real render delta? Record the answer.
2. **Main target: grid `1fr` ignores the item's min-content floor** (Chrome sizes the track to min-content 1295.9px, RustKit gives naive 600px). Same family as card-grid (37.2%) — a fix likely moves sticky-scroll AND card-grid. Minimal repro first, shared-crate fix to a review branch + open PR (gh is now permitted).
3. Housekeeping: local atlas/trench carries b87ab7a (belongs to the review branch) — reset trench to origin before working, do not push that ref.

## Day-sprint session 1 (2026-07-08, Pete live: "improve hiwave as much as possible today on both systems")
0. PRs #3+#4 are MERGED into hiwave-macos master — rebase atlas/trench onto master, re-measure: the honest post-merge pass rate is the day's starting number. Record it.
1. Main target (carried): grid `1fr` min-content floor. Minimal repro → shared-crate fix → PR via gh immediately (Atlas reviews within minutes today, don't batch).
2. If Athena's step-11 Windows port PR arrives mid-session, note it in the digest — Atlas (live) reviews it, not you.
3. Digest after THIS session (not end of day). Cap ~2h as always; the day is a chain of capped sessions, not one long one.

## Day-sprint session 2 (2026-07-08, Atlas-approved pivot per session-1 digest)
1. **Main target: the gradient/background paint family** — 8 of 17 failures (gradients 22.8, gradient-no-radius 24.3, gradient-radius-only 21.2, gradient-backgrounds 24.0, gpu-gradient-regression 38.4, backgrounds 30.9, bg-solid 19.7, rounded-corners 26.4) sit 5–23pp over t15. Hunt ONE paint-side root cause (renderer/compositor shared crate → PR lane). A/B against Chrome on the simplest family member (bg-solid 19.7) first — smallest delta = cleanest signal.
2. Port back Athena's §9.4.11 stretch gating from hiwave-windows PR #5 (definite cross size wins over stretch) — macOS is less spec-faithful here today.
3. Ledger (not chased): inline-block margin-right dropped by inline layout; card-grid reclassified as flex-wrap (NOT grid family).
4. PATH is fixed seat-side (~/.cargo/bin now in the launchd PATH) — drop the shim if it conflicts.

## Day-sprint session 3 (2026-07-08, Pete "continue, Athena offline")
BASIS UPDATE: PRs #5+#6 merged to master under Pete's continue-directive — **committed pinned metric is now 46.2% (12/26)**, up from morning's 34.6%. Both flagged for Athena's post-hoc review on return.
Scope (text lane — macOS engine, no Windows collision while Athena offline):
1. **text-align never applied by inline layout** (ledgered session 2) — hits every text page. Root cause in rustkit-layout inline path, minimal repro vs Chrome, fix. Highest remaining leverage: touches the whole websuite.
2. **unstyled elements default to 16px instead of inheriting font-size** (ledgered) — same breadth. Fix at style/cascade time.
3. Port-back Athena's §9.4.11 stretch gating (her PR #5 now MERGED, safe to port): definite cross size wins over align-items:stretch — macOS flex.rs is less spec-faithful here.
4. bg-solid sits at 15.20 (0.2pp from pass) — item 1 or 2 likely flips it. Re-measure at session end; report new pass count.
Shared-crate fixes still go to PRs (queue for Athena's review; Pete may merge proven ones). Cap ~2h. Aleph-first.

## Day-sprint session 4 (2026-07-08, Athena offline, Aleph grant now fixed)
PRE-FLIGHT: reset hiwave-macos submodule to origin/atlas/trench (session 3 left it on a PR branch); inspect+drop the stale `session-3 pre-work` stash if it's just the 16k-line results re-measure. USE ALEPH — aleph_search/resolve/expand are now permitted (verify with a quick aleph_search before falling back to grep).
Scope (paint/UA-default lane — text-align lane is exhausted; line-box model is a Friday architectural item, NOT a capped-session fix):
1. **bg-solid residual = h1 UA-default line-height family** (session 2+3 both fingered it; bg-solid sits 15.20, 0.2pp from pass). Audit the UA default stylesheet for heading line-height/margins vs Chrome's; a correct h1 line-height likely flips bg-solid to 13/26 AND helps every heading page.
2. **backgrounds 30.9** (untouched, different root cause than the gradient family already fixed) — A/B vs Chrome, root-cause, shared-crate PR.
3. **pseudo-classes 23.3** if 1+2 land early.
Shared-crate fixes → PR (Pete merges proven ones while Athena offline). Cap ~2h.

## Day-sprint session 5 (2026-07-08 evening, Atlas-approved per digest decisions)
PRE-FLIGHT: add `fastrender/` to hiwave-macos `.alephignore` + rebuild index — Aleph must steer to rustkit-* (the metric engine), not fastrender. Cost session 4 ~40min.
1. **Main target: external stylesheet loading in parity-capture** (approved decision 1) — resolve `<link rel=stylesheet>` against the HTML file's base URL in the headless path (load_html+render_view). This unblocks the entire micro-suite: rustkit currently renders reset-less vs Chrome-with-reset. PR #8 (line-height inheritance, MERGED) is the prerequisite already in place. Measure honestly: the reset also brings font-family — expect some cases to move backward as font mismatches surface; report both directions.
2. Full-suite re-measure after; report new pass count vs the 12/26 basis.
3. parity-capture is seat-local tooling (not shared crate) — commit direct to atlas/trench; any rustkit-* spillover goes to PR.

## Day-sprint session 6 (2026-07-08 late, decisions 2+3 approved as recommended)
Trendline rule: annotate everything before session 5 as "pre-determinism" — the campaign metric only moves forward; no historical re-measures.
BASIS: 57.7% (15/26), deterministic (two runs identical). PRs #5-#9 + capture-CSS all on hiwave-macos master; hub pin current. Session-5 scope is DONE — do not redo external stylesheets.
1. Cheap flips first: combinators 16.3 (needs 1.3pp), images-intrinsic 12.2 vs t10 (needs 2.2pp) — small, real gaps; a pass is a pass.
2. Then the real dig: gpu-gradient-regression 38.6 — worst non-paint-known case; A/B vs Chrome, root-cause, PR lane for shared crates.
3. If time remains: css-selectors 29.8 (keeps the selector/cascade lane hot).
Cap ~2h. Aleph-first (index excludes fastrender). Digest as always.

## Session 9 scope (2026-07-09, first run at the new 3h cap)
BASIS: 69.2% (18/26) — PRs #12 (inline-flex atomic) + #13 (flex-item intrinsic width) MERGED to master. Aleph-first is enforced now; hiwave-web added to hub .alephignore (ledger d).
Ledger, worst-first (all real renders): sticky-scroll 48.2 (grid 1fr min-content, known), card-grid 32.6 (flex-wrap, DIFFERENT root cause — untouched by intrinsic-width), css-selectors ~27.6, shelf ~25.6, backgrounds ~25.5, gpu-gradient-regression 18.2 (now bounded — real gradient render + heading text), image-gallery 21.6 (network-image loading, seat-tooling).
1. **card-grid 32.6 (flex-wrap)** — #2 worst, its own root cause, twice-noted as unmoved. A/B vs Chrome, shared-crate fix → PR.
2. **gpu-gradient-regression 18.2** — now that flex-width is fixed, the residual is finally real gradient parity; dig into the actual gradient renderer.
3. Cap ~3h now — you have room for one real dig plus a second target. Aleph-first (aleph_search/resolve, not grep).

## Session 10 scope — REVISED AGAIN 2026-07-09 evening (phases 1 AND 2 done live)
Live session with Pete completed BOTH phases; PRs #15 + #16 MERGED to master.
**Committed basis: 19/26 (73.1%), avg diff 13.6 — campaign high.** Phase 2 root
cause: estimate_min_content_width had no Text arm (text contributed 0px to every
intrinsic width in the engine); fixed + flex-basis:auto now max-content per spec.
Remaining ledger, worst-first: sticky-scroll 48.1 (t25), css-selectors 30.4 (t15,
UNMOVED all campaign), backgrounds 27.7, shelf 26.0 (needs text-overflow:
ellipsis + overflow clip), image-gallery 21.6 (t10, network-image tooling),
settings 19.2 (closest flip, 4.2pp), gpu-gradient-regression 18.2.
Tonight (pick in order, cap ~3h):
1. **Line-box phase 3: mixed-inline content** — multiple inline children
   (text + <code>/<b>/<span>) currently wrap per-NODE, each starting a new
   vertical stack, not per shared line box. css-selectors (30.4, never moved)
   is full of exactly this; article-typography benefits too. Design note in
   PLAN: build line boxes at the block level across inline children, reusing
   phase-1's TextLine fragments per child.
2. If phase 3 stalls early: settings 19.2 flip (4.2pp) — likely form-control
   or heading metrics, A/B the diff heatmap first.
3. Ledger, do not chase: intrinsic_cache test flake (parallelism, pre-exists).

## Session 10 scope — REVISED 2026-07-09 evening (phase 1 DONE live with Pete)
Atlas completed line-box phase 1 in the live session: **PR #15** (wrap block text
into line boxes + css-text-3 §5.2 overflow of unbreakable words). Measured
honestly: 18/26 → 17/26 BUT avg diff 14.5 → 13.9; card-grid 32.6 → 10.2 (PASS),
bg-solid 6.7, combinators 6.0; gradient-backgrounds/gradient-no-radius lost
their passes by 0.3/1.1pp because wrapping exposes under-computed shrink-to-fit
widths (pill labels, shelf header) that no-wrap used to hide. Tonight:
0. Merge queue: if PR #15 is merged by session start, rebase and re-measure —
   the committed basis is whatever master says, no pre-merge numbers.
1. **Phase 2 target: inline-block / shrink-to-fit width under-measurement.**
   Chrome fits "135deg Purple" (gradient-backgrounds pills) and "Command
   Palette" (shelf header) on one line; RustKit sizes those containers
   narrower than their text, so wrapped text breaks where Chrome doesn't.
   Minimal repro: one inline-block span with padding + short text, A/B width
   vs Chrome layout-rects. Fix likely recovers BOTH gradient passes (they sit
   0.3pp / 1.1pp over) and moves shelf.
2. If time remains: shelf needs `text-overflow: ellipsis` + overflow clipping
   to pass — scope it (implement only if small).
3. Ledger: intrinsic_cache tests are parallelism-flaky on clean master —
   seat-tooling item, do not chase mid-session.
Shared-crate PRs as usual. Cap ~3h.

## Session 10 scope (2026-07-09, Pete-directed: LINE-BOX LANE opens)
Pete (2026-07-09): the goal is real websites rendering chrome-like — that names text
wrapping (session 9's engine-wide gap: `layout_text` measures each text node as ONE
run; `TextShaper::wrap_text` has zero callers) as the campaign's main lane. This is
session 1 of a multi-session lane; do NOT try to finish it in one cap.
0. Merge queue first, as always (any approved cross-seat PRs; Athena is deprioritized
   per Pete — Windows ports wait, discoveries still go to the exchange).
1. **Line-box phase 1 — wrap plain block text.** Wire `TextShaper::wrap_text` into the
   inline path of rustkit-layout `layout_text` for the simplest case: a block
   container whose inline content is a single text run. Available width = containing
   block content width. Each returned line = one line box advancing by line-height.
   Spec anchors: CSS2 §9.4.2 (inline formatting), css-text-3 §5 (line breaking).
   Minimal repro FIRST (one <p> with long text, A/B vs Chrome), then the wiring,
   behind rustkit-layout unit tests. Do not touch inline-block/mixed-inline yet —
   that is phase 2+.
2. Re-measure the full suite after. EXPECT NON-MONOTONIC MOVEMENT: pages that
   accidentally benefited from nowrap layout may regress while text pages jump.
   Report both directions honestly; the lane is judged over its whole arc, not night 1.
3. Instrument note: `visual_test_runner.sh` now pixel-diffs vs chrome-148 with
   parity thresholds (honest 7/13, was fake "13/13") — `--no-window` for headless.
   parity_test.py remains the campaign metric; the runner must agree with it.
Shared-crate (rustkit-layout/text) changes → PR lane; Pete may merge proven ones
while Athena is deprioritized (flag for her post-hoc review). Cap ~3h.

## Session 10 scope — FINAL (2026-07-09 ~18:00, phases 1-3 all done live; PRs #15/#16/#17 merged)
Committed basis: **19/26 (73.1%), avg 13.8.** css-selectors moved for the first
time all campaign (30.4 → 26.7 — inline-level boxes now share line boxes).
Tonight's single target: **LINE-BOX PHASE 4 — css-text §4 whitespace processing.**
Root cause located and documented: rustkit-engine lib.rs ~1434 drops
whitespace-only text nodes entirely and trim()s kept text, so runs that now
correctly share a line sit flush (buttons jammed, byline separators tight).
1. At box build: between two INLINE-LEVEL kept siblings, materialize a
   collapsed single-space Text(" ") node; never between block-level siblings
   (that would add phantom rows — the reason the old code dropped them).
2. Keep one leading/trailing collapsed space on kept text nodes whose raw text
   had edge whitespace AND whose neighbor is inline-level (\"By <span>\" case);
   line-start spaces should not paint (strip at line assembly, not box build).
3. Re-measure. EXPECTED RECOVERIES: article-typography 15.6→~13, form-controls
   10.2→~9, images-intrinsic 8.9→~6, css-selectors pushes below 25.
4. If time remains: settings 19.2 flip (4.2pp) — A/B the heatmap first.
Ledger unchanged: intrinsic_cache flake (do not chase); shelf needs
text-overflow:ellipsis; sticky-scroll is grid-min-content + scroll-pinning.
Shared-crate PRs; cap ~3h.

## Session 10 scope — FINAL v2 (2026-07-09 late evening; phases 1-4 ALL merged: PRs #15-#18)
Committed basis: **19/26 (73.1%), avg diff 13.5 — campaign-best average.**
CI NOTE: master's metrics-history collector had failed on EVERY master push of
the campaign (dirty-tree checkout cascade) — fixed (ca5c807) and verified green;
the trendline branch finally collects. Treat pre-tonight trendline as absent.
Tonight, closest flips first (the lane's architecture work is banked; tonight is
harvest):
1. **gpu-gradient-regression 18.2 (3.2pp from t15)** — ledgered as line-box/
   strut family, NOT gradients (pixel A/B receipt committed: gpu-row5-compare
   .png). Phases 1-4 may have moved the substrate under it; re-A/B FIRST, then
   fix the residual (likely heading strut/half-leading).
2. **settings 19.2 (4.2pp)** — A/B the heatmap before digging; form-control
   metrics or heading line-height are the standing suspects.
3. Stretch: **line-box phase 5 — IFC text splitting**: a text run that does NOT
   fit the remaining line space currently drops to its own block row; Chrome
   fills the remainder then wraps. Needs first-line-width support in wrap_text
   (wrap against remaining width for line 1, full width after). article-
   typography and css-selectors both gain.
Ledger: shelf=text-overflow:ellipsis; sticky-scroll=grid-min-content+scroll
pinning; image-gallery=network image tooling (t10). intrinsic_cache flake: NOT
tonight. Shared-crate PRs; cap ~3h.
