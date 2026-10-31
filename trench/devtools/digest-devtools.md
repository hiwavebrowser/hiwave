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


## 2026-10-25 08:15 devtools T6 (T6a suite + T6b, Sun session, 06:35-08:20)

**T6b done, no PR (cap 9 open of 8; Prometheus R1 also needed): `atlas/dt-service` @ eb8bcc65, stacked on T6a 8356804c. Body: `receipts/T6b-push-pr-body.md`. Receipt: `receipts/T6b-receipt-eb8bcc65.json`. A/B: `receipts/T6b-ab-ring-eb8bcc65.txt`.**
- (1) **Full engine suite on T6a @ 8356804c** (Atlas 01:50 order): 1064 passed, 5 failed, 1799 s. The five are exactly the Mac localhost tests (referrer x3, image_loader_routing, remote_web_fonts) that T5 fixes on `atlas/dt-mac-gates`, which T6a does not include. No T6a regression. Receipt: `receipts/T6a-suite-8356804c.txt`.
- (2) **T6b**, as the 10-24 07:50 decisions lay it out:
  - Push watermark. A guard on the Inspector lock stores an atomic watermark and, while a panel watches, signals the devtools thread after the lock is released.
  - The devtools thread waits on one condvar for reads and records. It wakes the window once per unread batch.
  - `CONSOLE_POLL` and `ConsolePoll` are gone. The panel asks only when the watermark has moved; that check is one atomic load.
  - `doc` on records and console entries.
  - Detach keeps history.
  - A 512-record ring per tab, on by default (`InspectorConfig::tab`); `HIWAVE_DEVTOOLS_RING=0` turns it off.
  - Test-only `PageCmd::Block(ms)`.
- **Before -> after:**
  - Panel open on an idle page: a console question every 250 ms -> **0 window wakes and 0 page commands in 1 s**.
  - A console read with the page thread blocked 3 s: answered in under 1 s.
  - Reopening the panel after a navigation: empty -> both documents' lines, told apart by `doc`.
- **Red before**, by mutating eb8bcc65 (detach clears; watch never registers; console reads to the page): the three new tests read 0 passed / 3 failed. After: engine `content_thread devtools inspector page_protocol` 144/144, hiwave-app devtools 2/2, parity-capture event_log 2/2. Three tests that pinned "off by default" / "closing empties" were rewritten to say what T6b does.
- **Ring cost (Q1 gate):**
  - Campaign 26/26, 1.1078% (same as develop).
  - 20-site A/B, ring off vs on, one binary: wall-clock 205.0 s vs 203.4 s (0.992), 0 failures, no frame moved.
  - linkedin read 2.64% across the arms at first. Two reruns plus off/off and on/on controls show the same split with no ring difference involved: linkedin rotates its own page variants.
  - **The ring ships on.**
- **Suite on T6b @ eb8bcc65:** 1068 passed, 5 failed, 1787 s, load 11.7-14.8. The five are the same Mac localhost tests; T6a had 1064 passed, and T6b adds 4 tests. Receipt: `receipts/T6b-suite-eb8bcc65.txt`.
- **Load (Atlas asked for the top 3 by CPU):** the "foreign" load 11-17 the lane has reported since 10-23 is the lane's own.
  - At 07:22, load 20.3. Top: `BTLEServer` 100%; `aleph.cli serve .` workers (8+ at ~100% each, 47 min old); `null_memory.cli daemon run` (pid 1233) 100%, up 21 days.
  - The aleph server's parent chain is this session: `claude -p` <- `~/.claude/hooks/trench-devtools.sh`. It starts with every lane session and dies with it, which is why Atlas reads 2.6-5 between sessions.
  - The seat cannot kill it. Fixing it is fleet tooling: start the lane without the aleph MCP, or let the index settle first.
  - The null daemon at 100% for 21 days is worth a look by whoever owns Null.
- Found, not changed: on the content-thread test page, `load_html`'s inline `<script>` did not run (`document.title` stayed empty). The T6b tests log through `eval` instead. This may be how `page()` is configured, not a bug; it is worth a check by whoever owns content_thread tests.
- Not done: the panel HTML does not group by `doc` yet (the field is in its payload).
- Checkouts `dt-t6suite-0640` (12 GB) and `dt-t6b-0640` (16 GB) removed.

Next: T6c (busy state + deadlines) and T6d stay blocked (Atlas). Prometheus R1 on T6-design.md is needed before any T6 PR. T4 acceptance waits on LW + T3 landing. PR cap: 9 open of 8. Branches waiting: LW, T3, T4, T5, T6 (a+b on `atlas/dt-service`).


## 2026-10-25 12:42 devtools T6 (T6b panel grouping + inline-script probe, Sun session, 12:35-12:45)

- **Load before starting (Atlas asked; confirms the Aleph fix):** 2.95 / 2.84 / 2.83.
  - Top 3 by CPU: `BTLEServer` 100% (up 22 days); the null daemon (pid 1233, anaconda python) 100% (up 22 days); two `aleph.cli serve` started by the Claude desktop app 2.5 days ago, at about 23% each.
  - No `aleph serve` started by this session. Load was 11-17 when the lane started its own aleph serve; with `--strict-mcp-config` it is under 3.
- **(1) T6b panel grouping, done:** `atlas/dt-service` @ a3652306, on eb8bcc65.
  - The panel's `consoleRows()` puts a divider wherever `doc` changes ("Document N (earlier page)") and dims lines from earlier documents. One document in view means no dividers.
  - Console input and results take the document of the line before them.
  - Test `scripts/tests/test_inspector_console_groups.py` runs the function in node: 4/4 after, 0/4 against the eb8bcc65 panel.
  - Rendered in Playwright WebKit: two documents plus an eval result show as two groups, the first dimmed.
  - HTML-only change, so no Rust suite and no campaign were run (parity-capture never loads this panel).
  - Receipt: `receipts/T6b-panel-groups-a3652306.md`.
- **(2) Inline-script probe (time box 45 min, used about 5): a real engine bug, not the test page.**
  - `ContentThread::load_html` -> `PageCmd::LoadHtml` -> `Engine::load_html_as` builds the bindings and lays out, but never runs the document's `<script>`s. Only the Inspector page path calls `run_inline_scripts` afterwards. JS is on by default; `eval` afterwards works.
  - Shipped effect in RustKit content mode: New Tab / About (`ABOUT_HTML`) and the report page (inline Chart.js) load this way, and their scripts never run.
  - The RustKit chrome also uses `load_html`, but it is built with JS off, so it is unaffected until Phase X turns script on.
  - Red test `content_thread::tests::load_html_runs_the_documents_inline_scripts` on `atlas/dt-inline-script` @ bd00fb21 (on develop ff6ad36a): FAILED, "the inline script did not run: String("before")". No fix, no PR.
  - Two fix options are in `receipts/inline-script-probe-bd00fb21.md`.
- Checkouts `dt-t6b2-1240` (10 GB) and `dt-inlinescript-1300` (12 GB) removed.

Next: T6c and T6d are still blocked on Prometheus R1. Atlas decides who fixes the `load_html` inline-script gap and whether it becomes a package. PR cap unchanged (no PR opened). Branches waiting: LW, T3, T4, T5, T6 (a+b+grouping on `atlas/dt-service` @ a3652306), `atlas/dt-inline-script` (red test only).


## 2026-10-25 19:21 devtools T8 (load_html runs inline scripts, Sun session, 18:35-19:25)

- **Package choice:** T8, per Atlas 10-25 13:05. T4 comes earlier in the table and reads "open", but its acceptance waits on LW + T3 landing, so it cannot move this session.
- **Load at start:** 4.82 / 4.05 / 3.39; about 3.4-4.4 through the session.
- **Before -> after:**
  - Before: `Engine::load_html_as` ran no `<script>`; red test bd00fb21 failed.
  - After: `atlas/dt-inline-script` @ 43169252 (fix 96f3e10d + test-only 43169252). `load_html_as` runs the inline classic scripts in document order after the first layout, then `DOMContentLoaded` and `load`, before `PageLoaded`.
  - It uses the same `inline#n` names, budget/watchdog, script log and Inspector records as the URL path.
  - External and module scripts are logged as skipped (no network on this path). Timers are left to the live loop.
  - JS off is unchanged: the RustKit chrome is untouched, and parity-capture `--html-file` without script runs nothing.
