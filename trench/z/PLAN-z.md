# Z phase plan, week 2 — the only source of tasks (2026-10-12 to 2026-10-16)

Written by Atlas 2026-10-12 08:40 ET from what Pete agreed on 2026-10-09 (outcome lanes, category board, visual debug mode) and the canon of 2026-10-07 (Phase X, Friday release). Last week's plan and its full record: `trench/z/PLAN-z-week1-2026-10-09.md`. A session or seat takes work ONLY from this file. A PR for an unlisted package is closed, not reviewed.

end_date: 2026-10-16
exit_metric: Pete's hand test confirms >= 4 open H-items closed on the Friday build AND the category board publishes a failure cause for every site AND the old 20-site board does not drop below 27/60
max_open_prs: 8
pr_repo: hiwavebrowser/hiwave-macos
pr_head_prefix: atlas/z-

> **CODEX RENDER REVIEW (Pete relayed 2026-10-12 morning; Atlas checked the claims against develop 81ef8b34) — THIS REORDERS THE LANES.** Verified: a shadow root is never laid out or painted (engine test `a_shadow_root_answers_queries_and_is_not_painted_yet`, lib.rs ~34371); #663's own body reports the google and bing height regressions and that reddit was never exercised; the 26-case campaign has no grid inside flex, so "campaign identical" says nothing about that work. New order for the Z lane and cloud sessions: **D1 (layout composition, #663 first) -> S0 (Shadow DOM render path) -> I0a (window frozen while scripts run) -> D0 (script reveal) -> rest of I0.** Bounded side targets, one PR each: apple hero image shifted left and hero height (use the element-diff tool from #648 to find the first ancestor whose box differs, then background/image positioning); #662 plus polygon/line clipping, checked while scrolling inside an overflow container in the real window. **Evidence rule for every major fix this week: a small reproducer, a stable page comparison, and one real-window check of the behaviour. A product row, a visible component or an icon that scrolls is the milestone; aggregate pixel percent does not set priorities.** Campaign: add grid-in-flex, shadow component and scrolled-SVG cases so it can see what we fix (new cases publish beside the 26; the 26 and their thresholds stay). Board: B0 captures also at the app's settings (15 s scripts, 2x) beside the 5 s / 1x record, and flags a Chrome reference that is a challenge or a different page variant.

> **09:05 SESSION ORDER (Atlas, 2026-10-12 08:40 ET). Develop is 81ef8b34 (= V1.3.0 plus nothing).** (1) If the screen is unlocked, rerun the 15 real-window pixel checks that did not run on the release build (`tools/real_window/driver.py`, bank the run under `z-realwindow-runs/`), and with the same build check by hand-driver whether H22 opacity, H23 static, H27 navigation reset and H25 simonwillison gutter hold in the window; post PASS/FAIL per item in the digest. (2) #662 (svg paths through the scroll transform, H24): a stand-in first review is requested this morning; answer what it names, red-first. Add a real-window check that scrolls ebay-like content with inline SVG icons and asserts the icons move. (3) #663 (grid as flex item, H26b): finish and take out of draft. (4) I0 below, item a. Do not start D1 before #662 and #663 are answered.

> **WEEK 2 STAFFING (Atlas, 2026-10-12).** Claude usage 29% with the reset mid-week; Grok seats 74% with a reset on Tuesday. So: first review goes to the Claude stand-in reviewer for #661-#663 now (they have waited since Friday night, far past the two-hour rule). Prometheus and the measure seats keep their hourly check and are tasked only for what nobody else can do until their reset. Athena stays offline until Pete says otherwise; Codex keeps the macOS-to-Windows sync. Atlas builds B0 (board and overlay) on this machine. Cloud sessions carry the Linux-buildable parts of I0, D0 and D1.

> **PETE'S WEEKEND HAND TEST: no notes received as of 08:40 ET Monday.** When they arrive they go here, above everything else, and reorder the lanes.

## Finish line (Friday 2026-10-16, Thursday-night baseline)
1. At least four open H-items closed and confirmed by Pete on the Friday build. Candidates in order: H24 eBay icons while scrolling, window frozen while scripts run, H26 Reddit grid, H13 google search box size, H9 resize latency.
2. The category board is the board of record: 30 sites in six categories, a failure cause named for every site that is not right, and the week's work chosen by counting those causes.
3. The old 20 keep running as a background trend and stay at or above 27/60; the 26-case campaign stays within 1.0 pt per case.
4. Phase X step 1 landed: `webview-fallback` deleted.
5. V1.4.0 promoted to master Friday midnight ET, with the weekly report and render comparison artifacts.

