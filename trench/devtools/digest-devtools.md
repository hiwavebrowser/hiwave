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
