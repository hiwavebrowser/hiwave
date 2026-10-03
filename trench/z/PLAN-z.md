# Z phase plan — the only source of tasks (2026-10-03 to 2026-10-09)

Approved by Pete 2026-10-02 (artifact "HiWave Z Phase Plan"). A session or seat takes work ONLY from this file. A PR for an unlisted package is closed, not reviewed.

end_date: 2026-10-09
exit_metric: github.com starts end-to-end (modules + fetch + one interaction, 3 quiet captures) AND CSS backgrounds (raster + SVG) paint on the live board AND macOS quiet board >= 34/60

## Finish line (Day 7, quiet board)
1. github.com starts up end to end: module scripts load and run, API calls go through fetch under FetchPolicy, real content renders, one interaction (open the search box) works. Three quiet captures.
2. CSS background images paint on the live board, raster and SVG, at the right size and position.
3. macOS quiet board >= 34/60; Windows and Linux within 2 points on the same day's engine.
4. No regressions: 26/26 within 1.0 pt per case of the 2026-10-02 receipt; develop compiles on every push; no security gate weakened.

## Packages (state: open | in-progress | blocked | done)
Priority order for the Z lane: D0 -> D1 -> B0. Seats own the rest.

| id | package | owner | R1 | R2 | state | note |
|---|---|---|---|---|---|---|
| B0 | Cascade decision: fix ab2.py build-count exclusion + share_check explicit arms; one quiet profile at tip; tree-reuse decision packet (A2) | Z lane (ONE session) | Prometheus | Cursor | open | packet -> digest; legacy ratio republished; absolute ms budget per site |
| D0 | Image pipeline: validate #443 paints on live pages; SVG background consumer (drop the .svg skip in discover_background_images); post-mutation discovery+paint | Z lane | Prometheus | Cursor | in-progress | all-site A/B per PR; D0-SVG landed #454 (dc616df); data: SVG + viewBox-less SVG images landed #462 (7a757a7); SVG gradient paint servers landed #463 (382efbe); image Accept without AVIF landed #470 (a238ae8); next: post-mutation discovery, fix 3524172 on atlas/z-post-mutation-images (no PR: yahoo A/B mover unexplained, see digest 2026-10-03 04:55) |
| D1 | L0 (docs/LAYOUT_CONSTRAINTS_FRAGMENTS_2026-09-30.md §4-§6), then S1 fallback-run boundaries | Z lane | Prometheus | Cursor | open | starts after D0's SVG PR lands |
| C0 | Module host: Boa ModuleLoader wired to the document; inline+external type=module; URL resolution; graph; no double eval; load/error events | Athena | Prometheus | Cursor (Pollux backup) | open | fixture suite green on 3 OSes; github module scripts run; next blocker recorded |
| C1 | Fetch/XHR bindings: reopen archive/xhr-bindings; fetch/Response/Headers + XHR state/events on FetchPolicy; promise jobs + callbacks through the engine pump | Athena (integrator), Talos inside rustkit-net/http | Prometheus; Talos on boundary | Cursor (Pollux backup) | open | module+fetch app fixture; §7 deny matrix passes |
| C2 | Module loading policy: script destination, MIME + CORS checks for module fetches through transport + shield | Talos | Prometheus | Cursor | open | deny tests: wrong MIME, cross-origin w/o CORS, private address |
| M0 | Scorer v2: text geometry by region + resource presence on archived frames; calibrated on known good/bad set; published BESIDE the old board | Pollux | Argos (Prometheus while Argos is silent) | n/a | open | separates google logo / missing art / blank shell / small splash |
| N0 | Nightly refresh, one engine sync per day, no feature work | Athena (Win), Talos (Linux) | Pollux / Argos | collect-metrics | open | within 1.0 pt per case of macOS; frames archived |
| F0 | Fleet ops: lane job, lease, receipt.py, archive hygiene, Day-7 promotion | Atlas | Argos (promotion) | n/a | open | daily digest |

## Next-phase queue (Pete, 2026-10-02 19:40: "if you get done with parts of the plan early, move onto the next phase")
When a seat or the lane finishes its packages and nothing above is open for it, it takes the first item below for its seat; Atlas re-prioritises here, Pete is not asked. Each item lands under the same closure gates.

