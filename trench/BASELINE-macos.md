# Trench Baseline — macOS seat (Atlas)
Recorded 2026-07-07. Source: live CI metrics (github-actions, updated 2026-07-07 12:25 UTC) + metrics/parity_results.json (10:53 UTC run).

## BASIS 2026-09-04 (night 42): develop `5b89ed8` (unchanged since n39; #174/#173/#176/#179/#182 still open)
Basis = n39's fresh clean-develop capture on this same commit (campaign 26/26
avg 4.0404, WPT Tier-1 24/26); no engine PR merged between n39 and n42.
- On `atlas/n42-flex-item-padding-column-basis` @ 0398324 (PR #184: an
  auto-width flex item's basis no longer adds its padding twice; a column
  container re-derives content-sized rows' heights after child layout —
  new step 11d — against its own definite height or max(content,
  min-height); 11b's column-item width is per-axis): **campaign 26/26,
  avg 4.0404 -> 3.6097** — flex-positioning 10.1126 -> 1.7460 (-8.37pp),
  gradient-no-radius -0.96, gradient-backgrounds -0.84, gradient-radius-only
  -0.60, shelf -0.58, chrome_rustkit -0.09, card-grid -0.04; new_tab 2.2600
  -> 2.5394 (+0.28: its `.container` is now at Chrome's x/w, y -6, and the
  develop-hardcoded four-column shortcuts grid — PR #182's lane — is fully
  in view instead of half below the fold); 17 of 26 byte-flat. **WPT 24/26
  flat.** Receipt: `.flex-item` 83.2/85.3/85.7 @ x 45/138.1/233.4 vs Chrome
  83.1/85.3/85.7 @ 45/138.1/233.4; nested rows y 491/548 = Chrome; repro
  flex-item-padding-column-basis.html five sections within 1px at the
  container/item level.
- Unclaimed after tonight: css-selectors 11.20 (board #2; first divergence
  `.direct-child` dy +4 at Chrome y 66, several ±4px block-flow terms),
  article-typography 7.46 (one span wraps to a different line — text).

## BASIS 2026-09-03 (night 41): develop `5b89ed8` (unchanged since n39; #174/#173/#176/#179 still open)
Basis = n39's fresh clean-develop capture on this same commit (campaign 26/26
avg 4.0404, WPT Tier-1 24/26); no engine PR merged between n39 and n41.
- On `atlas/n41-about-features-grid` @ 5822115 (PR #182: `repeat(auto-fit|
  auto-fill)` fits the container instead of a hardcoded 4; fr re-find after
  flooring (§12.7.1); content-box grid items keep padding inside the track):
  **campaign 26/26, avg 4.0404 -> 4.0336** — new_tab 2.2600 -> 2.0819
  (-0.18pp), 25 of 26 byte-flat; about byte-flat (its `.features` grids sit
  at y 800–1200, below the 800x600 fold). **WPT 24/26 flat.** Receipt: every
  card-4 `.feature` cell matches pinned Chrome (x 89 / 300.3 / 511.7, w 199.3,
  h 77); repro grid-auto-fit-minmax.html 4x150 -> 3x199.33.
- about's visible residual is now fully claimed by open PRs (#176 badge /
  sponsor width, #179 emoji line); nothing unclaimed remains in view.

## BASIS 2026-09-02 (night 40): develop `5b89ed8` (unchanged since n39; #174/#173/#176 still open)
Basis = n39's fresh clean-develop capture on this same commit (campaign 26/26
avg 4.0404, WPT Tier-1 24/26); no engine PR merged between n39 and n40.
- On `atlas/n40-fallback-face-line-height` @ de1ff02 (PR #179: a glyph the
  primary face lacks is shaped by its fallback face; `normal` line boxes
  unite the used faces, Blink model): **campaign 26/26, avg 4.0404 ->
  3.9294** — about 11.5860 -> 9.3213 (-2.26pp), image-gallery 5.6028 ->
  5.0638 (-0.54pp), card-grid -0.06, chrome_rustkit -0.05, sticky-scroll
  +0.03, 21 of 26 byte-flat. **WPT 24/26 flat.** Repro receipt: 12/12 row
  heights match pinned Chrome (16px emoji line 18 -> 26, button 42 -> 50,
  flex h2 23.55 -> 29, Arial 17.52 -> 18).
- about's two named visible terms (a.sponsor-btn dh -8, h2.card-title
  dh -5.4) were BOTH the emoji line — not inline-flex sizing. Remaining:
  #176's badge width (separate PR), features-grid dx +486 below the fold.

## BASIS 2026-09-01 (night 39): develop `5b89ed8` (#168 grid re-flow + #169 ellipsis merged in)
Fresh clean-develop capture reproduced before-numbers on the SAME tree/binary
path as the after-numbers (stash-rebuild-measure, no stale-binary risk):
- **Clean develop: campaign 26/26 PASS, avg 4.0404** (about 11.5860 is the top
  case), **WPT Tier-1 24/26 (92.3%)** — same two fails (lba001 AA column,
  empty-span-size-002 outline paint).
- On `atlas/n39-inline-badge-width` @ a274a16 (PR #176: atomic inlines with
  width:auto shrink to fit, CSS2 §10.3.9): **campaign 26/26, avg 4.0404 →
  3.9232** — about 11.5860 → 8.5404 (−3.05pp), new_tab −0.003pp, 24/26
  unchanged. **WPT 24/26 flat.** Badge receipt: border box 672.0 @ x=64 →
  106.6 @ x=346.7 vs Chrome 104.6 @ x=347.7.
- about's remaining visible-region residual after the fix (9 elements >2px):
  card-3 block sits dy −8 (h2.card-title dh −5.4 — heading line-height/margin
  term; its <p>s ride at −13.4) and a.sponsor-btn dh −8 (inline-flex vertical
  sizing: block path gives 42 vs Chrome 50). Below the fold only:
  div.features cells in cards 4/5 misplace by dx ≈ +486 (column placement).

## BASIS 2026-08-31 (night 38): develop `2be7d37` (unchanged; #167–#171 all open)
Basis = the n37 branch receipts (campaign 26/26 avg 3.9318, WPT 24/26 on
`atlas/n37-ws-line-box` @ 4b1c2f8) — n38 stacks on that branch since the n37
svg box is a hard dependency.
- On `atlas/n38-inline-svg-paint` @ d340072 (inline svg paint + three
  rustkit-svg parser fixes): **campaign 26/26, avg 3.9332** — shelf 5.2051 →
  5.2428 (the search icon paints as an outline in black, Chrome's currentColor
  is gray #6b7280), 25 of 26 byte-flat. **WPT Tier-1 24/26 (92.3%) unchanged.**
- The board carries exactly ONE inline svg (shelf). `images-intrinsic` is 14
  `<img>` elements — the seven-inline-svg file is `image-intrinsic-size/`,
  which is NOT in the registry. The lane's receipts are the pinned-Chrome
  repro A/B (`parity-tests/repro/inline-svg.html`): post-fix bboxes match
  Chrome within 1–2px on path/circle/polygon/text.

## BASIS 2026-08-30 (night 37): develop `2be7d37` (unchanged; #168/#169/#171 all open)
Basis = n36's byte-flat develop receipts (campaign 26/26 avg 4.0546, WPT 24/26);
no engine PR merged between n36 and n37.
- On `atlas/n37-ws-line-box` @ 4b1c2f8 (cross-node whitespace collapse + inline
  svg box): **campaign 26/26, avg 3.9318%** — images-intrinsic 8.4501 → 5.2510,
  shelf 5.1992 → 5.2051 (+9 px), settings +1 px, 23 of 26 byte-flat.
  **WPT Tier-1 24/26 (92.3%) unchanged**, same two fails (lba001 0.0173 AA
  column — tolerance decision; empty-span-size-002 0.0121 outline paint).
- Census correction: of 129 whitespace-only text boxes with height>0 across the
  26 captures, only 2 were phantom LINES (images-intrinsic, shelf); the rest are
  same-line spaces Chrome renders too. `scratch_n37/ws_rows.py` classifies.

## BASIS 2026-08-29 (night 36): develop `2be7d37` (#166 n35 overflow clip merged)
Fresh parity-capture on develop tip, reproduced bit-for-bit before any edit:
- **Campaign pixel board: 26/26 PASS, avg diff 4.0546%.**
- **WPT Tier-1: 24/26 (92.3%)** — pass 24 / fail 2 / skip 4 / error 0, n=30.
- On `atlas/n36-text-overflow-ellipsis` @ 803d62a (text-overflow: ellipsis + five
  inherited css-text properties reaching child elements): **both boards byte-flat**
  (0 of 26 moved, WPT 24/26). The meter does not see either change — no board
  case carries a truncated title, no Tier-1 case declares `text-overflow`; the
  receipts are 9 tests + a pixel A/B vs pinned Chrome on
  `parity-tests/repro/text-overflow-ellipsis.html`. Remaining Tier-1 fails
  unchanged: lba001 0.0173 (AA column — tolerance decision),
  empty-span-size-002 0.0121 (outline paint).

## BASIS 2026-08-28 (night 35): develop `6e5d944` (#164 n34 tail + #165 measure-side font chain)
Fresh parity-capture on develop tip, reproduced bit-for-bit before any edit:
- **Campaign pixel board: 26/26 PASS, avg diff 4.0586%.**
- **WPT Tier-1: 22/26 (84.6%)** — pass 22 / fail 4 / skip 4 / error 0, n=30.
- On PR #166 (`atlas/n35-overflow-clip` @ b363d76, not yet on develop): **24/26 (92.3%)**,
  campaign 26/26 avg 4.0546 (new_tab 2.3646 → 2.2600, 25 byte-flat). Remaining fails:
  lba001 0.0173 (AA column — tolerance decision), empty-span-size-002 0.0121 (outline paint).

## BASIS 2026-08-27 (night 34): develop `d223b31` (#162 W3 layout half + #163 web-font lane)
Fresh parity-capture on develop tip, reproduced bit-for-bit before any edit:
- **Campaign pixel board: 26/26 PASS, avg diff 4.06%** (was 5.3 at the n30 basis).
- **WPT Tier-1: 18/26 (69.2%)** — pass 18 / fail 8 / skip 4 / error 0, n=30. The
  `blocked_by` tag is attribution only since n33 (faces load; TTF/OTF).
- On PR #164 (`atlas/n34-wpt-tail` @ 29c267a, not yet on develop): **22/26 (84.6%)**,
  campaign 26/26 avg 4.059. Remaining fails: owa002/003 (square overflow clipping —
  never implemented, next lane), lba001 (AA-noise column — tolerance decision),
  empty-span-size-002 (outline paint).

## RE-BASED 2026-08-23 (night 30): develop is the measurement tree
Per the 2026-08-22 retarget (PLAN §Direction update), nightly boards measure
**hiwave-macos `develop` tip** until the develop→master promotion ceremony.
First develop basis, fresh parity-capture at `a23f8c2` (#153: E0 lane +
slice-0 + @font-face lane + docs, all in one tree):
- **Campaign pixel board: 26/26 PASS, avg diff 5.3%** (was 6.5 on master —
  improvement is the merged tree, zero regressions).
- **WPT Tier-1: 9/25 (36.0%)** — pass 9 / fail 16 / skip 4 / error 1, n=30.
  Matches n29's stack prediction. 12 fails still attributed `blocked_by:
  @font-face` — read as "declares a web font", not "fails because of it"
  (n29 over-claim finding stands; 5 passes remain SUSPECT).
- lba001/002 measure 0.30%/0.25% on develop (worse than the n29 stack's
  0.085%/0.068%) because #152's abspos margin-collapse + paint-order fixes
  are not yet on develop.
- Night-30 finding: the "#150 ink residual" is NOT a slice-0 bug — it is a
  global glyph-seating bug (raster bitmap padding never folded into the
  bearings; every glyph on every page painted (+2,+2)px off). Fix on
  `atlas/glyph-raster-bearing` (rustkit-text, shared-crate PR lane).

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

## Session 10 scope — FINAL v3 (2026-07-09 night; basis 20/26 = 76.9%, avg 13.4, ALL instruments clean)
Evening block 2 landed: PR #18 (whitespace collapsing), PR #19 (radial corner-
ellipse spec radii — gpu-gradient-regression 14.59 PASS; NOTE: taxonomy AND the
session-9 strut reclassification were both wrong, pixel-ramp arithmetic settled
it), CI metrics-history fixed (failed every master push all campaign — lie #7),
and a baseline-dimension audit (lie #8): settings/bg-solid/pseudo-classes were
captured at wrong viewports; regenerated; generate_baselines.py now follows
PARITY_BASELINE_SET. Settings' HONEST gap is 20.12 (5.1pp), not 19.2.
Remaining ledger (6 fails): sticky-scroll 48.1, backgrounds 27.3, css-selectors
26.7, shelf 25.9, image-gallery 21.6 (t10), settings 20.1.
Tonight:
1. **settings 20.1** — with the honest baseline, re-read the heatmap first
   (old read is void). Suspects: per-row vertical drift (cumulative), form
   control metrics.
2. **Line-box phase 5 — IFC text splitting** (css-selectors + article-typo
   both gain): text runs that don't fit remaining space should fill it then
   wrap; needs first-line-width support in wrap_text.
3. backgrounds 27.3 — never dug this campaign; A/B one background family
   member first.
Cap ~3h. Shared-crate PRs. Do NOT re-measure historical numbers.

## Session 12 scope (set 2026-07-10 session-11 exit)
Basis: committed 20/26 avg 13.3; **with PR #22 (inline-block line metrics) applied: 21/26 (80.8%), avg 11.9** — merge-queue first, as always: if #22 is merged, rebase + re-measure and that's the committed basis (expect 21/26).
Remaining fails @ #22: sticky-scroll 48.1 (t25), css-selectors 26.7, shelf 25.9, image-gallery 21.6 (t10), settings 20.2.
1. **settings 20.2 — root cause ALREADY REPRODUCED** (`parity-tests/repro/toggle-height.html`, hiwave-macos master 00bdde5): a flex ITEM with definite height gets sum-of-children height instead (26→40.4/67.2). Fix flex-item cross sizing in rustkit-layout (definite height must win); ALSO in the same repro: `position:absolute; inset:0` doesn't fill the parent (slider 4px wide). Second settings term: h1→p adjacent-sibling margin collapse (24 vs 16).
2. **css-selectors 26.7** — line-box residual; re-y-table it AT ITS CASE VIEWPORT (the baseline layout-rects.json is per-case; 900×1000 for backgrounds bit session 11 an hour).
3. Ledger, not chased: inline_strut_descent ≈7.7 vs Chrome 6.0 (+1.7px/row residual, backgrounds passes anyway); shelf=text-overflow:ellipsis; image-gallery=network tooling.
Cap ~3h. Shared-crate → PR lane. y_table.py is committed — use it.

## Session 10 addendum (2026-07-10 ~00:30 ET, live pre-work by Atlas — READ BEFORE DIGGING)
backgrounds (27.31) partially dug live; VERIFIED facts to build on, do not re-derive:
- STRIPES EXONERATED: repeating-linear-gradient 45deg renders with correct
  direction AND correct 28px period on the page itself (measured pixel
  transitions, both engines identical). Earlier "mirrored/denser stripes"
  reads were crop artifacts. Do NOT dig the gradient renderer for this case.
- Minimal repros confirmed clean: plain 45deg two-stop (corners verified
  red/blue), repeating with unpositioned first stop (28px period exact).
  Repro files in the session scratchpad if needed.
- REAL driver: VERTICAL DRIFT (~15-20px by section 2) — the checker band is
  striped, so any y-offset makes its whole area diff; drift multiplies into
  ~27%. UA h1 (bold/32px/21.44 margins) and p (16/16) defaults verified
  correct — the term is elsewhere: suspect margin-collapse vs Chrome,
  body/section defaults, or heading line-box height. METHOD: per-element
  y-table — RustKit layout.json vs Chrome layout-rects.json top-to-bottom,
  find the FIRST element whose y diverges, fix that term, iterate.
- Also on this page: layered backgrounds test (two comma-stacked
  linear-gradients on one element) — check whether background_layers renders
  ALL layers or only the legacy single gradient; if single, that's a paint
  gap on the lower sections.
- settings (20.24) remains the other scoped target; same y-table method
  applies (its rows are uniform-63.2px in Chrome, non-uniform in RustKit).

## n37 scope (Atlas, 2026-08-29 evening — supersedes the n36 digest's decision-2 default)
Unit: **whitespace-only text between block siblings must not produce a line box** (see the Atlas reply appended to digest-macos.md under night block 36 for the full receipt: images-intrinsic `' '` box y=68 h=24 after `<h1>`, 14/26 campaign captures carry such boxes, pseudo-classes 32 of them). Method: per-element y-table RustKit layout.json vs Chrome layout-rects.json (y_table.py), fix the block-flow term, re-table. WOFF/WOFF2 is NOT tonight (HARD NO as next unit; no board receipt). Boards measure develop tip; PR to develop via the review lane; honest last-run pin. Cap ~3h.

## n39 scope (Atlas, 2026-08-31 evening — conditional, read at lane start)
- **If #174 (n37-r2) — and #173 after its retarget — are MERGED into develop by lane start:** take n38 digest decision-2 option (a), **currentColor through the Image command** (rustkit-layout+engine; flips shelf's black icon to CSS color, fixes black icons on real pages), branching from develop tip.
- **If they are NOT merged (Argos smoke still pending): do NOT stack a third PR on unmerged branches.** Take the independent receipt-backed unit instead, from develop tip: **about `#versionBadge` is laid out full-width** — inline badge gets dw +567 vs Chrome 148 (`baselines/chrome-148/builtins/about/layout-rects.json` vs capture; likely the `_ => {}` UA fallback making unknown/inline elements Block, n37 forensics ledger). Gate-A dy/dw receipts + campaign board (about 11.59 is the top mover). PR to develop, review lane, honest pin. Cap ~3h.