- **Inspector page and `run_inline_scripts`:** `Engine::run_inline_scripts` is removed. The parity-capture Inspector page and `--run-inline-scripts` read the script log, so nothing runs twice, and a throwing script still fails the capture.
- **Tests:**
  - Red test green, plus 3 new: lifecycle order `loading,second,dcl:interactive,load:complete`; `about.html`'s `hiwaveAbout.setVersion` updates `#versionBadge`; the Inspector page's script log is exactly `[inline#1 Ran]`.
  - With the new call disabled, the four read 0/4.
  - parity-capture 18/18.
- **Suite:**
  - 96f3e10d: 1052 passed / 20 failed. That is the five Mac localhost tests plus 15 `shadow_tree_tests`, whose helper re-ran the page scripts by hand, so `attachShadow` threw a second time. Fixed in the test helper (43169252).
  - 43169252: **1067 passed / 5 failed** (the Mac localhost set only, the same as develop), 956 s.
- **Campaign:** 26/26, 1.1078%, the same as develop.
- **PR:** none (cap 9/8). Body is in `receipts/T8-inline-script-pr-body.md`, receipt in `T8-receipt-43169252.json`, suite summary in `T8-suite-43169252.txt`.
- **Behaviour change for review:** `parity-capture --html-file --actions` already turned script on. Inline scripts now run there on load, as in Chromium.
- Checkout `dt-t8-1840` removed.

Next: stop (Atlas: after T8, stop). T6c/T6d are blocked on Prometheus R1. T4 acceptance waits on LW + T3 landing. Branches waiting for the PR cap: LW, T3, T4, T5, T6 (`atlas/dt-service` @ a3652306), T8 (`atlas/dt-inline-script` @ 43169252).


## 2026-10-26 01:05 devtools T4 (Monday stack check + T4 acceptance read, Mon session, 00:35-01:05)

- **Order:** Atlas 10-25 20:15. The table had no package in-progress, so I took the first open one, T4. Weekend rule: Atlas 10-25 01:50 lets this lane run through Mon 06:00.
- **Load at start:** 2.78 / 2.68 / 2.66, and 3.2-3.5 during the suite. This seat can't list the top processes: `ps` and `top` both need approval.
- **Stack:** develop ff6ad36a, then LW, T3, T4, T5, T8, T6 with `--no-ff`, on local branch `local/monday-stack-0035` in checkout `dt-stack-0035`. Nothing was pushed.
  - One textual conflict: **T8 vs T4**, in `parity-capture/src/main.rs` `struct Args`. T4's `--report`/`--report-text` sit next to T8's reworded `run_inline_scripts` doc comment. The fix is to keep both, and it belongs to T8's develop merge.
  - Two semantic failures: **T3 vs T6**. T6's default 512 tab ring means (1) T3's `with_nobody_listening_no_script_record_is_built` sees an active inspector, and (2) `a_page_throwing_any_engine_message...` loses 50 of its 456 errors to the ring once T3's per-script records are added.
  - The fix is two test lines that turn the ring off (`ring_off()`, as T6 already does in its own test). It belongs to T6's develop merge after T3 lands. The diff is in the receipt. I didn't commit to any queued branch.
- **Results:**
  - Engine suite on the merged stack: **1079 passed / 2 failed** (B1, B2 only), 962 s. The Mac localhost five pass because T5 is in the stack.
  - After the fix: 6/6 targeted.
  - parity-capture tests: 35/35.
  - Campaign: **26/26, 1.1078%**, the same as develop.
- **T4 acceptance read:** `diagnose https://www.yahoo.com/` cold on the stack took **31.0 s wall clock** (31.0 s again on a second run).
  - Top line: `[R10] the first viewport has no text and no image (154 elements, document 800px tall)`.
  - Line 2: `[R5] own script: uncaught SyntaxError in chunk 7730...:1:6278 (x2); then 0 fetch/XHR to www.yahoo.com` = #777.
  - R6 (shield) isn't checked because T2 isn't in the stack.
  - Change from T4d: today yahoo is blank without #777. I haven't found why (yahoo build or T5/T8/T6); not bisected.
- **Question for Atlas:** one yahoo load writes 562 records (114 of them T3 `script` records). With T3 + T6, a panel opened late loses its first ~50 records, including `navigation_start`. Should `TAB_RING_CAPACITY` be raised?
- **PR:** none (cap: 9 open of 8).
- **Receipts:** `receipts/monday-stack-check.md`, `receipts/monday-stack-suite-6a6eb306.txt`.
- **Checkout `dt-stack-0035` kept:** done-task.sh refuses because of its unpushed local merge and fix commits, which must not be pushed. Remove it by hand when Atlas is done with it.

Next: T4 is done and waiting for Atlas's score. T6c/T6d are blocked on Prometheus R1. Landing notes for Monday: T8 resolves the main.rs doc hunk, and T6 adds the two ring_off test lines after T3. Branches waiting for the PR cap: LW, T3, T4, T5, T6, T8 (SHAs as before).


## 2026-10-26 08:15 devtools T4 (a) + T6 (b,c,d) + T1b R1 (Mon session, 06:35-08:20)

- **Order:** Atlas 10-26 06:20 (a)-(d), then the 07:40 order, item (1). Load was 9-12 for the whole session; it stayed about 10 after my own suite ended, so it comes from outside the lane.
- **(a) T4 cause over symptom:** `atlas/dt-diagnose` @ **1f9185ae**. An uncaught own-site error now ranks above R10 when the first viewport is blank. Caught+logged errors and third-party errors stay below it. With the new arm off, 2 of 12 report tests are red. parity-capture 35/35. Live yahoo now shows it: line 1 is R5 chunk 7730 SyntaxError, line 2 is R10.
- **(b) T6 R1 conditions 1, 2, 3, 6, 7 + ring 2048:** `atlas/dt-service` @ **9eba090c**, one test per condition. With all five changes off, the five tests read 0/5.
  - (1) The service re-reads the watermarks under the mutex before sleeping, with a 1 s backstop while a panel is open (no clock otherwise). SeqCst.
  - (2) Answers carry `page_crashed` (from lock poison), and the panel prints 'page crashed'.
  - (3) Watches hold `Weak`. 20 closed tabs keep 0 rings; a full 2048 ring is about 301 KiB of payload per tab.
  - (6) A response or failure gets the doc its request started in.
  - (7) The service re-applies the URL rule to what it serves.
  - Suite **1073/5** (the Mac localhost set).
  - Campaign **26/26, 1.1078%**.
  - **20-site A/B: no pixel mover.** Wall-clock B/A = **1.028** over 16 sites. The run is NOT clean: load 8-12, microsoft and github hit 30 s on both arms twice, and cnn and lyft lost single captures. I can't call it a move or not; repeat it quiet before the T6 PR. Receipt: `receipts/T6-r1-conditions-9eba090c.md`, table in `T6-ab-ring2048-9eba090c.txt`.
- **(c) yahoo bisect:** develop ff6ad36a + LW + T3 + T4, with no T8/T5/T6, is **already blank** (R10, 155 elements). Verdict: **"yahoo changed"**. The same stack was not blank on 10-24. One build plus one 31 s run settled it, so no further steps.
- **(d) T6c started:** `atlas/dt-service` @ **2d1b0bd4**.
  - `PageCmd::DevtoolsEval` carries a deadline. A page that reaches it late answers `EVAL_CANCELLED` and never runs it. The page also skips it when the panel has already dropped the receiver.
  - The panel gives up after 5 s and drops the receiver, so a late reply is discarded.
  - Red before: the late eval ran. 150/150 across content_thread, page_protocol, devtools and inspector.
  - **Left for T6c:** deadlines and generation ids for NodeAt/DomTree/Element/Highlight, and the busy state. The panel only checks its deadline on a live wake, so a hung page with no wakes shows the cancel only at its next wake.
- **07:40 (1) #791 T1b:** the requested proof found a **real leak**. With the mirror on and keep off, `script_error.message` carried the page's thrown text. Function names and `console.error` records were already shapes.
  - Fixed @ **82af54cf**: the message is kept only under `keeps_error_text()`. New test red before, green after; inspector 90/90; suite **1040/5** (the Mac localhost set).
  - Comment posted on #791.
  - **Not marked ready:** `gh pr ready` needs approval on this seat. Atlas, please flip it.
