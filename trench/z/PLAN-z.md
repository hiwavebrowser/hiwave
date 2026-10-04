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
Priority order for the Z lane (amended 2026-10-03 by Atlas after Pete's live testing): I0 -> D0 -> D1 -> B0. Seats own the rest.

| id | package | owner | R1 | R2 | state | note |
|---|---|---|---|---|---|---|
| B0 | Cascade decision: fix ab2.py build-count exclusion + share_check explicit arms; one quiet profile at tip; tree-reuse decision packet (A2) | Z lane (ONE session) | Prometheus | Cursor | open | packet -> digest; legacy ratio republished; absolute ms budget per site |
| D0 | Image pipeline: validate #443 paints on live pages; SVG background consumer (drop the .svg skip in discover_background_images); post-mutation discovery+paint | Z lane | Prometheus | Cursor | done | all-site A/B per PR; D0-SVG landed #454 (dc616df); data: SVG + viewBox-less SVG images landed #462 (7a757a7); SVG gradient paint servers landed #463 (382efbe); image Accept without AVIF landed #470 (a238ae8); post-mutation image discovery landed #473 (877fa55); #443 validated against pinned Chrome, url-background percentage size + px position landed #474 (b7addf2); far-edge offsets + calc() positions landed #475 (1585ad1) |
| D1 | L0 (docs/LAYOUT_CONSTRAINTS_FRAGMENTS_2026-09-30.md §4-§6), then S1 fallback-run boundaries | Z lane | Prometheus | Cursor | open | starts after D0's SVG PR lands |
| C0 | Module host: Boa ModuleLoader wired to the document; inline+external type=module; URL resolution; graph; no double eval; load/error events | Athena | Prometheus | Cursor (Pollux backup) | done (#451,#452) | fixture suite green on 3 OSes; github module scripts run; next blocker recorded |
| C1 | Fetch/XHR bindings: reopen archive/xhr-bindings; fetch/Response/Headers + XHR state/events on FetchPolicy; promise jobs + callbacks through the engine pump | Athena (integrator), Talos inside rustkit-net/http | Prometheus; Talos on boundary | Cursor (Pollux backup) | done (#450,#455,#459) | module+fetch app fixture; §7 deny matrix passes |
| C2 | Module loading policy: script destination, MIME + CORS checks for module fetches through transport + shield | Talos | Prometheus | Cursor | done (#448) | deny tests: wrong MIME, cross-origin w/o CORS, private address |
| M0 | Scorer v2: text geometry by region + resource presence on archived frames; calibrated on known good/bad set; published BESIDE the old board | Pollux | Argos (Prometheus while Argos is silent) | n/a | done (#449) | separates google logo / missing art / blank shell / small splash |
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
| I0 | LIVE INTERACTION (Z lane, macOS): (a) the live click path (hiwave-app main.rs drain_pending_clicks) only does focus_at_point + link_at_point and never dispatches mousedown/mouseup/click to the DOM, so every JS-driven control is dead; wire DomEvent dispatch with hit-test target, default action (link navigation) only if not preventDefault'ed, then relayout+render; (b) Pete reports plain link clicks also fail and resize scales inversely (bigger window -> smaller page; small window -> huge text): find the window->viewport->layout scale mismatch (one root cause likely explains both: hit test in the wrong coordinate space); (c) late-arriving content never shows in the live browser: confirm whether timers/fetch/image completions after load schedule a relayout+render on the live loop | Z lane | Prometheus | Cursor | in-progress | red-first: action-script test (I1) failing before the fix. (a) click dispatch landed #480 (71de6bc); inline on<type> attributes landed #498 (0fd7882); button/img/svg click target landed #500 (ec21b4f1); checkbox/radio/label activation with live :checked and paint landed #502 (cd018121); submit and reset button click landed #504 (7f8d4ae7); details/summary landed #508 (a475082c); fragment and javascript: links landed #509 (bba8d899); keydown/input on typing and submit on Enter landed #511 (3fddd38e); fragment jump tells script landed #512 (ca855f03); keys with nothing focused and keyup landed #515 (7df68809); one focus for engine and page (script focus takes typing; focus/blur/change) landed #517 (5825c7f1); label click focuses its control up as #519 (85fb9d6f, no review yet, open at close). (c) live timer/network pump landed #486 (9e435ad). (b) resize scale landed #487 (f3efeb6); real-window click tests landed #499 (bcff1487). Not verified by a person in the real window (#515 changed app key and first-responder code nobody has run). Next session first: after-the-fact macOS receipt for #518 (landed without one, 1dff4a1b), and #514/#516 at their restacked heads if still open. Then: :checked in matches/querySelector; POST forms; keypress and modifier keys; focus at the press. See digest 2026-10-04 00:38 |
| Z2-I1 | Action-script harness: parity-capture --actions 'wait:N;click:x,y;key:..;resize:WxH;capture:name' with the same script driven through Playwright on pinned Chrome; frame diff per step. Headless, CI-able. Catalog = websuite/interactions-top20.json (Z2-M3) | Pollux | Prometheus | Cursor | | covers DOM events + post-event relayout + resize relayout |
| Z2-I2 | Real-window driver (macOS): launch HiWave, synthetic CGEvent clicks/scroll/keys + AppleScript/AX window resize, screencapture -l <window>, log assertions (content click -> Link clicked/DOM click -> Navigating). Prometheus runs it and judges frames (vision as secondary judge, Chrome-at-same-step as primary). Needs one-time Accessibility + Screen Recording grant (Pete) | Z lane builds, Prometheus drives | Argos/Cursor | | tests the real shell path the harness cannot |
| Z2-M4 | Time-stable board: (1) frames at t=1/3/5/10 s in both engines, compare matched times; 'late content' = Chrome changes between t1 and t10 and RustKit does not; (2) record/replay: freeze a site's bytes once and serve both engines from the archive with a pinned clock, so moving pages compare like-for-like. Publishes BESIDE the board (A3 untouched) | Pollux | Prometheus | Cursor | | Pete 2026-10-03: snapshots differ moment to moment |
| Z2-I3 | WebDriver endpoint in the live HiWave app (design only this phase): the W3C classic subset (new session, navigate, find element, element click, send keys, get/set window rect, screenshot, execute script) served by the real app, so the same click/resize path Pete uses is drivable by standard tools and by WPT's testdriver. CDP for Playwright connectOverCDP is rejected for now: far larger surface | Atlas (design), build after A5 | Prometheus | Cursor | | Pete 2026-10-03: 'can we use Playwright for live testing' |
| CP-A/B/C | Cloud pilot (Pete approved 2026-10-03): three one-shot Claude cloud sessions on Linux. A = web API census ledger (measurement only); B = DOM utility completeness; C = encoding/URLSearchParams/structuredClone utilities. Branches cloud/pilot-*. Measure dollars per landed PR, then scale or stop | cloud sessions (Atlas coordinates) | Prometheus | Cursor | | no macOS gates run in cloud: Z-lane macOS receipt required before landing; routines trig_011Zd9eEDd8UMrVusKMWrLoo, trig_015per4pGcL9wT7g3t2Kt4Gh, trig_01HLFQtQatxe9FG9hJePmbW5 |
| Z2-L1 | Limits ledger: one file (docs/LIMITS_LEDGER.md) that collects every 'stated limit' from the PRs since GO (en-US-only Intl, element scroll stored not rendered, same-task layout reads stale, shadow tree not rendered, adopted stylesheets not applied, no POST forms, observers ignore ancestor clipping, presence-only interfaces), each with the PR, the owner and what would retire it. New PRs add their limits to it. Guards against compatibility surface outrunning semantics (external review 2026-10-03) | cloud session drafts, Atlas owns | Prometheus | Cursor | | Monday |
| Z2-R1 | Status ladder on all three READMEs + umbrella: every feature row says implemented / integrated / exercised on real sites / compat-tested (no bare checkmarks); per-component status words; numbers refreshed from receipts with SHA | Atlas | Day 7, ships with the promotion PR (external review 2026-10-02: Windows checklist overstates) |
| Z2-M3 | 'interactive' column on the real-site board (one scripted interaction per site), alongside loads/readable/looks-right | Pollux | design only this phase; scoring change is an A3 call |

## Closure gates (B0, C0, C1, C2, D0-SVG, D1-L0), on top of the land law
1. Reduced failing case committed before the fix, green after.
2. receipt.py output in the PR body.
3. 26-case campaign at the candidate SHA (identical or every mover explained); all-site A/B for paint/fetch/script changes.
4. C1/C2: XHR_FETCH_DESIGN §7 deny matrix passes; no connection before the vet.
5. Independent re-run of the acceptance claim on the merged binary by a non-author seat that can run it: PROMETHEUS on the Mac for macOS closures (exact merged SHA, release build through the lease, own worktree); Pollux re-runs the Windows side on the next refresh; Argos (or Prometheus while Argos is silent) for Linux. Posted on the exchange.

## Receipt step for seat and cloud PRs
Athena and Talos cannot run macOS gates. For every seat PR to hiwave-macos that reaches R1 CLEAR, the Z lane runs a RECEIPT STEP on the Mac before its own package work: build the PR head with --profile parity, run the 26-case campaign and (for paint/fetch/script changes) the all-site A/B against develop, and post the result on the PR. The seat posts its own OS's parity and script-log A/B, labelled with the OS. Nobody claims a result they did not run.
- receipt.py: hiwave-macos scripts/receipt.py (plain Python, all OSes); until it lands, the same fields by hand.
- Cloud pilot PRs (branches cloud/*, amended 2026-10-03): same rule. To keep it to ONE lane run: when several cloud PRs are R1 CLEAR and confined to rustkit-bindings/rustkit-js with green pr-swarm (the CI's macOS 26-case run), merge their heads into one throwaway local branch, run the all-site A/B of that against develop once, and post the same result on each PR naming the SHAs covered. If the combined run regresses a site, bisect by PR. A cloud PR does not land without this.

## Rules
- D1 (L0 fragments) rebases on Athena's Shadow DOM slice 2 (flat tree: rustkit-dom shadow root field + flat_children() in the layout build), approved 2026-10-03 21:50 ET. The lane does not start D1's tree-build changes until slice 2 has landed or Athena says it is parked.
- Thresholds, baselines and scorer do not move this week (A3). Scorer v2 publishes beside the old board.
- Stop rule: two consecutive sessions on one package with no landed receipt -> state=blocked + one-line decision packet in digest-z.md; the lane takes the next package.
- Pete decides only: A2 (tree-reuse), A3 (any threshold change), A4 (reset spend, Day 6), A5 (ship/hold, Day 7). Silence for 24h = Atlas's recommendation.
- Builds: every cargo command via rs-cargo.py (lease + sccache). --profile parity for pixels, --release for timing. One warm worktree per package.
- No pings 17:00-19:30 ET. One noon digest per day.

## Approvals log
- STAND-DOWN (Pete, 2026-10-03 ~22:55 ET): Sunday 2026-10-04 07:00-23:59 ET all workers stand down (weekly Claude usage 67%). Mac jobs gated by ~/.claude/standdown via bin/standdown-check.sh. Day 3 of the plan is a rest day; the Day-7 date (2026-10-09) is unchanged unless Pete moves it.
- Cloud routine 'hiwave-macos parity trench' (05:00 UTC nightly, hub hiwave-macos atlas/trench-parity-finish-line, last run night 73 -> #467): PAUSED by Pete 2026-10-03 ~22:35 ET for the Z phase. Not retired. Decide at A5: resume under the next plan with an end_date and exit_metric, or write its funeral note.
- A1 plan: approved 2026-10-02 (Pete).