| id | package | owner | note |
|---|---|---|---|
| Z2-C3 | Async modules: dynamic import(), import.meta.url, top-level await, import maps as the sites need | Athena | after C0 + C1 |
| Z2-C4 | Custom elements + Shadow DOM (the likely next first blocker on github/microsoft per the ledger) | Athena | ledger decides the order against C3 |
| Z2-C5 | Scheduler: promise jobs, timers, network callbacks, DOM mutation -> resource discovery -> repaint; cancellation on navigation | Athena, Talos on net | the signed design's bounded rounds become a real loop |
| Z2-D2 | Generated content as fragments: list markers, counters, ::first-letter | Z lane | after L0 |
| Z2-D3 | S1-S3 of the shaped-run contract: fallback-run boundaries, GradientText, cluster-aware breaking | Z lane | |
| Z2-D4 | Image pipeline tail: image-set(), <picture>, lazy loading, decode census on the 20 sites | Z lane | |
| Z2-B1 | Largest remaining cascade cost from the fresh profile; one profile-backed cut with equal-output A/B | Z lane | only after B0's packet; stop after two unproductive sessions |
| Z2-M1 | Matched-workload cascade measurement (Chrome trace vs RustKit phases, same pinned bytes) | Pollux | legacy ratio keeps publishing; replacement needs A3 |
| Z2-M2 | CSS declaration census, bounded to the top three buckets with owners | Pollux | |
| Z2-N1 | Second holdout site set (20 unseen sites) scored by both scorers | Pollux | guards against overfitting to the board |
| Z2-C3b | Vendor boa_parser 0.20.0 with the one-line upstream backport (boa-dev/boa #4593, `let of`) under third_party/, same layout as boa_gc; red-first test + 92-module parse receipt. Boa 0.22 upgrade stays out of Z | Athena | Atlas GO 2026-10-03 04:10; blocks Finish line 1 (github behaviors.js, landing-pages.js) |
| Z2-R1 | Status ladder on all three READMEs + umbrella: every feature row says implemented / integrated / exercised on real sites / compat-tested (no bare checkmarks); per-component status words; numbers refreshed from receipts with SHA | Atlas | Day 7, ships with the promotion PR (external review 2026-10-02: Windows checklist overstates) |
| Z2-M3 | 'interactive' column on the real-site board (one scripted interaction per site), alongside loads/readable/looks-right | Pollux | design only this phase; scoring change is an A3 call |

## Closure gates (B0, C0, C1, C2, D0-SVG, D1-L0), on top of the land law
1. Reduced failing case committed before the fix, green after.
2. receipt.py output in the PR body.
3. 26-case campaign at the candidate SHA (identical or every mover explained); all-site A/B for paint/fetch/script changes.
4. C1/C2: XHR_FETCH_DESIGN §7 deny matrix passes; no connection before the vet.
5. Independent re-run of the acceptance claim on the merged binary by a non-author seat that can run it: PROMETHEUS on the Mac for macOS closures (exact merged SHA, release build through the lease, own worktree); Pollux re-runs the Windows side on the next refresh; Argos (or Prometheus while Argos is silent) for Linux. Posted on the exchange.

## Receipt step for seat PRs (C0, C1, C2)
Athena and Talos cannot run macOS gates. For every seat PR to hiwave-macos that reaches R1 CLEAR, the Z lane runs a RECEIPT STEP on the Mac before its own package work: build the PR head with --profile parity, run the 26-case campaign and (for paint/fetch/script changes) the all-site A/B against develop, and post the result on the PR. The seat posts its own OS's parity and script-log A/B, labelled with the OS. Nobody claims a result they did not run.
- receipt.py: hiwave-macos scripts/receipt.py (plain Python, all OSes); until it lands, the same fields by hand.

## Rules
- Thresholds, baselines and scorer do not move this week (A3). Scorer v2 publishes beside the old board.
- Stop rule: two consecutive sessions on one package with no landed receipt -> state=blocked + one-line decision packet in digest-z.md; the lane takes the next package.
- Pete decides only: A2 (tree-reuse), A3 (any threshold change), A4 (reset spend, Day 6), A5 (ship/hold, Day 7). Silence for 24h = Atlas's recommendation.
- Builds: every cargo command via rs-cargo.py (lease + sccache). --profile parity for pixels, --release for timing. One warm worktree per package.
- No pings 17:00-19:30 ET. One noon digest per day.

## Approvals log
- A1 plan: approved 2026-10-02 (Pete).