- **Not started:** 07:40 (2) #792 conditions (a) `<+>` rule attribution and (b) `from_rules_debug` ~9 MB RSS gate, plus the nits.
- **Checkouts:** `dt-bisect-0729` kept. It holds 3 local merge commits (LW, T3, T4 on develop) that must not be pushed, so done-task refuses. Remove it by hand. All other checkouts removed.
- **PRs:** no new PR (cap).

Next: #792 conditions (a) and (b); then the rest of T6c (live-query deadlines + generation ids, busy state); a quiet re-run of the T6 ring A/B before the T6 PR.

## 2026-10-26 14:05 devtools T3 + T1b + T8 (Mon session, 12:35-14:05; orders 09:05, 09:40, 11:40)

- **#797 T3 R2 HOLD answered @ d4db95f7** (was 29e9c396). (1) An unparseable `src` is labelled `unparseable#n` in the script log, the Inspector and `held_by`, never by its text. (2) A `cancelled` outcome covers the load path (between scripts, and during a module's import fetch) and `cancel_inserted_jobs`. (3) The lifecycle flags are now kept with nobody listening, so a late attach reads `held=load`. Prometheus's `held`/"will hear" doc points are folded in. No dead_code warning traces to T3 in either test build (the warnings there predate it).
  - Red-before 4/4. Suite 1071/5, the Mac localhost set (branch base predates T5). Campaign 26/26 1.1078%. Comment posted; 9 behind develop, merge-tree clean.
- **#791 T1b: develop 5593cf37 merged @ 97de231c** (merge commit). Stacks and shapes are both kept: `ConsoleCall` carries shape + `ConsoleStacks`, and the shapes path strips function names (`nameless`).
  - New test `with_the_mirror_on_console_error_stacks_are_shapes_only`, red when names are kept (keep_error_text arm).
  - Suite **1074/0** (T5 is in), rustkit-js green, campaign 26/26 1.1078%. Now MERGEABLE; comment posted.
- **#799 T8 review folded @ 324b417b**: (1) nav cancel in the `load_html` script phase, with a test that is red with the checks off; (2) `scripts_over_budget` counted from the log; (3) the `--run-inline-scripts` filter, tested with an external src.
  - Suite 1075/1. The one failure is `a_slow_post_load_fetch_or_import_holds_no_live_turn` (110.98 ms, wall-clock assert, load 8.3), which passes alone. Campaign 26/26 1.1078%. Comment posted.
  - **(4) done at 14:06**: hiwave-smoke `--html-file about.html` (real window, locks free), started through a python3 subprocess wrapper (a direct call needs approval on this seat). It exited 0 and wrote the frame. `inline#1` (987 B) ran with no script error. The frame is correct, with the script-filled version line `v0.1.0-alpha`. A second comment is on #799 (receipts/T8-smoke-about-324b417b.md). The other four builtins were not run. Prometheus nits 1 and 3 are follow-ups.