## Packages (state: open | in-progress | blocked | done)
Priority order for the Z lane (reordered 2026-10-12 after the Codex render review): D1 -> S0 -> I0(a) -> D0 -> I0(b-e). B0 is Atlas's. Related fixes ship as ONE deliverable with one combined test page (Codex review 3): a fix that only shows once another lands is tested together with it.

| id | package | owner | R1 | R2 | state | note |
|---|---|---|---|---|---|---|
| I0 | Responsive controls. (a) Page scripts off the window thread, per the thread-ownership design merged as #652 (correct the doc per its HOLD review first); the window keeps drawing, scrolling and taking clicks while a script runs. (b) #575 input ordering (clicks, scrolls, keys in arrival order, with view identity). (c) H13 google box size, H15 ebay search box, abs-pos control height from top+bottom (bing). (d) H9 resize latency. (e) Phase X step 1: delete `webview-fallback`. | Z lane; cloud for (c) | stand-in / Prometheus | Cursor | open | Acceptance is in the real window: a page running a 3 s script still scrolls and repaints. |
| D0 | Content reveal: pages that load but keep content hidden or late. FIRST classify each representative page (instagram, youtube, squarespace, github, netflix) into one bucket, and fix the first blocker, never raise a budget: content never entered the DOM / content is in an unrendered shadow tree (-> S0) / content has zero geometry (-> D1) / content hidden awaiting a callback or animation / navigation or resource load never completed. Squarespace hero (opacity now correct, the script that reveals it does not run), github loads ending at the 15 s budget, H1/H7 late content and never-ending lists, H28, H29. Use the `relayout cause=` lines (#655) to say why frames rebuild before fixing. | Z lane; cloud for script gaps | stand-in / Prometheus | Cursor | open | Each fix names the reveal mechanism (class toggle, IntersectionObserver, animation end, fetch) and pins it. |
| D1 | Layout composition, shared sizing and rendering cost. FIRST: #663 (grid as a flex item): explain and fix the google doodle block height (230 -> 460) and bing `#sb_form_q` height (60 -> 0) before it leaves draft, close the 13th case (`grid-auto-rows` with a row span), and exercise reddit itself in the app. Then nested dispatch across block, flex and grid; track sizing; spans; keeping resolved dimensions. Extend the #653 equivalence suite across nested block/flex/grid with aspect-ratio images, percentage heights, spans and out-of-flow children. ONE sizing rule in one place (stop rediscovering it): #622 relative widths, #603 flex item cross floor, #663 grid in flex, flex container in a float not shrink-to-fit, auto min-width of an empty block flex item, the 12 ignored sizing tests (grid.rs:3611, grid.rs:3451). Cost: opacity layer pool cap (50 nested opacity boxes at 2x can hold about 1 GB of GPU memory), SVG re-parse per tile stays fixed, inline SVG paths antialiased and under ancestor transforms. | Z lane; cloud for the equivalence tests | stand-in / Prometheus | Cursor | open | Sizing changes land with the equivalence suite from #653 extended, not one test per site. |
| S0 | Shadow DOM render path, end to end: flat tree (slots, assignment and reassignment, light-DOM children that are not slotted do NOT render), scoped styles (`:host`, `::slotted`, shadow stylesheets do not leak), layout, paint, hit testing, and updates on mutation. One acceptance page: a styled shadow component, slots assigned and reassigned, contents mutated; geometry, pixels and hit test checked against Chrome and in the real window. Live targets: microsoft (blank sections), reddit (light-DOM content showing where slotting should exclude it). Replaces the test that pins "not painted yet". | Z lane + cloud (dom, css, layout build on Linux) | stand-in / Prometheus | Cursor | open | Not another script-visible method: the render path. Athena's slice 2 design (2026-10-03) is the starting point. |
| B0 | Category board and visual debug mode. Board: `websuite/realsite-categories.json` (below), tagged by category and build traits; blocked sites in their own row; per site: element positions vs Chrome (#648), failure cause, first paint, layouts after load, settled CPU, scroll and link checks; a 2x capture. Debug mode: capture-tool overlay of Chrome's boxes on our frame first, then an in-app outline toggle. | Atlas | stand-in | Cursor | open | First reading Tuesday. Old /60 and /78 keep running untouched. |
| N0 | Windows sync from macOS, issues filed on what it finds (#641-#644) | Codex | n/a | n/a | open | macOS first; #641 (Windows clicks and wheel dropped) waits for Athena or Codex. |
| F0 | Fleet ops: lane job, reviews, landing, receipts, Friday promotion | Atlas | stand-in (promotion) | n/a | open | #661 receipt host paths. Correct docs #647, #652, #654 per their HOLD reviews. |

## Category board (B0), first list, Atlas's picks pending Pete's edits
Six categories of five. A site that is refused at the network layer moves to the blocked row and is reported there, never quietly dropped.
- search/portals: google, bing, duckduckgo, yahoo, msn
- reference/docs: wikipedia, github, developer.mozilla.org, stackoverflow, docs.python.org
- news/editorial: cnn, bbc, theguardian, npr, simonwillison
- shopping/listings: walmart, etsy, cargurus, autotrader, bringatrailer
- social/forums: reddit, x, youtube, news.ycombinator, facebook
- apps/product: shopify, squarespace, lyft, microsoft, apple
- blocked row (network refusal with the board's honest handshake): ebay, amazon, chrono24, cars, nytimes, chatgpt. ebay stays on Pete's hand-test list, where the app loads it.

## H-list (hand-test items)
- Landed, need Pete's hand check on V1.3.0: H22 opacity, H23 static, H27 navigation reset, H25 simonwillison gutter.
- Half: H24 eBay icons (size fixed #658; staying put while scrolling -> #662). H26 Reddit (logo width #659; grid causes open, #663).
- Open: window frozen while scripts run; H9 slow resize; H13; H16; H19b; H19c; H28; H29.

## Follow-ups carried from the promotion review and week 1
Opacity layer pool cap (D1). Abs-pos control height from top+bottom (I0c). Inline SVG paths not antialiased and ignoring ancestor transforms (D1). No 2x measurement in `parity-capture` (B0). Looks-right `unstable` rule misses a Chrome self-difference just under 15% (B0, report only; thresholds do not move without Pete). `2616ec28` (#629) never had its full engine headless run. github: half of loads end at the 15 s budget (D0). Handshake build and README "Network identity" note (awaits Pete). Executor guard; rolling app log file.

## Land law and reviewers
- Land when: R1 CLEAR and R2 PASS at the same head, checks green, merge state CLEAN. Atlas merges one PR per command with `--match-head-commit`. Never force-push. Master only on Pete's word.
- R2 stamps come from Cursor as comments OR reviews; check both.
- Stand-in first reviewer (Pete, 2026-10-09): a fresh Claude cloud session with no author context may give the first review when Prometheus has not answered within two hours; its body starts `R1 CLEAR @ <sha8>` or `R1 HOLD @ <sha8>`. This week it is used first for #661-#663.
- hiwave-macos is public: no host paths, ports, security details or live-site screenshots in PRs or issues. Frames go to hiwave-renders-private.
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
- Hand-test findings outrank headless scores. A fix for a hand-test item is not landed until the real-window driver shows it in the window.
- Progress is reported as user tasks that work, board points and H-items closed, never as commit counts.
- Thresholds, baselines and the scorer do not move without Pete. New measurements publish beside the old board.
- Honest networking as amended 2026-10-06: the app may match Chrome's handshake shape; no User-Agent change, no challenge answering; the board keeps the old handshake by default; one load per site per run.
- Stop rule: two consecutive sessions on one package with no landed receipt -> state=blocked + one-line decision packet in digest-z.md; the lane takes the next package.
- Builds: every cargo command via rs-cargo.py (lease + sccache). --profile parity for pixels, --release for timing.
- No pings 17:00-19:30 ET. One noon digest per day. LLM seats dormant Fri 00:00 to Mon 06:00 ET.
- Thursday night is the baseline; fixes continue to Friday midnight; Pete hand-tests on the weekend and his notes are Monday's queue.

## Approvals log
- Week 2 plan: written by Atlas from Pete's 2026-10-09 agreements ("Agreed, good plan"; "Perfect"). Site list is Atlas's pick until Pete edits it.
- Everything in the week 1 approvals log stays in force (script budget 60 s in the app, tree reuse on, cascade budget, handshake amendment, 25-site board).
