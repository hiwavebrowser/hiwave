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
| D0 | Image pipeline: validate #443 paints on live pages; SVG background consumer (drop the .svg skip in discover_background_images); post-mutation discovery+paint | Z lane | Prometheus | Cursor | open | all-site A/B per PR |
| D1 | L0 (docs/LAYOUT_CONSTRAINTS_FRAGMENTS_2026-09-30.md §4-§6), then S1 fallback-run boundaries | Z lane | Prometheus | Cursor | open | starts after D0's SVG PR lands |
| C0 | Module host: Boa ModuleLoader wired to the document; inline+external type=module; URL resolution; graph; no double eval; load/error events | Athena | Prometheus | Cursor (Pollux backup) | open | fixture suite green on 3 OSes; github module scripts run; next blocker recorded |
| C1 | Fetch/XHR bindings: reopen archive/xhr-bindings; fetch/Response/Headers + XHR state/events on FetchPolicy; promise jobs + callbacks through the engine pump | Athena (integrator), Talos inside rustkit-net/http | Prometheus; Talos on boundary | Cursor (Pollux backup) | open | module+fetch app fixture; §7 deny matrix passes |
| C2 | Module loading policy: script destination, MIME + CORS checks for module fetches through transport + shield | Talos | Prometheus | Cursor | open | deny tests: wrong MIME, cross-origin w/o CORS, private address |
| M0 | Scorer v2: text geometry by region + resource presence on archived frames; calibrated on known good/bad set; published BESIDE the old board | Pollux | Argos | n/a | open | separates google logo / missing art / blank shell / small splash |
| N0 | Nightly refresh, one engine sync per day, no feature work | Athena (Win), Talos (Linux) | Pollux / Argos | collect-metrics | open | within 1.0 pt per case of macOS; frames archived |
| F0 | Fleet ops: lane job, lease, receipt.py, archive hygiene, Day-7 promotion | Atlas | Argos (promotion) | n/a | open | daily digest |

## Closure gates (B0, C0, C1, C2, D0-SVG, D1-L0), on top of the land law
1. Reduced failing case committed before the fix, green after.
2. receipt.py output in the PR body.
3. 26-case campaign at the candidate SHA (identical or every mover explained); all-site A/B for paint/fetch/script changes.
4. C1/C2: XHR_FETCH_DESIGN §7 deny matrix passes; no connection before the vet.
5. Independent re-run of the acceptance claim on the merged binary by a non-author seat (Pollux macOS, Argos Linux), posted on the exchange.

## Rules
- Thresholds, baselines and scorer do not move this week (A3). Scorer v2 publishes beside the old board.
- Stop rule: two consecutive sessions on one package with no landed receipt -> state=blocked + one-line decision packet in digest-z.md; the lane takes the next package.
- Pete decides only: A2 (tree-reuse), A3 (any threshold change), A4 (reset spend, Day 6), A5 (ship/hold, Day 7). Silence for 24h = Atlas's recommendation.
- Builds: every cargo command via rs-cargo.py (lease + sccache). --profile parity for pixels, --release for timing. One warm worktree per package.
- No pings 17:00-19:30 ET. One noon digest per day.

## Approvals log
- A1 plan: approved 2026-10-02 (Pete).