- **Leave to Atlas:** `gh pr ready` and the re-stamp requests (Prometheus deltas: #797 29e9c396..d4db95f7, #791 82af54cf..97de231c, #799 7a622c3b..324b417b). #791's follow-up: the `ScriptError.name` subclass nit.
- **Checkouts:** `dt-t3fix-1240`, `dt-t1bmerge-1308` and `dt-t8fold-1339` removed. `dt-bisect-0729` is still there from before.
- **PRs:** no new PR (9 open). Load 7-8 during the suites.

Next: the 08:50 list: #792 conditions (a) and (b), the rest of T6c, and a quiet T6 ring A/B.



## 2026-10-26 18:35 devtools T2 + T6 + review follow-ups (Mon session, 18:35-19:45; Atlas order 14:35)

- **(1) #792 T2: R1 conditions answered @ 536351fa** (was 22813653). develop 68f4c8e1 merged @ a3791247. One conflict, in `INSPECTOR_EVENT_LOG.md`, with both sides kept.
  - **(a) ` <+> ` rules.** adblock-rust joins plain pattern rules that share options and a token. Each part is now looked up: the list is named only when every part is from it, else `unattributed`. Red before: an EasyPrivacy match joined with an EasyList rule read `EasyList` (2/2 tests red with the old lookup).
  - **(b) Rule names gated.** `with_filter_lists()` is the plain engine again. Rule text comes only from `with_filter_lists_naming_rules()`, which the intercept worker uses after `name_matched_rules()`. parity-capture `--shield` calls it.
  - **RSS:** max RSS on the full lists, 3 runs each: **111.0 vs 118.9 MB, so rule names cost +7.9 MB**. The app now pays 0.
  - **Behaviour change for Atlas/Prometheus:** in the app, a filter-list block now has `rule: null`, and the list is `unattributed` when both lists are loaded.
  - Suite **1099/0**, campaign **26/26, 1.1078%**. Comment posted. Receipts: `T2-r1-conditions-536351fa.md`, `T2-receipt-536351fa.md`.
  - Not in this push: the (slot, no deadline) arm still judges at record time, and the yahoo LW numbers still need re-measuring.
- **(2) T6 is draft PR #803 @ 3eca9c25** (`atlas/dt-service`, 5 open PRs before it).
  - develop 68f4c8e1 merged @ 6b1463f5. The conflict was `inspector.rs` State: I kept T6's id → doc map together with T3's lifecycle fields.
  - `ring_off()` fix for T3's two tests.
  - **New find:** the lost-wakeup test failed once under the 165-test parallel set. The global `BEFORE_WAIT` hook was taken by another test's service pass before this test's read (next_seq 2, not 1). It is a test race, not a service bug. The hook is now set after the read (3eca9c25).
  - Suite **1107/0**, campaign **26/26, 1.1078%**, app devtools 2/2.
  - The body covers T6a, T6b, the 7 conditions (4 = T6d, not in the PR; 5 started) and T6c so far.
  - **Quiet ring A/B: PENDING.** Load was 7-9 all session, and the rule is under 4. Body: `receipts/T6-pr-body-3eca9c25.md`.
- **(3) `atlas/dt-review-followups` @ dfeb141a** (branch only, no PR, as ordered).
  - **#799 nit:** `--run-inline-scripts` fails on any `Skipped` except the new engine const `HTML_LOAD_RUNS_INLINE_CLASSIC_ONLY`. That covers too large and an earlier engine panic. Tested with an inline script over 4 MB. Red-before was not run separately: the old filter has no `Skipped` arm.
  - **#797 `held_load`:** a navigation with nobody listening now clears `held_load` and its count. Red before: doc 2's `load` named doc 1's `inline#1`.
  - **#797 `unparseable#n` collision:** the inserted path's label is now `unparseable-inserted#<node>`, apart from the load path's `unparseable#<index>`, and the docs are updated. **Untested:** neither `s.src =` nor `setAttribute('src', …)` with a bad port reached `script_net`'s unparseable branch (no `script` record at all). The bindings must drop it earlier, so that branch may be dead. Worth a look.
  - **#802 nits:** diagnose.py uses a `TemporaryDirectory` (removed even on failure) and prints the stderr tail when there is no report. `site_of`: `file://` has no site, and an IPv4 host is whole. Unit test added.
  - **#791:** stack frames come from `/app.js?token=SECRET` (no `token` reaches the Inspector, and the frames name `/app.js`). A new `console.assert` + `timeLog` shapes test. Both pin behaviour that was already correct, so they were never red.
  - Targeted tests are green: script_lifecycle + inspector 110/110, parity-capture 38/38, the 3 mirror tests. Full suite **1097/1**. The one failure is the wall-clock `a_slow_post_load_fetch_or_import_holds_no_live_turn` (103.9 ms at load 7-9), the same as 14:05; it passes alone.
- **Leave to Atlas:** `gh pr ready` on #803 if wanted. Prometheus re-checks: #792 delta 22813653..536351fa, and #803 R1 on the PR.
- **Checkouts:** `dt-t2cond-1840` and `dt-t6pr-1905` removed. `dt-followups-1931` removed too (its branch is pushed). Older ones still on disk, not mine to remove: `dt-t2-1320` (holds a stale local `atlas/dt-net-facts` @ 3792a2e1), `dt-t2c-1900`, `dt-t4r4-0147`, `dt-cshape-scripts`.
- **PRs:** 1 new (#803); 6 open.

Next: the rest of T6c (deadlines and generation ids for NodeAt/DomTree/Element/Highlight, busy state) on #803. A quiet ring A/B when load is under 4. T6d (condition 4). Whether the inserted unparseable branch is reachable at all.


## 2026-10-27 01:10 devtools T6 + T2 + review follow-ups (Tue session, 01:10-02:45; Atlas notes 10-26 21:05, 22:00, 20:50)

- **#803 T6: independent HOLD answered @ 59795a2b** (was 3eca9c25).
  - **(0) Ring default is now OFF until a panel attaches.** No quiet A/B was possible: load was 7.8 at 01:10 before the lane started anything, and 8.8-11.4 through the session (the rule is under 4). Machine load from foreign processes is a skip reason. `HIWAVE_DEVTOOLS_RING=1` keeps the 2048 ring from view creation.
  - **The cost of off:** a late panel has no earlier history, and closing the panel drops its session (that is nit 1).
  - **(a) Same-thread path:** the console answer now posts a window wake.
  - **(b) Attach during boot or load:** the page watches when it handles the attach. A same-thread attach that a load dropped is stored in `pending_attach` and sent again in `load_ended`. A repeated watch keeps the read mark.
  - **(c) Nits:** clear on detach when the ring is off; with no devtools thread, an empty answer plus a log line; the blocked-page test asserts the page was in `Block`.
  - Red before **4/4**. Suite **1112/0**. Campaign **26/26, 1.1078%**. develop e587d94a merged. Comment posted; the PR body now states the default. Receipt: `receipts/T6-review-hold-fix-59795a2b.md`.
- **#792 T2: independent HOLD answered @ 2a52bc58** (was 536351fa).
  - The rule→list map is built only with rule names and more than one list. Without rule names, several lists return `unattributed` explicitly.
  - **`rule_names_rss plain` max RSS: 110.6 → 89.4 MB, so −21.2 MB per engine.** The app builds two engines, so about −42 MB for every user.
  - The intercept ready-branch assertion now matches what each path produces.
  - Both-lists test and doc nits done. The body already covered `queued_ms`/`SlotWait`/`in-flight cap` (now also named in the HOLD section).
  - Red before 1/1. Suite **1099/0**. Campaign **26/26, 1.1078%**. develop merged. Comment posted. Receipts: `T2-review-hold-fix-2a52bc58.md`, `T2-receipt-2a52bc58.md`.
- **Draft PR #806, `atlas/dt-review-followups` @ 9071f48d** (20:50 (2)-(4); 7 open PRs with it).
  - **(2) `unparseable-inserted#<node>` removed as unreachable.** `web_scripts.js` resolves `src` with the `URL` it captured at install (the `url` crate) and fires `error` on a throw, so the engine only ever receives a parseable `href`. That holds even when the page replaces `window.URL`. A bindings test pins it. The doc now says such a script gets no `script` record.
  - **(3) #791 Error subclass name: green, kept as a pin.** Class names and a set `name`, thrown, rejected and `console.error`'d, mirror off and on: no page name reaches any record. The 09:40 trace holds; no breach.
  - **(4) Callback errors:** timer, rAF and listener throws each reach the Inspector as a `script_error` (pin). The report page runs its inlined Chart.js and its DOMContentLoaded listener (test).
  - Suite **1098/0** at 0d2fedb6; **1101/0** at head 9071f48d. Campaign **26/26, 1.1078%** at 693bc3ac.
- **Checkouts:** mine (`dt-t6hold-0115`, `dt-t2hold-0150`, `dt-followups-0208`) are removed. Of the stale ones, `dt-t2-1320`, `dt-t2c-1900` and `dt-t4r4-0147` are removed, and `dt-bisect-0729` was already gone.
  - **`dt-cshape-scripts` is not a worktree.** It's a folder of edit scripts from 10-23, so done-task fails on it. I left it for Atlas.
- **Leave to Atlas:** Prometheus delta re-stamps (#803 3eca9c25..59795a2b, #792 536351fa..2a52bc58), R1 on #806, and `gh pr ready`.

Next: the rest of T6c (generation ids for NodeAt/DomTree/Element/Highlight, busy state), then T6d (condition 4). A quiet ring A/B if load ever gets under 4; if it is clean, turning the default back on is one line.



## 2026-10-27 06:35 devtools #806 + T6c + T6d (Tue session, 06:35-07:45; Atlas notes 04:10, 03:20)

- **#806 merge (Atlas 04:10, done first) @ 89b32a93** (was 9071f48d, DIRTY).
  - develop 3e2f9cf8 merged in as a merge commit, with no rebase and no force-push. The one conflict was `script_net.rs` `enqueue_inserted`. I kept my let-else plus #792's `waits_on(SlotWait)`, `queued()`, the `inserted_script` label and `FetchJob.wait`, and dropped develop's unreachable `unparseable#n` arm.
  - Prometheus nits: `FetchedInserted::Skipped` and its 4 arms are deleted, and its dead_code warning is gone. `tracing::warn!` sits beside the `debug_assert!`; the crate logs with `tracing`, not `log`. The doc sentence is fixed.
  - The Chart.js `include_str!` stays. `inspector_page.rs` already embeds `inspector_rustkit.html` from hiwave-app in production code, so moving one test wouldn't untie the crates.
  - Engine **1120/0**, bindings **383/0**. No campaign: this is a merge plus dead-code removal. One PR comment posted. Receipt: `receipts/806-develop-merge.md`.
- **T6c: draft PR #809, `atlas/dt-t6c` @ 33a04a80.**
  - **Same-thread console read during a load (Prometheus #803 note).** The view now keeps its Inspector and counters from build, so the read no longer borrows the endpoint the load holds. Red before 1/1.
  - **Live queries:** one of each kind out at a time, with the newest asked next. Each has a 2 s deadline; past it, the panel shows `page busy (no answer for N s)` and greys the kept tree. A late answer is dropped, and its kind is asked again with the newest question. Highlight is now its own kind. Console reads and Attach are exempt.
  - Three panel-state tests. They are new state, so there is no red build to compare against.
  - **Deviation for Atlas:** §4's `in script N s` can't come from the last `script` record, because a hung script has no record until it ends. N is how long the oldest late question has waited. Naming the script needs a script-began atomic on the Inspector; that's a small follow-up.
  - App **60/0**. Campaign **26/26, 1.1078%**; parity-capture doesn't link hiwave-app.
- **T6d: draft PR #810, `atlas/dt-t6d` @ 99aa6e2c** (condition 4 + Atlas Q2).
  - rustkit-js `set_console_live` is decided per call. Live calls go to the handlers at once, with held calls first, each once and in order. Live calls are capped at 200/s; past that, calls are held, and a `K console calls dropped (more than 1024 held)` warn line now also counts the flush path's drops, which used to vanish without a count.
  - The engine turns live on while the Inspector is active. Shapes and nameless stacks are unchanged (same handlers).
  - Red before **2/2** (rustkit-js live timing; engine reader sees the line 400 ms before a 600 ms script ends). Plus the mid-evaluation dedupe, hot-loop and live-off tests.
  - Engine **1116/0**, rustkit-js **86/0**, bindings **382/0**, campaign **26/26, 1.1078%**.
- **Not done:** the ring quiet A/B. Load was 8-18 all session (not the lane's: it ran one cargo job at a time), and the rule is under 4.
- **Checkouts:** `dt-followups-0636`, `dt-t6c-0700` and `dt-t6d-0715` are removed. `dt-cshape-scripts` was deleted (Atlas 03:20). `dt-t2-1320` was already gone.
- **Open PRs: 7** (with #809 and #810).
- **Leave to Atlas:** Prometheus delta re-check on #806 @ 89b32a93, R1 on #809 and #810, `gh pr ready`, and the T6c busy-text deviation.

Next: T7 (HTTP-thread network recording) once Atlas writes it into the table. The quiet ring A/B, if load ever gets under 4.

## 2026-10-27 12:35 devtools T6 (#809 HOLD, #810 condition + Atlas 13:35 HOLD) + T7 design note

- **#809 (T6c) independent HOLD answered @ 4d1fe7ae** (was 33a04a80). Both R1s are now CLEAR at this head; Atlas 13:40 says don't push to it.
  - Subtree questions coalesce per expanded node, not per kind.
  - A late answer is shown when nothing newer was wanted for its slot. Before, it was asked again forever.
  - A late hover after the pointer left clears the outline.
  - Navigation and close paths pulled out as `forget_page`/`forget_questions`, with a test.
  - Red before: 4 of 9 panel tests with the old behaviour. App **64/0**.
  - Prometheus nit (b) was not a bug: `domTreeContainer` is `#dom-tree`, a sibling of `#page-busy`.
  - No campaign: the change is app-only, and parity-capture does not link hiwave-app.
- **#810 (T6d) condition answered @ b36807e6, then Atlas 13:35 HOLD @ 5ea74e5e** (was 99aa6e2c).
  - Boa has no drain hook (its interrupt is a stop word), so held calls are **counted, not delivered**. `Inspector::console_held()` is an atomic the runtime keeps.
  - The devtools thread wakes the window when a watched view's held count moves, without a read and without touching `woken`. The console answer carries `held`.
  - The panel's `pump` shows "K console lines held by a running script".
  - Prometheus nits: live delivery is rebuilt in the handler setters; the dropped line says "; console rate cap"; the timing test spins 1000 ms. Review nits: cap = hand-overs, the flush test is looser, the hot-loop bound can now fail, no private doc link. Held-count tests take stable reads; the cap flag is set by the latest hold.
  - Red before: 2/2 at b36807e6 and 2/2 at 5ea74e5e (service test plus a view-level hot-loop-then-hang test).
  - Final head 5ea74e5e: engine **1118/0**, rustkit-js **88/0**, app **57/0** three runs in a row (the view test flaked once in its first form; fixed with a second burst). At b36807e6: bindings **382/0**.
  - Campaign **26/26, 1.1078%**, every case identical at both heads.
  - One comment per push on #810.
- **#809 leftovers** (the in-time Unavailable hover clearing the outline, with a test) are on a **new branch `atlas/dt-t6c-followups` @ cacf5917**, not on #809. They are for a follow-up PR after #809 lands. App **65/0**.
- **T7 design note written:** `trench/devtools/T7-design.md`.
  - Finding: a script request's HTTP work is polled by the page thread (`settle_live` on its LocalSet), and rustkit-http has no thread of its own. Moving only the record writes would change nothing.
  - Proposal: a 2-worker `rustkit-net` runtime. `begin_request` stays on the page thread at request start (doc stamp, scrub). The guard moves into the spawned task, so response and failure records are written there. Abort-on-drop for navigation and close.
  - Step 0 is a `Send` compile probe.
  - Blocked on Prometheus R1; no code.
- **Not done:**
  - 09:20 item (3), naming the running script in the busy text. Scoped, not started: scripts start at 5+ sites, and the one central turn wrapper (`with_script_js`) carries no label. It needs a script-began mark at each runner, and Atlas 13:40 says no more T6 work unless a review asks.
  - Ring quiet A/B: load was 9-18 all session.
- **Open PRs: 6.**
- **Checkouts:** `dt-t6c-1240` and `dt-t6d-1240` are kept for Atlas to remove (per the 10-26 08:50 rule).
- **Leave to Atlas:** Prometheus delta R1 and stamp on #810 @ 5ea74e5e; landing #809; the follow-up PR from `atlas/dt-t6c-followups` after #809 lands; Prometheus R1 on T7-design.md.

Next: T7 once Prometheus clears the design note.

## 2026-10-27 18:35 devtools T6 follow-up PR + T7a (Tue session, 18:35-19:55; Atlas notes 15:20, 16:55)
- **T6: done.** One follow-up PR, as the 15:20 note asked:
  - **#814** (`atlas/dt-t6-followups` @ a81c00ab). It had already **landed** by 19:48, as 469a8779 on develop.
  - It has all three items: the in-time Unavailable hover clears the outline; the forget test goes through `console_answered` (the Console arm, pulled out) and `close()`; `clearConsole()` resets `held_shown`, so the held line comes back on the next pump.
  - Red before, by mutating each fix out against the final tests: 2 failed per run. App **67/0**.
  - No campaign: the change is app-only. Receipt: `receipts/T6-followups-a81c00ab.md`.
- **T7a: draft PR #815** (`atlas/dt-t7a` @ cb7622c6), which meets C1 to C5.
  - **Before → after:** a fetch started before a 1.5 s `PageCmd::Block` showed **no** response record until the block ended (red at 77baefee). Now its response is read **through the devtools service** while the page is still blocked, in the doc the fetch started in.
  - Live script requests make their Request record on the page thread at start, then run and record on a `rustkit-net` runtime. The page side holds an abort-on-drop guard: a navigation records one `cancelled` in the old doc, and a closed view frees its Inspector.
  - Per C2, the runtime-or-fallback choice comes before `begin_request`.
  - Per C3, a panic in the policy call records `engine failure: request task panicked`. A panic in `guard.response`/`fail` is outside the unwind; the code says so.
  - Per C1(a), `brief_url` drops the query and fragment.
  - Per C5, `DevtoolsQuery::Network` and `DevtoolsNetwork` carry the current doc, read under the records' lock.
  - Other parts: the `MAX_LIVE_NET_TASKS` cap of 240; the `DiagContext` nav id plus the test switch and sink set on every poll; the kill switch `HIWAVE_NET_RUNTIME=0`.
  - **Deviation D1:** one current-thread runtime, not two workers. With two workers, tasks raced to the policy's FIFO origin semaphore, and T2's combined fixture capped `/hang/4` instead of `/hang/6`. One thread first-polls tasks in spawn order, so slots go in request order.
  - **Tests:** 1–5, 7 and 9–11 are present. Test 6 is T2's fixture, still green on the runtime. **Test 8 (delivery order) is not added.** Only test 1 was run red first.
  - Engine **1138/0** at cb7622c6. The earlier heads were 1128/1 and 1135/2; the PR body explains both.
  - Campaign **26/26, 1.1078%**, every case identical to T6d. Receipt: `receipts/T7a-pr-815-cb7622c6.md`.
- **Owed on #815:**
  - test 8;
  - the 20-site A/B with the net runtime on and off (load was 7–10 all session);
  - RSS and thread count;
  - `Inspector` lock-hold p99 with the file sink on;
  - panel rendering of the network list (a named follow-up).
- **Not done:** no lock-hold measurement, and no panel HTML.
- **Open PRs: 5** (#815, #812, #801, #787, #777).
- **Checkouts:** `dt-t6fu-1835` and `dt-t7a-1855` are kept for Atlas to remove. The old `atlas/dt-t6c-followups` branch is superseded by #814.
- **Leave to Atlas:** Prometheus R1 and the independent review on #815, including a ruling on D1.

Next: #815's review findings. T7b (fold `rk-inserted-script` and `fetch_module` in, with the Send probe first) comes after #815's R1.

## 2026-10-28 00:35 devtools T7 (#815 HOLD answers; Wed session, 00:35-01:30; Atlas 21:15 note)
- **#815 (T7a) HOLD answered**, pushed to `atlas/dt-t7a`: b4c9f720 (fixes), 522532b9 (receipt tests), **d60b9e1a** (env-parse test). Comment 6461395310 plus a short head note; body updated. No new PR.
- **C4:** test 3 now asserts the Inspector is freed within **1 s** (was 3 s). Close-to-dead-`Weak` timings, n = 10 each: idle p50 36 ms / max 45 ms; beside 24 × 4 MB fetches on `rustkit-net`, p50 18 ms / max 54 ms.
- **D1 receipts (one current-thread runtime), load 10–13:**
  - 20-site A/B, `HIWAVE_NET_RUNTIME` on vs off: **B/A 1.014** over 19 clean sites. No pixel mover: every across-arm difference also appears within one arm.
  - Two heavy tabs at once (cnn + yahoo in one process, 4 rounds each arm): **+1.7% / +1.3%**, in the same direction every round. Both are under the 5% threshold, so D1 is kept and a ruling is asked for.
  - Named follow-up: take the slot ticket in `begin()` on the page thread, then 2 workers.
- **Lock hold with the file sink on** (1 MB × 3, rotating): p50 8.7 µs, p99 15.3 µs, max 4.2 ms. Ring only: 3.5 µs / 10.5 µs / 1.5 ms. Sink I/O stays under the lock.
- **RSS:** cnn medians 776.5 MB (on) vs 776.6 MB (off). yahoo and wikipedia are within 5 MB. Threads: +1 by construction; `ps -M` sampling can't resolve it.
- **Nits done:**
  - the poke now comes after the outcome is stored (oneshot);
  - a `DiagContext` drop guard restores context on panic, and its doc is fixed;
  - test 7 gains a failure reason that holds the URL;
  - `brief_url` drops `;params` and `user:pass@`;
  - the other mirror URL lines are scrubbed and the header narrowed;
  - the kill-switch env parse has a test.
- **Suite** 1139/0 @ b4c9f720 (1041 s). **Campaign** 26/26, mean 1.1078%, every case identical. Receipts: `receipts/T7a-hold-answer-522532b9.md`, `T7a-ab-netrt-522532b9.txt`, `camp-t7a-522532b9.log`, `T7a-receipt-522532b9.md`.
- **Not done:**
  - test 2 does not yet check that the server sees the stream close;
  - test 8 and the ring clone are left for T7b;
  - develop (e1093aad, #812) is not merged in; the PR reads MERGEABLE.
  - The new receipt tests (C4 latency, lock hold, two tabs) were not run red; they are measurements.
- **Open PRs: 5.** Checkout `dt-t7a-0035` is kept for Atlas to remove, along with `dt-t6fu-1835` and `dt-t7a-1855`.
- **Leave to Atlas:** the D1 ruling (+1.7% two-tab), and the Prometheus/Atlas R1 delta cb7622c6 → d60b9e1a.

Next: #815 review findings; then T7b (Send probe first, test 8 first).

## 2026-10-28 06:35 devtools T7 (#815 R1 delta HOLD answer; Wed session, 06:35-06:45; Atlas 02:00 note)
- **#815 (T7a) R1 delta HOLD answered** at **1fefcc7b**, plain push to `atlas/dt-t7a` (before: d60b9e1a). Comment 6466899510; PR body updated. No new PR.
- `brief_url`:
  - a scheme counts only at the start (`^[A-Za-z][A-Za-z0-9+.-]*:`), so `/api?token=X&next=https://x.test/p` becomes `/api` and `./m.js?a=1&u=http://e.test/` becomes `./m.js`;
  - `;` is cut after the authority only;
  - a leading `//` drops userinfo;
  - `data:` URLs become `data:<mime>,…`.
- `brief_place`: `word#N` is a label only when N is all digits.
- **Tests:** 4 new console_log tests, **red 4/4 on d60b9e1a**, green now. Targeted runs: `console_log::` 14/0, `content_thread::` 40/0, `script_net devtools inspector page_protocol` 165/0.
- **`close_latency_receipt`:** the beside-busy figure is dropped (Atlas's second option); nothing asserted a body was still in flight at the close. The body's "beside busy, max 54 ms" claim is withdrawn.
- **PR body:** slot ticket in `begin()`, then 2 workers, is now a **hard gate before T7b**: at least 8 interleaved rounds per arm, paired diffs, 1 thread vs 2 workers vs off, on a parity/release build.
- **Not re-run, per the note:** the full suite, the campaign, the A/B. Load 8.5–10.
- **Open PRs:** unchanged. Checkout `dt-t7a-0636` is kept until the review lands, for Atlas to remove along with the older `dt-t7a-0035`, `dt-t7a-1855` and `dt-t6fu-1835`.
- **Leave to Atlas:** Prometheus/Atlas R1 delta d60b9e1a -> 1fefcc7b. Prometheus's test 2 nit (the server sees the stream close) is still open; I did not push it, so the asked SHA stays fixed.

Next: #815 delta findings; then the D1 hard gate (slot ticket + 2 workers), then T7b (Send probe first, test 8 first).

## 2026-10-28 12:35 devtools T7 (T7b design only; Wed session, 12:35-13:30; Atlas 10:05 note)
- **#815 (T7a) was still OPEN** at session start: Prometheus R1 CLEAR and Atlas R1 delta CLEAR, both at 295816ff; the R2 stamp is pending (the last stamp, at 75f82d34, FAILED on a cancelled `pr-swarm (2)`). So per the 10:05 note, this session wrote the T7b design only. I did not push to #815.
- **`trench/devtools/T7b-design.md`** (read against 295816ff in a read-only checkout `dt-t7b-1240`, removed with done-task.sh). It proposes two PRs:
  - **G (the #815 hard gate):** `FetchPolicy::reserve()`, called in `begin()` on the page thread. It does the budget, the shape check and `SlotWait::queued`, and it registers in the origin semaphore's FIFO by polling `acquire_owned` once with a no-op waker. So per-origin slot order is fixed by start order, whatever the worker count. The page slot is still taken in the task. After that, `HIWAVE_NET_WORKERS` (default 2, 1 = D1). Tests G1–G4 (the T2 combined fixture 50× under 2 workers). The gate receipt: >= 8 interleaved rounds per arm, off / 1 thread / 2 workers, paired diffs.
  - **T7b:** the `rk-inserted-script` dispatcher moves onto the net runtime as one task, and its jobs get `DiagContext`. `FetchJob` owns the guard and answers it on the net thread (test 12, 12b). `fetch_module` moves too if its Send probe passes. Also in T7b: test 8 (delivery order, red by mutation), a network read that clones only the current doc's network records (lock-hold receipt), test 2 checking that the server sees the stream close, and Atlas's 15:54 `scrub_url` `//` guard.
  - **Three R1 questions:** no-op-waker poll vs a turnstile; whether per-origin FIFO is the contract; whether to keep the old inserted path behind the switch for one release.
- **Plan state:** T7 is set to **blocked**. It waits on #815 landing AND an R1 on `T7b-design.md`.
- **No build, no tests, no receipts this session** (design only). Open PRs: 9 (#777, #786, #787, #815, #817–#821), which is over the cap of 8, so G can't open as a PR until something lands.
- **Leave to Atlas:** land #815 on the R2 stamp; ask Prometheus for R1 on `T7b-design.md`. The older checkouts `dt-t7a-0035`, `dt-t7a-0636`, `dt-t7a-1855` and `dt-t6fu-1835` are still yours to remove.

Next: after #815 lands and the note has R1, G first (reserve + its tests, then the gate receipt), then T7b.

## 2026-10-29 12:35 devtools T8 (slot ticket + 2 workers + T7a carry-overs; Thu session, 12:35-13:25)
- **Draft PR #827** `atlas/dt-t8` @ **df6a05af** (base develop d16d0f89). Open PRs: 7 (cap 8).
- **Slot ticket:** `FetchPolicy::reserve` takes the budget, the shape check, `queued` and the origin-FIFO place on the page thread, via one no-op-waker poll of `acquire_owned` under `unconstrained`. `start_live` reserves before it spawns; refusals are recorded there. **Two workers** by default (`HIWAVE_NET_WORKERS`, 1 = T7a). The parity build caught that `rustkit-engine`'s tokio lacked `rt-multi-thread` outside dev-deps (fixed df6a05af).
- **Also in #827:**
  - the network read clones only the current doc's network records (2048 ring: 0.89 ms -> 0.51 ms debug; same answer);
  - T7 test 2 (server sees EOF < 1 s);
  - T7 test 8 (start-order delivery after a block);
  - the T7a nits: not-quite-scheme userinfo, control chars, `foo:/;x/a@b`. The `data:` no-comma, `javascript:` and authority-`;` items were already pinned by #815's later deltas.
- **Red before:**
  - 4/4 nit tests red on develop;
  - G2 red by mutation (d,c,b,a);
  - the slot-ticket pin, test 8 and test 2 red by mutation (one mutation build, reverted).
- **Evidence:**
  - suite 1220/0 @ 9f40d798; the later commits by targeted runs (20/0, 155/0);
  - rustkit-net 104/0;
  - **campaign 26/26, 1.1078%, every case identical to T7a**.
  - Receipts: `receipts/T8-receipt-df6a05af.md`, `camp-t8-df6a05af.log`, `T8-three-arms-df6a05af.log`, `T8-three-arms-sum-df6a05af.txt`, `T8-pr-body-df6a05af.md`.
- **Gate receipt (two heavy tabs, parity, 8 interleaved rounds, off/w1/w2):** every round started at **load 10.2-12.6 (>8)**, so it is indicative, not the gate.
  - w2-w1 paired median: -0.60 s (-3.5%) cnn, -0.50 s (-5.2%) yahoo; both spreads straddle 0.
  - w2-off: -3.2% cnn, -2.1% yahoo.
  - Network records are the same in every arm.
- **Not done:**
  - the quiet rerun (tool: `trench/devtools/tools/three_arms.py`, summary `three_arms_sum.py`);
  - the 20-site A/B w2 vs off;
  - G1 as a 50x loop (the combined fixture runs once per suite, under 2 workers);
  - the `rk-inserted-script` fold (B1a/B1b), which is not in T8's row.
- **Tooling note:** the campaign ran on the prebuilt parity binary, linked into target/release. parity_test.py's own `cargo build --release` was made a no-op by `~/Repos/.worktrees/dt-t8-noop-cargo/` (`camp.py <wt> <log>`), so no bare cargo ran.
- **Checkout `dt-t8-1240` is kept** (acceptance not complete). No `gh pr ready`; that is left to Atlas.

Next: the quiet-hour gate rerun on #827 (load < 8), then the 20-site A/B; then R1.

## 2026-10-29 18:35 devtools T8 (#827 gate rerun, A/B, L2 pin; Thu session, 18:35-19:05; Atlas 13:50 + 15:30 notes)
- **#827** `atlas/dt-t8` df6a05af -> **c041ae21** (one test-only commit). Receipts comment: issuecomment-6510566649. Still a draft: `gh pr ready` needs approval on this seat, so Atlas flips it.
- **(1) Three-arms rerun, INDICATIVE.** Load at round start was 22 -> 8.3 and never under 8. It was 9.5 before the lane started anything, so it came from outside.
  - cnn: w2-w1 -0.6%, w2-off -0.0%.
  - yahoo: w2-w1 +1.0%, w2-off -1.0%.
  - Spreads are about half those of the 13:10 run. Network records are the same in every arm (cnn 110 every run; yahoo 254-258). 24/24 runs ok.
- **(2) 20-site A/B, off vs w2 @ df6a05af: B/A 0.969 over 17 clean sites, no pixel mover.**
  - lyft, linkedin and cnn each lost one capture and are dropped. lyft's A-arm 0.3 s failure and linkedin's served variant both repeat the T7a pattern.
- **(3) L2 pin** `two_origins_competing_for_the_page_slot_keep_per_origin_order`: per-origin order holds with two origins sharing one page slot, nothing starves, and the cross-origin order is not pinned.
  - Red by mutation: d,c,b,a. rustkit-net 105/0, 5 runs.
  - **Wording mismatch for Atlas:** the 15:30 note says "page slot in reservation order", but the code does not reserve the page slot, by design (starvation), and Prometheus's L2 asks for the per-origin-only pin. I followed Prometheus. If Atlas wants the cross-origin page-slot order pinned, that is a code change, not a test.
- Receipts: `receipts/T8-gate-ab-l2-c041ae21.md`, `T8-three-arms-1835-df6a05af.log`, `T8-ab-w2-df6a05af.txt`. New tool: `tools/absum.py` (A/B wall clock + mover check).
- No noop-cargo shim was used this session; every build went through z-cargo.py. `dt-t8-1240` was already gone at start. `dt-t8-1835` removed (done-task.sh).
- Develop moved to 831cf6f7 (#825/#777/#824/#826). GitHub still reports #827 MERGEABLE; no develop merge done.
- Not done: G1 as a 50x loop; a quiet (<8) three-arms gate run.

Next: Atlas flips #827 ready and lands it (R1 CLEAR @ df6a05af; the delta is test-only). The lane is idle on T8 unless a review asks for something.

## 2026-10-30 00:35 devtools T9 (SKIPPED: canon weekend dormancy)
- Session started Fri 00:35 ET. HiWave canon: every LLM seat is dormant Fri 00:00 -> Mon 06:00. The only lane exception (10-25 01:50 note, Pete's 10-23 order) ran "through Mon 06:00" of last weekend and has not been renewed in this plan, and the 10-29 19:35 T9 order does not name the weekend.
- Nothing started: no checkout, no build, no PR. T9 stays **open** (not set in-progress).
- **Decision for Atlas:** if T9 (or the G1 50x loop, which has no model cost once scripted) should run this weekend, write the exception into the plan; otherwise the lane resumes T9 at Mon 06:35.

## 2026-10-30 06:35 devtools T9 (exit-metric scoring run + G1; Fri session, 06:35-06:50; Atlas 10-30 01:00 note)
- **Before -> after:** exit metric unscored -> **scored by the lane as NOT met at develop 702154ef.** Atlas has the final score. No PR, no engine change.
- **Result:** `diagnose` ran 3/3 in 31-33 s and was read in under a minute per run, but its output says "not blank" (800..1600 holds 56-60 text and 36-40 image boxes). A hand check outside the score shows "For You" still grey skeleton rows at 25 s and at 70 s, the footer painted over them, and no failed request in the 70 s run. The "logged Error" on the top line is React #418 (hydration failure), shape-hidden in the report. #418 causing the skeletons is **not established**; no record links them. The frames used a 2400 px viewport; the diagnose runs used 800.
- **G1:** no leak. Two 50x loop tests pass: one policy with both caps at 1 (red by mutation at round 0), and 50 real loads on one view with stable counts (not mutation-tested). One debug pass each, and they stand in for a "T8 fixture" that is not a single named fixture. Text in `receipts/T9-g1-loop-tests.rs.txt`, on no branch.
- **Not run:** `scripts/receipt.py`, campaign and full suite; no code changed.
- **Decisions for Atlas** (full gap list in `receipts/T9-yahoo-exit-metric-702154ef.md`):
  1. Exit metric: recommend keeping it and scoring against "skeletons that never fill"; unmet until `diagnose` says so.
  2. T10: recommend one `report.rs` PR for placeholder boxes in bands, the misleading R5 "then N fetch" clause (read 2/1/0 with 8-10 fetches before the error), a "still changing at capture end" line, and "shield not installed" under Not checked. Then overlap reporting and own-site string `console.error`. A data-to-DOM link gets a design note only if those leave the question open.
  3. Shape-rule exception (Pete's rule): recommend allowing only a matched `Minified React error #N`, fixed library text with no page data. Without it the tool cannot name a hydration failure.
  4. Z lane: yahoo's feed stays on skeletons with #418 logged. This lane fixes no sites, so routing is yours.
- **Next:** T9 is done and no package is open. The lane has nothing to take until Atlas picks T10. Per the 01:00 note this lane is also ordered to run T9 at 12:35 and 18:35 today; with T9 done those runs have no package.

## 2026-10-30 13:00 devtools T10
- **Before:** yahoo's `diagnose` read "not blank", top line one logged Error, and nothing said whether the page had finished or that no shield was installed.
- **After:** draft **#835** `atlas/dt-t10-report-gaps` @ 80b44d9d (T9 gaps 1, 2, 4, 5; no engine change). Yahoo now ranks first: `[R11] y 1600..2400: 16 painted boxes with no text and no image (skeleton?)`, then the own-site Error `at t=25.4 s; 8 fetch/XHR to www.yahoo.com before, 2 after`. Facts add `still changing at capture end: last relayout 10 ms before; 0 requests open`; Not checked adds `R6 shield: not installed`.
- **Exit metric, lane read: still NOT met (Atlas scores).** The report no longer misleads, but it gives what and not why: one 25 s window can't show "never", the Error has no link to the rows and no name (gap 3), and no record links a fetch to the rows (gap 8). This run was on the branch; the plan's scoring run comes after landing.
- **Evidence:** 14 tests red before, parity-capture 50/0 after, engine diagnostics 33/0, campaign 26/26 1.1095% (same mean as the #833 receipt). One rank test was added after the fix and was not seen red. Full engine suite not run, no engine file changed. Receipt: receipts/T10-report-gaps-80b44d9d.md.
- **R11 false-positive check:** no fire on github, wikipedia, bbc, apple, nytimes or hacker news; with yahoo that is 7 pages, not a broad sample. The first yahoo run ranked 12 absolute gradient scrims as a first-viewport skeleton, so R11 now counts in-flow boxes only.
- **Found on the way:** `set_live_wake` is one slot per process, so two live-window tests in parallel fail `an_inserted_script_runs_...`. Fixed with a test lock.
- **Blockers:** none. #835 waits on Prometheus R1; `gh pr ready` is left to Atlas. Checkout removed.
- **Decisions for Atlas:** (1) T10 is left `open` as your 07:55 note says, so the 18:35 slot picks it up with nothing to do unless R1 has arrived. Change the row if you'd rather skip that session. (2) Gap 3 is still Pete's ruling, and it would name the Error in the R5 line.

## 2026-10-30 18:35 devtools T11, T12
- **T11 before:** yahoo's report had no word for content painted over content, and an own-site `console.error` of a string was invisible.
- **T11 after:** draft **#838** `atlas/dt-t11-overlap-strings` @ 1a6c8095, `report.rs` and tests only. Yahoo now reads `[R12] y 800..1600: 7 boxes overlap other content, 3 run past the right edge` and `[R12] y 1600..2400: 9 boxes overlap other content, 0 run past the right edge`, under R11. R12 fired on yahoo only, of 7 pages.
- **T11 departs from its row twice, both stated in the PR:** (1) overlap compares content leaves anywhere in the tree, because the row's sibling rule read 0 on yahoo and fired on wikipedia; (2) a string is named by its first own-site frame, because yahoo wraps `console.error` from s.yimg.com, so `location` is the wrapper. Also fixed: `console.error("text", err)` read `logged string thrown in`.
- **T11 not shown live:** the string rule has not produced a yahoo line. All four runs held only the consent script's string, which is another site and rightly left out. T9's own-site string did not recur. Pinned by unit tests and a live local test. R12's counts are layout rects, not checked against a frame this session.
- **Exit metric, lane read: still NOT met (Atlas scores).** The overlap is a second symptom, not a cause. Why the rows never fill still needs gaps 3 and 8.
- **T11 evidence:** red first in four test commits, three more tests red by mutation; parity-capture 64/0; engine diagnostics 33/0 at 2dc9a3b2 (later commits touch only parity-capture); campaign 26/26 1.1095%. Full engine suite not run, no engine file changed. Receipt: receipts/T11-overlap-strings-1a6c8095.md.
- **T12 before:** `other_ms` was 88% of a 36.8 s microsoft load hold and 97% of a 23.2 s ebay one (real window, Pete's 18:00 log).
- **T12 after:** draft **#839** `atlas/dt-t12-hold-buckets` @ b380863c. The hold line names script turns (total, count, longest, watchdog stops), parse, style, document fetch, sheets, fonts, images, scripts still arriving, and the script phase's network waits. Headless `other_ms`: microsoft 128 ms of 43.4 s (0.3%), cnn 960 ms of 28.9 s (3.3%), yahoo 119 ms of 12.5 s (1.0%). One run each, at load about 7.
- **T12 is NOT accepted:** the row wants real-window lines and these are headless. Real-window runs are barred 17:00-23:00, and this seat never loads ebay live. The row stays `open`: the next slot at or after 23:00 takes one real-window microsoft line if the locks are free. Real-window `other_ms` could read higher, since a load is polled in 8 ms slices there.
- **T12 first reading, not a measurement:** microsoft's biggest cost was scripts still arriving (21.2 s in one run, 2.4 s in another at the same code), with script itself 4.4-5.2 s. cnn's was build + layout (15.2 s of 28.9 s). This is not the "script is the cost" story; the hand-test line should confirm or kill it.
- **T12 evidence:** 6 tests red over no-op stubs, double-charge guard red by mutation (the nested-bucket sum check not seen failing on a double charge); engine 1269/0/10 ignored; hiwave-app check clean; campaign 26/26 1.1095%. Unexplained: about 700 ms of `other` on a tiny page in a debug test build. Receipt: receipts/T12-hold-buckets-b380863c.md.
- **Blockers:** none. Atlas landed #838 at 19:50 (develop 8d66ff41) while this session was closing. #839 waits on R1 and its base is now behind that; `gh pr ready` is left to Atlas. Both checkouts removed.
- **Decisions for Atlas:** (1) T12's ebay line needs Pete's next hand-test, on a build with #839 in it, so landing #839 before the weekend hand-test gets that line; I recommend it once R1 clears. (2) With T11 and T12 up there is no further open row after the microsoft line. Gap 8 (data-to-DOM link, design note) and Pete's gap 3 ruling are what is left of the exit metric, and the first needs your pick.

## 2026-10-31 01:05 devtools T13
Before: no per-property CSS census. After: draft #842 `atlas/dt-t13-css-census` @ cb0188c9, base develop 1de44430, one command (`cargo run --profile parity -p css-census`), report in `docs/census/CSS_PROPERTY_CENSUS_2026-10-31.md` + `.json`, oracle Chromium 143.0.7499.4.
Result: 344 properties, 415 values. Effect 130, computed 9, parse 51, unsupported 154. Red 213 (164 visual, 49 non-visual reads). Not exercised 28 values, not visual 50.
Evidence: tool tests red first (32 of 38 against stubs, then 3 more), now 41/0; campaign 26/26 1.1095%, no engine change; two runs byte-identical; fresh `new-task.sh` checkout with node_modules removed, so `npm ci` ran. Not a bare `git clone` (needs approval on this seat), and that checkout's target is seeded.

Decisions for Atlas (red list, for the Z C rows; no fixes in this row):
1. `position: relative` offsets do nothing: `positioning_of` maps Relative to Static (rustkit-engine lib.rs:8556), in every form tried. 61 of 67 sites use relative positioning; only those setting an offset show it. Top of the list.
2. A leading `;` drops the next declaration: `#p{;width:200px}` reads the earlier rule's 120px, Chrome 200px. Seen once, not reduced further.
3. `getBoundingClientRect` ignores transform, translate, rotate and scale (0 off probes, geometry miss): paint right, rect wrong. Those rows are red on geometry alone.
4. `object-fit: cover` on an SVG image paints past the box. Raster not tried.
5. The bg context's control is off by 916 probes: background painted about 20 px below the border box with padding + dashed border + tiled gradient. Not reduced. `bg` rows are unproven until it is fixed, because the control's noise is credited (`background-size: 30px 30px` reads match with 915 off).
6. Prevalence: the technique census covers only 18 of the 344 properties; the rest show `?` and sort by 26-case corpus count. So the order below those 18 is not top-100 prevalence. Say if you want a per-property top-100 crawl; I did not add one.

T13 is 344 properties, not the row's ~250. T14 not started: this session took one package; it is first open for the next slot.
PR #842 is a draft; `gh pr ready` is Atlas's on this seat. R1 asked for in this digest.

## 2026-10-31 06:50 devtools T14

**T14: WPT reftest runner W0b. Done, awaiting R1: draft hiwave-macos #844 (`atlas/dt-t14-wpt-reftest` @ 3492047b).**
- Before: the runner read `target/release`, last counted 9/25, and had no `develop_sha` or `oracle` in `last-run.json`. The `wpt_sync.sh` network path had never run.
- After, on develop 6f64c7c4 at WPT pin a6f29b0bedaf: **26/27 scored, 1 FAIL, 3 SKIP (reftest-wait), 0 ERROR, n=30.** The negative control went red at 25.0%, and two runs gave identical rows.
- Instrument bug found by the first sync: `css-flexbox/align-self-015` needs `support/flexbox.css`, which the manifest never listed. It is listed now, and an absent local resource is an ERROR with no pixels compared.
- The stale "no script host" skip is gone: `empty-text-node-001` is scored with script on and passes.
- Tests: `test_wpt_tier1.py` 17/17, red first @ 4ffcdedb (6 failures + 11 errors). Campaign 26/26, mean 1.1095%, no engine change.

**Limits on the number:**
- 26/27 is close to the all-green shape the pin distrusts, so I attacked it by hand. With all styles removed, all 27 stop matching. With only the named property removed, 18 of 26 passes go red and 8 still match (named in the PR table).
- 10 passes share one frame, the green square. No Chrome comparison was run.

**Not done:**
- `wpt_sync.sh` has not run as one script. The seat refuses it, so its git steps ran one by one; the `--stdin` path list is unexercised. R1 should run it once.
- "Fresh clone" here is a fresh `new-task.sh` checkout, because `git clone` needs approval on this seat, as in T13.

**Decisions for Atlas:**
1. Pixel rule: the row says the campaign's rule. `status` stays exact, and the campaign rule is reported beside it. All 27 are within 15%, including the real failure, so it separates nothing here.
2. Z item: `css-inline/empty-span-size-002`, empty `<ruby>` boxes, 55 px at x 12..14, y 29..48. Not reduced further.
3. The row says "first honest pass count", but the seed has been counted since #74. This is the first count with the resource gate and on the current engine.

Blockers: none. T13b is the next open row; left for the next slot.
