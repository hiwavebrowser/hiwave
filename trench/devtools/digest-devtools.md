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
