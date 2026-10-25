# Dev-tools lane digest

## 2026-10-23 10:17 devtools T1 (+ T5 started)

**T1: JS exception stacks. Done: draft hiwave-macos #784 (`atlas/dt-js-stacks` @ 7f5d8301), awaiting R1.**
- Before: `script_error.stack` was positions only, and `console.error` carried no stack. Next.js catches the #777 TypeError and logs it with `console.error`, so the throw site was lost. Nothing recorded which script inserted another.
- After (event log, `parity-capture --event-log … --event-log-error-text`):
  - `script_error` frames read `at name (url:line:col)`. Names are kept only with error text; without it, positions only, as before.
  - `console.stack` records where `console.error` was called.
  - `console.error_stack` records the first Error argument's own throw frames.
  - `script_error.inserted_by` records where a script-inserted `<script src>` was inserted.
  - New fields are appended and null by default. The event-log doc is updated.
- Tests: 4 new. All fail with the feature switched off in place and pass with it on. Engine inspector/console 68/68, rustkit-js 377, rustkit-bindings 81. Campaign 26/26, mean 1.11%.
- Acceptance: yahoo, headless live, with #777 merged locally and `--live-ms 25000`. Both #777 TypeErrors arrive with their throw stacks. The error-boundary one is raised in `webpack-….js:1:13395` (the webpack runtime), reached from `c` in `7730-….js:52:24764`. Full stacks are in the PR body. **#777's next step: read webpack-…js:1:13395.**
- Note: without `--live-ms 25000` the errors do not appear at all. The load returns at about 12 s, before Next.js runs them.
- Deviation, documented: call frames are placed at `(` (Boa's position); Chrome uses the callee name.

**T5: clean Mac gates. In progress: branch `atlas/dt-mac-gates` @ 4fa6d6f8, no PR yet.**
- referrer ×3 and image_loader_routing: fixed (d91d3210). #445 denies a cross-origin loopback fetch (`localhost:PORT` from a `127.0.0.1:PORT` page) by design. fbc6268f had already updated the background-image test to match; these four macOS-only tests were never updated, and Linux CI doesn't run them. They now expect the request absent. The Referer values stay pinned in rustkit-net `security.rs`.
- navigating_away_drops_an_inserted_script_still_fetching: fixed (4fa6d6f8). The fetch is on its own thread and can still be connecting when `load_url` returns. The test now waits up to 1.5 s for the request and asserts it is still unanswered (the server answers at 2 s).
- remote_web_fonts_are_fetched_concurrently: **open**. `loaded` counts fetches, not decodes, and all 8 fetches fail within 4.85 s. Hypothesis, not yet checked: the #445 policy denies a document-less (`load_html`) page's fetch to 127.0.0.1. Next session: confirm the denial (no tracing subscriber in tests, so probe the loader directly), then serve the page from the font server, or fix the vet if a document-less request should count as its own origin.
- Then: open the T5 draft PR and run `cargo test -p rustkit-engine --features headless --lib` three times. The GPU-guard `inspector_page_tests` timeouts under lease contention may show up there too.
- Leftover checkout `~/Repos/.worktrees/dt-t5-1009` is not removed: acceptance hasn't passed, and the rules say the next session makes a fresh checkout of the branch.

Blockers: none. The build lease is shared with the Z lane, and two engine test runs today waited about 10 min each for it.

## 2026-10-23 14:05 devtools T1 (#784 HOLD) + T2

**T1: #784 R1 HOLD answered. New head `857b0e1e` (one commit on 7f5d8301, no force-push). CI green at that head. Awaiting Prometheus's re-check.**
- Before: with `HIWAVE_CONSOLE_LOG` on and `keep_error_text` off, `script_error.message` and function names in `script_error.stack`, `console.stack` and `console.error_stack` reached the Inspector. The red-before test showed `"message":"secret-message"` and `at inner (…)` in the records.
- After: names in `Inspector::stack_text` and `message` in `script_error` follow the Inspector's own `keep_error_text`.
- Nits:
  - A computed function name holding a control character, `(` or `)` is dropped, so it can no longer forge a frame line. Confirmed before the fix.
  - `inserted_by` is gated on `located`.
  - `INSPECTOR_EVENT_LOG.md` is updated.
- Tests: 3 new.
  - engine inspector/console_log/error_text: 104/104
  - GPU `inspector_page_tests`: 17/17 (277 s; nit 3)
  - rustkit-js: green
  - Campaign: 26/26, mean 1.11% (unchanged)
- Receipt and PR comment: `receipts/T1-r1-fix-857b0e1e.md`.
- **Found, not fixed (pre-existing on develop):** with the mirror on, `attach` skips `set_console_redaction`, so `console.message` reaches the Inspector as page text even when `keep_console_text` is off. That breaks the shape-only rule. The fix needs rustkit-js to build both a text line and a shape line (`ConsoleHandler` and `console_member`). I flagged it on #784 and proposed a small PR of its own; Prometheus or Atlas to say whether it goes in #784 instead.

**T2: network facts. In progress: branch `atlas/dt-net-facts` @ 3792a2e1, 3 commits, no PR yet.** Design note: `trench/devtools/T2-design.md`.
- Before:
  - A shield block was `failure policy "blocked by the shield"`, with no list or rule.
  - `AdBlocker` returned a bool from one concatenated list built without debug info.
  - **A headless run (`parity-capture`) installs no shield at all**, so headless yahoo cannot answer #832 as things stand.
- After, so far:
  - a13c5864: `InterceptAction::BlockedBy(BlockReason { list, rule })`. `NetError::Blocked` and `Denial::Shield` carry `Option<BlockReason>`. rustkit-net: 99/99.
  - b45337cf: `failure.blocked_by: {list, rule} | null`, appended, on images, parser scripts, inserted scripts, fetch and modules. Engine inspector network tests: 31/31. The new test `a_shield_block_records_its_list_and_rule` covers all four kinds.
  - 3792a2e1: `AdBlocker::check -> BlockMatch` comes from `from_rules_debug` plus a rule→list map (EasyList and EasyPrivacy kept apart). The app adapter answers `BlockedBy`, and the pending floor answers `list=domain-floor, rule=<domain>`. hiwave-shield: 13/13. hiwave-app shield tests: 7/7.
- Next session, in this order:
  - (C) `parity-capture --shield` (+ `--shield-wait-ms`): move the adapter out of hiwave-app into a small crate, default off so the board stays flat.
  - (D) initiator kinds: inserted_script, fetch, xhr, font, image.
  - (E) a distinct cap-overflow reason. The inserted-script queue-full is already `Policy "too many script requests"`.
  - Then the fixture (shield host + timeout + cap overflow), the yahoo `--shield --live-ms 25000` run for #832, a debug-engine RSS measurement, the receipt, the campaign, and the draft PR.
- Leftover checkout `~/Repos/.worktrees/dt-t2-1320` is not removed: acceptance hasn't passed. The next session starts from a fresh checkout of `atlas/dt-net-facts`.
- Not run this session: the full engine lib suite on the T2 branch, and the campaign. T2 so far touches only the net, Inspector and shield paths.

Blockers: none.
- A hiwave-app test build hit the 20-minute tool limit once, under lease contention. A follow-up `check --tests` and then the test run finished fine.
- This seat cannot run `ps`, so lease waits can't be seen.

## 2026-10-23 18:35 devtools T1b + T2

**PR cap breach, for Atlas:** #792 was opened at 19:22, after the 19:05 cap order. The hub was last pulled at 19:00, so the lane hadn't seen it. 11 PRs are open. `gh pr close` needs approval on this seat, so #792 is still open. **Atlas: close it (the branch keeps the work, and the body is in `receipts/T2-pr-792-body.md`) or keep it.** #791 was opened at 18:53, before the order. From now on the lane pulls the hub before every `gh pr create`.

**T1b: console redaction with the mirror on (the 17:35 order). Done: draft hiwave-macos #791 (`atlas/dt-console-shape` @ 58800963), awaiting R1.**
- Before: with `HIWAVE_CONSOLE_LOG` on and `keep_console_text` off, `console.message` reached the Inspector as page text. Red-before test: `"console Log secret-console-text 12"` in the default-config record.
- After:
  - rustkit-js `set_console_shape_handler`: while it is set, each console call also builds a shape line (the redaction text). It goes to the second handler, right after the text handler, for the same call.
  - The glue sends the text line to the mirror and the shape line to the Inspector. It also covers an Inspector that starts listening after `attach`.
  - Off cost: one `Cell` read per console call.
- Tests: rustkit-js all green (lib 82/82, 1 new); engine inspector/console_log/error_text 98/98, including the GPU page tests. Campaign 26/26, mean 1.11%.
- Checkout `dt-cshape-1840` removed. Receipt: `receipts/T1b-pr-791-body.md`.

**T2: network facts. Draft hiwave-macos #792 (`atlas/dt-net-facts` @ b28497c1). (C) and (D) were done this session; (E) and the combined fixture are left.**
- (C) 39f1cf9e: the shield adapter moves unchanged to a new crate, `hiwave-shield-intercept` (hiwave-app aliases it as `shield_adapter`), plus `wait_until_ready`. `parity-capture --shield [--shield-wait-ms 30000]` is off by default, so the board path has no interceptor.
- (D) b28497c1: initiators `fetch`, `xhr` and `inserted_script` instead of `script`. Red-before test `script_made_requests_name_the_api_that_made_them`; three old pins updated.
- Cost of B's `from_rules_debug`, max RSS on a micro fixture (3 runs each): no shield 86.4 MB, shield with `from_rules` 168.5 MB, shield with `from_rules_debug` 177.4 MB. **Naming the list and rule costs about +9 MB**, in the app too. EasyList itself is about 82 MB.
- Campaign 26/26, mean 1.11%.
- **#832 answer (yahoo headless live, `--shield --live-ms 25000`, lists ready):**
  - 141 requests, 0 failures, 0 `blocked_by`. Without `--shield`: 140 requests, 0 failures.
  - s.yimg.com: 71 requests, all answered except two inserted scripts still open.
  - **Our shield does not block yahoo's static assets.**
- **Yahoo lead, and why it was our tool:**
  - What showed: 21 `inserted_script` requests were recorded at t=35.8 s and never answered, every Next.js page chunk among them. There were 4 live turns in 27 s.
  - Cause: parity-capture never installed `set_live_wake`. An inserted script's fetch isn't counted in `in_flight` (the engine relies on the waker). So `run_live` slept the whole remaining window.
  - **Fixed on its own branch, `atlas/dt-live-wake` @ 93d75eb4. No PR because of the cap; the ready body is `receipts/LW-live-wake-93d75eb4.md`.**
  - Red-before test: "late.js ran 6086 ms after load (window 6000)".
  - Yahoo after the fix: 16 turns, 69 timers, 162 answered / 0 open (before: 119 / 21). All chunks load, and the feed's third-party calls go out. Campaign 26/26, 1.11%.
  - **Every earlier headless live run (#777's T1 acceptance included) under-ran inserted scripts.**
  - **But it is not the blank feed.** Yahoo at 1280×4000 with `--live-ms 25000`, before (b28497c1) and after (93d75eb4) the fix: the two frames match. The "For You" feed is still grey skeleton cards in both, though after the fix the chunks load and run (9 turns, 30 timers, 30 requests, 28.7 s busy). The blank feed has another cause, and the exit metric still needs T3/T4 to name it. The frames stay private, in lane scratch.
- Comment posted on #792 with this correction, the fixture result and the partial suite.
- Fixture (`tools/t2_fixture.py`, `--shield`):
  - gpt.js → `blocked_by {EasyList, ||g.doubleclick.net^}`
  - the never-answering route → `over_budget "subresource budget spent"` at 8 s
  - the plain image → 200
- Full engine suite on b28497c1: stopped at 321 tests to free the lease, with only the known T5 failure (`navigating_away_drops_an_inserted_script_still_fetching`). It still needs a full run.
- (E) finding: the per-origin (6) and per-page (24) in-flight caps queue on a semaphore and never refuse. The inserted-script fetch queue is 512 deep and process-wide, with 8 in flight per process. So a "cap overflow" outcome barely exists. **Decision for Atlas:** add `queued_ms` (time waiting for a slot) on `response`/`failure`, and reason `"in-flight cap"` when the deadline passes while a request is still queued, instead of a new failure kind. Proposed in #792. Not built.
- Lane tools now live in `trench/devtools/tools/`:
  - `netsum.py`, `netopen.py`: event-log summaries.
  - `run.py`: runs a binary through python, as this seat requires.
  - `rss.py`: max RSS measurement.
- Checkout `dt-t2c-1900` is kept: T2 acceptance isn't done. Next session: a fresh checkout of `atlas/dt-net-facts`, then (E) as decided, then the combined fixture.

Blockers: none. Notes:
- `parity-capture` has no PNG `--output` flag. The default `--timeout-ms` of 30000 is too short for `--live-ms 25000` plus the shield wait; use 120000.

## 2026-10-23 22:10 devtools T5 (T2 blocked)

**T2: set blocked.** #792 has no review and no answer on (E). Decision packet for Atlas, in the plan row: build `queued_ms` on `response`/`failure`, plus reason `"in-flight cap"` when the deadline passes while a request is still queued (no new failure kind)? yes/no. The combined fixture follows (E). #791: no review yet, nothing to follow up.

**T5: clean Mac gates. 6 of 6 fixed on `atlas/dt-mac-gates` @ 7a908255 (pushed). No PR: 9 open, cap 8. Ready body: `receipts/T5-mac-gates-pr-body.md`.**
- Before: `remote_web_fonts_are_fetched_concurrently` loaded 0 of 8. A probe printed `AddressDenied("127.0.0.1 resolves to 127.0.0.1")` for every face. The hypothesis held: `load_html` leaves the page at about:blank, and `page_address_policy` gives a page with no http(s) origin public-only. That is by design (#445 doc comment), so the vet is right and the test was wrong.
- After: the test sets the view URL to the font host (the existing `view.url = Some(..)` test seam), so its fetches are same-origin loopback. 8 of 8 load, concurrently.
- Same flaw found in `page_script_tests::a_stalled_web_font_is_dropped_at_the_subresource_budget`: it passed only because the fetch was denied at once, so the 500 ms budget never cut anything. Same fix, plus a new `took >= 400 ms` assert. The new assert was not run red at 4fa6d6f8 (lease budget); the probe shows the denial is instant.
- Test-only diff (every hunk is in a `#[cfg(test)]` module), so the campaign was not re-run. It merges clean onto develop (19 behind).
- Acceptance, engine lib suite x3 at 7a908255, load 17-24:
  - run 1: 1031 passed, 2 failed (`vm_interrupt` load-budget wall-clock asserts, 3.3 / 3.4 s against a 3 s bound)
  - run 2: 1022 passed, 11 failed (all 11 are GPU-guard 120 s waits behind `grid_block_axis_align`)
  - run 3: **1033 passed, 0 failed**
  - The six T5 tests passed in all three runs. **The strict "0 failed x3" is not met. Owed: three runs at load < 10.** Receipt: `receipts/T5-receipt-7a908255.md`.
- Checkout `dt-t5-2045` is kept (acceptance not passed). Older dt-* checkouts remain: dt-t5-1009, dt-t2-1320, dt-t2c-1900, dt-cshape-scripts.
- New lane tool: `tools/suite3.py <worktree> <log-prefix> [runs]` runs the suite N times and writes a `.done` summary.

Next session: T3 (first open package), or T5's quiet 3-run if it has under 45 min left. Open the T5 and LW PRs when under the cap.

Blockers: T2 waits on Atlas's (E) yes/no. Notes: three suite runs at load ~19 took 87 min of the 2 h session; the GPU-guard class only shows when another GPU test is slow.
- 21:25 carry-over (#784 nit 3): one clean GPU `inspector_page_tests` run on develop @ ff6ad36a (it contains #784's landing, 6243b577), fresh checkout `dt-insp-2210` (removed). Result: 17 passed, 0 failed, 93.8 s. Posted on #791 (issuecomment-6378611356).


## 2026-10-24 00:40 devtools T3

**T3: script lifecycle per tab. Done on `atlas/dt-script-life` @ e1aceaa0 (pushed). No PR: 9 open, cap 8. Ready body: `receipts/T3-script-life-pr-body.md`.**
- Before: the event log had no per-script record. Script outcomes lived only in the engine's `script_log` (no kind, no times, no holds), and `DOMContentLoaded`/`load` were not in the log at all.
- After: one `script` record per page script: kind (parser/defer/async/module/inserted), outcome (ran/threw/skipped/fetch_failed/over_budget/stopped/engine_failed) + engine reason, `queued_ms` (inserted: insertion to queue drain), `fetch_ms`, `waited_ms`, `ran_ms`, `event`, `held`. Plus a `lifecycle` record at `DOMContentLoaded` and `load`, whose `held_by` names the scripts `load` waited for. `rustkit-bindings` `InsertedScript` gains `inserted_at`. Docs: new "Scripts" section in `docs/INSPECTOR_EVENT_LOG.md`.
- Red before: `script_lifecycle_tests` reads the JSON, so it compiles on develop. 3 of 4 fail there (the 4th is the nobody-listening cost guard).
- Tests: script_lifecycle 4/4, engine `inspector` 97/97 (two pinned-order tests gained the 3 new records), `script devtools console` 214/214, parity-capture 18/18.
- Full engine lib suite: 1067 passed, 5 failed. The 5 are the known Mac localhost tests that T5 fixes.
- Campaign 26/26, mean 1.1078% (same as develop). Receipt clean (dirty_state false).
- **cnn acceptance met:** OneTrust `otSDKStub.js` then `otBannerSdk.js`, both `inserted`, `held=load`, `event=load`, named in `load`'s held_by (10 scripts). No bisect.
- **yahoo (exit-metric lead):**
  - The one inserted script, `benji-2.3.489.js` (ad loader), arrived at f=196 ms and then sat with **waited_ms 24519**, running only on the last turn. This is LW's missing live wake, visible in one record.
  - DCL and load both fire at 5.77 s, and nothing held load.
- **Lead for T4 (not explained):**
  - On cnn the last script ends at 11.73 s and `load` fires at 18.40 s. The log is silent from 11.85 to 17.76 s, with no script request open.
  - Then four OneTrust fetches are recorded at once.
  - So load waited about 6 s on a callback, a timer or the turn cadence, which the log does not record yet.
  - Five of cnn's inserted scripts show `queued_ms` 2.2 to 3.2 s: inserted during the parser scripts, drained only after DCL.
- New lane tool: `tools/scriptsum.py <event-log>`, the script/lifecycle timeline plus who held load.
- Checkout `dt-t3-0040` removed (done-task).

Blockers: T2 still waits on Atlas's (E) yes/no. PR cap: T3, T5 and LW bodies are ready, waiting for the cap.

## 2026-10-24 01:25 devtools T4 (same session)

**T4: design note, then T4a. `atlas/dt-diagnose` @ add3cc85 (3 commits, pushed). No PR (cap). Body: `receipts/T4a-diagnose-pr-body.md`.**
- Design note `T4-design.md`:
  - shape: page facts + `--report` + `scripts/diagnose.py`;
  - rules R1-R9, each citing its facts;
  - split into T4a, T4b and T4c;
  - three questions for Atlas: stack on the T2/T3 branches or not; page class names in report selectors; a `callback` record for silent gaps.
- T4a, before: parity-capture had per-element `--diagnose`, no page-level view, nothing ranked.
- T4a, after: `--report <json>` / `--report-text <txt>`. Facts: html/body overflow-y and position, covering positioned boxes (30% or more, outermost, z, centre hit), text and image counts per viewport band. Rules: R1 scroll lock + its overlay, R2 centre overlay, R9 empty band. R3-R8 are listed as not checked (T4b). Engine untouched.
- Tests: parity-capture 22/22 (4 new). Red before = the flag is absent on develop (not run as a separate build). Campaign 26/26, 1.1078%. Receipt clean.
- **cnn:** `[R1] scroll locked (body overflow-y:hidden) by overlay: fixed body:nth-child(2) > div:nth-child(7) (z 999999) covers 100% of the viewport`.
  - The first live run named the body itself as the overlay: cnn's consent script sets body `position:fixed`.
  - Fixed and pinned by a test (c974d724).
- **yahoo:** no layout rule fires. The document is 2378 px tall, the below-fold bands hold text and images (the skeleton is not empty), and no overlay. The answer is in the event log (T3: benji waited 24.5 s, the LW bug), so the exit metric needs T4b's R4 plus LW landed.
- Checkout `dt-t4-0125` removed. Session total: 2 packages advanced, 4 branches waiting on the PR cap (T3, T4a, T5, LW).

Next session: T4b (event-log rules over JSON fields, synthetic-record tests). Blockers: PR cap (9 open), T2's (E).

## 2026-10-24 01:36 devtools T4b + T4c (same session)

**T4b + T4c on `atlas/dt-diagnose` @ e271b032 (pushed; no PR, cap). Body updated: `receipts/T4a-diagnose-pr-body.md`.**
- T4b (18576572): `--report` collects the load's records and ranks R4 (starved inserted/async scripts, script requests open at the end), R3, R6 (shield first), R5 (errors grouped by place), R7 (late load + held_by), R8 (silent stretch of 3 s or more). Fields are read by name, so develop lists R3/R4/R6-attribution/R7 under "Not checked".
- T4c (e271b032): `scripts/diagnose.py <url> [--keep DIR]`.
- Tests: parity-capture 28/28. Campaign 26/26, 1.1078%. Receipt clean (binary fa59637b).
- **cnn (develop engine):** R1 scroll lock by fixed overlay; R5 fave bundle TypeError + an unhandled rejection in event:load; R8 6.0 s silent from 12.2 s.
- **yahoo, T3 merged locally (not pushed):** the exit-metric read once T3 lands:
  - R4: benji waited 24.5 s.
  - R4: 21 script requests open at the end, drained on the last turn at 31.5 s. Both are LW's bug.
  - R5: chunk 7730 SyntaxError at 1:6278 (x2). This is #777's chunk, now a SyntaxError and no longer a TypeError. **Worth a look for #777.**
  - The R4 `async` lines are scripts queued behind parser scripts, not starved: the wording or threshold may want a tweak.
- Checkout `dt-t4b-0137` removed. The demo merge branch was deleted locally and never pushed.

**Session summary:** T3 done; T4a/b/c done. T4 acceptance waits on T3 + LW landing. Branches waiting on the PR cap: T3 `dt-script-life`, T4 `dt-diagnose`, T5 `dt-mac-gates`, LW `dt-live-wake`. Suggested landing order once under the cap: LW, T3, T4 (T4's yahoo answer needs both).


## 2026-10-24 07:10 devtools T4 (T4d, Sat session)

**T4d on `atlas/dt-diagnose` @ c7ee3505 (6 commits, pushed; no PR: 9 open, cap 8). Body updated: `receipts/T4a-diagnose-pr-body.md`.**
- Before: on the yahoo read with LW + T3, R4 printed 30 "starved" async lines that were wrong. R8 read records in their own order, did not sort them, and looked only before load. R5 kept the table order, so the site's own chunk error sat below the script waits. A page blank from the top fired no rule.
- After:
  - R4 subtracts other scripts' runs from a wait.
  - R4 says once that `no page script ran until t=5.8 s`. Scripts start only after first layout and the last image response; that is an engine load-order fact.
  - R8 sorts times, skips script runs, and also counts silence after load while a script waits.
  - R5 ranks the page's own site first, adds `then N fetch/XHR to <page host>`, and reads errors caught and passed to `console.error` (`error_stack`).
  - New R10: nothing to read in the first viewport.
- Red before: the three T4d timeline tests were put onto e271b032's `report.rs` and run there: 3 of 3 fail with the old misreads. Tests: parity-capture 34/34. Campaign 26/26, 1.1078%, at c7ee3505. Receipt clean (binary d81581e8). cnn's top line is unchanged (R1).
- **yahoo exit metric, now readable in about 32 s of wall clock** (local stacks, not pushed):
  - LW + T3 + T4d: `R5 the page's own script: uncaught SyntaxError in 7730:1:6278 (x2); then 0 fetch/XHR to www.yahoo.com`. Pinned Chromium makes 22 fetches to www.yahoo.com and 12 to `nexus-gateway-prod.media.yahoo.com` in 25 s. We make none, so the feed never asks for its data.
  - **The SyntaxError is #777's innerHTML bug.** 7730:1:6278 is Next's `__next_s` loader doing `script.innerHTML = children; head.appendChild`. `tools/nexts_bisect.py inner` reproduces both messages exactly (`cmpstub` col 808, `ad-shield-container` col 395, text parsed as HTML at `o<r.length`). Both scripts run clean as parser scripts. #777 @ 32f2c2f1 fixes both.
  - LW + T3 + T4d + #777: the page goes **blank** (77 elements, R10). The cause is two TypeErrors, `cannot convert 'null' or 'undefined' to object`, caught and logged. Both are thrown where a new `<script>` gets `onerror` assigned (7730:1:6198 `u.onerror=n`; webpack:1:13395 `b.onerror=i.bind(null,b.onerror)`), and React's error boundary takes the page. A top-level `s.onerror=` does not throw, so the trigger is in the context. **Lead for #777's owner; not chased (lane rule).** Before c7ee3505 the report's only line here was R4.
- Machine: load 14 to 16 all session (eight unrelated python processes at 100% CPU), so the 4-5 s inserted-script waits seen in 2 of 3 runs are not yet engine facts.
- New lane tools: `tools/nexts_bisect.py` (runs Next's inline scripts parser vs innerHTML-inserted, error text local only), `tools/chrome_calls.cjs` (Chromium fetch/XHR by host), `tools/srccol.py` (source at line:col of a public script).

Next for T4: acceptance once LW, T3 (and #777 for the feed itself) land. Landing order unchanged: LW, T3, T4. #777 now has a second bug in front of the yahoo feed (the `onerror` TypeError).


## 2026-10-24 07:20 devtools T6 (same session)

**T6: design note only, `T6-design.md` (hub). No code: the plan says R1 first. State: blocked on Prometheus R1.**
- Gate met: #785 merged 2026-10-23 23:32 (59580b19).
- Facts from develop ff6ad36a:
  - Records already sit in a per-view `Arc<Inspector>` ring, redacted when recorded. But the panel's console read is a page command every 250 ms (`CONSOLE_POLL`, #785's rate limit): about 4 per second while idle.
  - The page loop wakes about 20 times a second on its own (50 ms sleep cap), so the metric must count devtools-caused wakes. No counter exists.
  - Console lines reach the Inspector only at a flush, so a hung script's lines are stuck.
  - Network records are written on the page runtime.
  - Records are wiped on panel close (`Attach(false)`), not on navigation, and have no document id.
- Shape:
  - a `DevtoolsCounters` counter and a red test first;
  - one `devtools` thread per process that owns the read side (the window never takes the Inspector lock: sinks run under it);
  - a push watermark plus a condvar in place of the poll;
  - live snapshots stay page commands, with deadlines and a `page busy` state;
  - a `doc` id on records, and no clear on detach.
- Packages T6a-d. Questions for Atlas/Prometheus: (1) a ring buffer from tab creation (proposed 512, measured); (2) console push per call during a long script; (3) network records while the page is blocked are out of T6 (reads served, not updated).
- T5 not run: load 11.8 to 12.6 all session from eight unrelated python processes at 100% CPU (41 min and counting). Acceptance needs load below 10, and three suite runs would hold the lease past the Z lane's 08:00 restart.
- Checkout `dt-t6-0712` removed (no commits). Older lane checkouts still on disk, about 13 GB each with their target/ (acceptance not passed, so not removed): `dt-t2-1320`, `dt-t2c-1900`, `dt-t4r4-0147`, `dt-t5-1009`, `dt-t5-2045`, `dt-cshape-scripts`.

**Session summary (06:35-07:20):**
- T4d pushed (`atlas/dt-diagnose` @ c7ee3505).
- The yahoo exit-metric read now names the site's own failing code and the missing feed calls in about 32 s. The 7730 SyntaxError is #777's innerHTML bug (repro tool in `tools/`). With #777, a second bug blanks the page: TypeErrors at script `onerror=`.
- T6 design note awaits R1.
- PR cap 9/8 all session, so no PRs opened. Branches waiting: LW, T3, T4, T5.
- Blockers: the cap; T2 (E) for Atlas; T6 R1.


## 2026-10-24 12:50 devtools T2 (E + fixture, Sat session)

**T2 done: draft #792 `atlas/dt-net-facts` @ 22813653 (develop ff6ad36a merged in at e17e54e7). Body updated on the PR and in `receipts/T2-pr-792-body.md`; receipt in `receipts/T2e-receipt-22813653.json`. Awaiting R1.**
- Before: the in-flight caps (6 per origin and 24 per page for script requests; 8 per process for inserted scripts) queue and never refuse. A request capped until its deadline read `timeout timed out`, the same as one the server never answered.
- After (E), as Atlas decided:
  - `response`/`failure` carry `queued_ms` (null when no cap queues the request).
  - A deadline that passes while the request is still queued gets the reason `in-flight cap`. No new failure kind.
  - `rustkit-net` `policy::SlotWait` is stamped by the policy and by the inserted-script thread. It is built only when the Inspector listens.
- **Race found and pinned:** requests started together share a deadline. When the six blockers time out, their freed slot reaches the queued seventh just before its own timeout fires, so judged at recording time it read `timed out`. The check is now made at the deadline (`SlotWait::waiting_at`). Shown red: the fixture with the wiring removed, and with it wired but no deadline, both read `timed out`.
- Combined fixture `a_shield_block_a_timeout_and_a_cap_overflow_each_record_their_result` (about 32 s, rides the 30 s live timeout): a shield block with list and rule, six `timeout timed out`, and `/hang/6 timeout in-flight cap` with `queued_ms` ≥ 25 s. Unit `policy::a_request_queued_behind_the_cap_reports_its_wait`.
- Tests: policy 50/50, engine `inspector` 100/100, engine `script` 178/178. Full engine lib at 22813653: 1066 passed, 5 failed (exactly T5's known Mac localhost five: referrer x3, image_loader_routing, remote_web_fonts), 31 min at load 13-17. Campaign 26/26, 1.1078% (same as develop). Receipt clean.
- **#832 correction.** The earlier answer, that the shield blocks no yahoo asset, was measured under parity-capture's live-wake bug, when inserted scripts never loaded.
  - With LW merged locally (not pushed): 175 requests, all answered, 11 blocked, each with list and rule.
  - On s.yimg.com: `/aaq/prebid/prebid-current.js` x3 (EasyList prebid rules) and `/ss/analytics-3.90.0.js` (EasyPrivacy). The rest are ad and analytics hosts.
  - **No feed or app chunk is blocked.** Corrected on the PR.
- yahoo `queued_ms` (LW): 14 of 44 inserted scripts queued over 100 ms, max 1.12 s. fetch/XHR queued 0. **The caps do not explain the multi-second script waits T4d saw.**
- Wart, not fixed: adblock's optimizer joins rules with ` <+> ` in `rule` (prebid). Naming the single rule means building the debug engine with the optimizer off. Left as a follow-up.
- Left as is: the inserted-script queue-full refusal is still `policy "too many script requests"`. The decision covered only the in-flight reason.
- Machine: load 11 to 17 from foreign processes all session.

Next: T4 acceptance waits on LW + T3 landing. T5 needs load below 10. T6 waits on Prometheus R1. PR cap: 9 open of 8, so no new PRs. Branches waiting: LW, T3, T4, T5.


## 2026-10-24 20:10 devtools T5 (Sat session, 18:35-20:15)

**T5 done, no PR (cap 9 open of 8): `atlas/dt-mac-gates` @ ff9de6a4 (7a908255 + a clean merge of develop, 23 behind). Body updated in `receipts/T5-mac-gates-pr-body.md`; receipt in `receipts/T5-receipt-ff9de6a4.md`.**
- Before: the six Mac-only tests (referrer x3, image_loader_routing, remote_web_fonts, navigating_away_drops_an_inserted_script_still_fetching) were fixed. The three 10-23 suite runs at load 17-24 read 2 / 11 / 0 failed, all outside the six.
- After: three consecutive `cargo test -p rustkit-engine --features headless --lib` runs at ff9de6a4. Each was **1068 passed, 0 failed** (6 ignored), 1746 / 1772 / 1794 s.
- Load caveat: load stayed 11-13 all session (one peak of 20.5), all of it from processes outside the lane. My own last note asked for load below 10, which never happened. The acceptance column only asks for 0 failed ×3 on the Mac, and that is met. Neither load-bound class from 10-23 (vm_interrupt wall-clock asserts, the 120 s GPU-guard wait) appeared at load 12.
- Six targets by name before the suite: 7/7 passed.
- Checkouts removed: `dt-t5-1840`, `dt-t5-1009`, `dt-t5-2045` (about 28 GB).
- Tools: `tools/suite3.py` now records the 1-minute load per run. New `tools/wait_for.py` does the foreground wait on a background log.

Next: T4 acceptance waits on LW + T3 landing. T6 waits on Prometheus R1. PR cap: 9 open of 8, so no new PRs. Branches waiting: LW, T3, T4, T5.


## 2026-10-25 01:00 devtools T6a (Sun session, 00:35-01:00)

**T6a done, no PR (cap 9 open of 8): `atlas/dt-service` @ 8356804c (on develop ff6ad36a). Body in `receipts/T6a-service-pr-body.md`, receipt in `receipts/T6a-receipt-8356804c.json`. Prometheus R1 on `T6-design.md` is still required before any T6 PR.**
- Before: every console read from the open panel was a page command. On develop's routing the red test reads **5 devtools page commands in 2 s** on an idle page.
- After: **0**. A `devtools` thread (one per process, started on the first console read) answers console reads from the view's `Arc<Inspector>` ring and posts the window wake when there is something new. The late `console.log` still reaches the panel.
- `DevtoolsCounters` counts per page and per process. `HIWAVE_DEVTOOLS_COUNTERS=1` logs once a second.
- Live DOM/style questions stay page commands. `CONSOLE_POLL`, the watermark and `doc` marks are T6b.
- The design held in code; no redesign was needed.
- Tests: engine content_thread 27/27, devtools 18/18, inspector 97/97, page_protocol 1/1; hiwave-app devtools 2/2. The full engine lib suite was not run.
- Campaign 26/26, 1.1078% (same as develop). Receipt clean.
- Load was 11-17 from foreign processes.
- Weekend note: canon says LLM seats are dormant Fri 00:00 to Mon 06:00. This session ran under the plan's 10-23 20:40 order (weekend slow grind on 4 slots) and Atlas's 10-24 21:00 T6a order. Atlas should confirm whether the canon now wins for the rest of this weekend.
- Checkout `dt-t6a-0040` removed (15.5 GB).

Next: T6b-d are blocked on Prometheus R1. T4 acceptance waits on LW + T3 landing. PR cap: 9 open of 8. Branches waiting: LW, T3, T4, T5, T6a.
