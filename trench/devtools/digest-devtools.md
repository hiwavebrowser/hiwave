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
