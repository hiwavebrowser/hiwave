# Dev-tools lane plan (macOS seat)

end_date: 2026-11-20
exit_metric: `diagnose https://www.yahoo.com/` explains why the below-fold feed is blank in under 5 minutes, with no hand digging (scored by Atlas)
owner: Dev-tools lane (Claude, launchd com.alephnull.trench-devtools). Stood up by Pete 2026-10-23 08:50 ET.

This lane reads ONLY this file. Orders from Atlas go in at the first `> **2026-10-23 17:35 (Atlas): the console.message redaction leak you found (mirror on skips set_console_redaction) is a separate small PR, NOT part of #784. Do it FIRST next session, before T2 (C): rustkit-js builds both a text line and a shape line; the Inspector gets the shape unless keep_console_text; red-before test with the mirror on and keep off. Branch atlas/dt-console-shape, draft PR to develop. Then resume T2 at (C).**

> **2026-10-23 12:00 (Atlas): #784 (T1) is R1 HOLD @7f5d8301 (Prometheus review 5630208550), one must-fix. Do this FIRST, on branch atlas/dt-js-stacks, no force-push:** inspector_glue::attach sets runtime keep_text=true whenever the HIWAVE_CONSOLE_LOG mirror is on, so with the Inspector listening and keep_error_text off, page function names reach script_error.stack / console.stack / console.error_stack (and script_error.message already leaks that way on develop). Gate function names AND message on inspector.keeps_error_text() in stack_text/script_error; add a mirror-on/keep-off test that is red before. NITs in the same push: sanitize newline and paren in page_stack function names (forged frame line), gate inserted_by on located, add one clean GPU inspector_page_tests run to the receipt, doc note. Post the new head on the PR; Prometheus re-checks the delta. Then T2.

> **2026-10-23 10:35 (Atlas): T1 is up as #784 @7f5d8301, CI green, R1 requested.** Pete 10:23 ET privacy rule applies to every devtools output: SHAPE-ONLY EVERYWHERE. Exception messages may stay (engine text), but console argument values are shapes (`<string len=13>`), no page text, and every URL (stack frames, network records, reports) drops query string and fragment. If #784 shows page values or full URLs, fix that on its branch first (no force-push), then go on to T2. #785 (Z lane Inspector panel) also touches rustkit-engine lib.rs; whoever lands second merges develop.

> **` line below.

## Why this lane exists
Pete's standing rule (2026-10-22): tooling first. On 10-22/23 the yahoo hunt, #777 and the cnn
"regression" each cost hours rebuilding facts the browser could have logged:
- #777 is stuck because the event log does not carry a JS exception's stack;
- yahoo waits on someone checking by hand whether our shield blocked a static-asset request;
- cnn took a 25-commit real-window bisect to find a consent dialog that a page-state dump shows at once.
This lane makes a broken page explain itself. It does NOT fix sites; it builds the instruments.

## Packages (take the first open one, in order)
| id | state | package | acceptance |
|---|---|---|---|
| T1 | done (draft #784 @ 857b0e1e: R1 HOLD must-fix + 4 nits answered 13:19, awaiting Prometheus re-check) | **JS exception stacks.** Every uncaught exception, rejected promise and console.error from page script reaches the event log / receipt with message, stack (frames: function, script URL, line, col) and the script's origin (inline #n, src URL, inserted-by). | A test page that throws three frames deep shows all three frames with correct URL:line:col; on yahoo (headless live, 25 s) the #777 TypeError ("cannot convert 'null' or 'undefined' to object", chunk 7730) appears with its stack. Paste that stack in the PR body. |
| T1b | done (draft #791 `atlas/dt-console-shape` @ 58800963: red-before test, campaign 26/26 1.11%; awaiting R1) | **Console redaction with the mirror on.** | Red-before test: mirror on, keep_console_text off, Inspector sees shapes only. |
| T2 | in-progress (19:00 session on (C) parity-capture --shield; `atlas/dt-net-facts` @ 3792a2e1: block reason end to end + shield names list/rule; see T2-design.md + digest) | **Network facts.** One record per request: URL (origin+path, no query in logs), initiator (parser / inserted script / fetch / XHR / css / font / image), result (loaded status+bytes+ms, blocked by shield with list name and rule, timed out, capped by an in-flight/queue cap, cancelled by navigation). | Fixture with a shield-listed host, a timeout and a cap overflow shows each with the right result. On yahoo, answers Trace's #832 question: is the static-asset request blocked by our shield, and which list/rule. |
| T3 | open | **Script lifecycle per tab.** For each script: discovered, fetched (ms), parsed, ran (ms), load/error fired, over budget, stopped by watchdog, skipped (size cap, reason). Window-load/DOMContentLoaded holds and what held them. | Fixture covering each state; on cnn the consent script shows as an inserted script that held window load (the beb6f228 behaviour) without a bisect. |
| T4 | open | **`diagnose <url>` command** (headless, one page of text + JSON): page state (element count, doc height, scroll lock: body/html overflow+position, top fixed/overlay boxes covering the viewport with selector), T1 errors, T2 blocked/failed requests, T3 slow/stopped scripts, holds. Ranked "most likely cause" list at the top, facts only below. | yahoo diagnosis in under 5 min wall clock by someone who has never seen the page; cnn shows "scroll locked by fixed overlay <selector>" at the top. |
| T5 | in-progress (`atlas/dt-mac-gates` @ 4fa6d6f8: 5 of 6 fixed; remote_web_fonts left, see digest) | **Clean Mac gates.** The five localhost tests (referrer x3, image_loader_routing, remote_web_fonts) and error_page_script_tests::navigating_away_drops_an_inserted_script_still_fetching fail on every Mac run. Find why (IPv6 ::1 vs 127.0.0.1, sandbox, port reuse, timing) and fix the tests or the code. | `cargo test -p rustkit-engine --features headless --lib` 0 failed on the Mac, 3 consecutive runs. |
| T6 | open | **Devtools service thread.** Move the Inspector's server side off the page thread: the page thread (and network threads) only append records to a bounded per-tab buffer and answer explicit DOM/computed-style snapshot requests; one devtools thread per process owns the buffers, applies the shape-only rule, and serves the panel and `diagnose`. No polling of the page thread; the page is never woken for a console/network read. Design note first (half a page, Prometheus R1), then the change. | With the Inspector open on an idle page, page-thread wakes per second = 0 from devtools (counter in the receipt); console/network reads served with the page thread blocked in a long script; #785's rate limit can be removed. Pete 10-23: the point is to DETACH devtools from what is displayed: the panel keeps its console/network/script history and stays usable when the page is hung, crashed, mid-navigation or replaced (records kept across navigation, marked per document); only live DOM/computed-style snapshots need the page. |

Order: T1 first (it unblocks #777), then T2, T3, T4, then T6 (after #785 lands; it builds on #785's protocol). T5 may be taken whenever a session has under 45 min left.

## Rules
- Engine code is hiwave-macos. FRESH CHECKOUT per package: `~/Repos/.worktrees/new-task.sh dt-<pkg>-<HHMM> develop`; all cargo through `python3 ~/Repos/.worktrees/z-cargo.py <worktree> <args>`; never bare cargo; never touch ~/Repos/hiwave-macos. After push + passing acceptance: copy small text receipts to trench/devtools/receipts/ on the hub, then `~/Repos/.worktrees/done-task.sh <name>`.
- Branch `atlas/dt-<slug>`, one draft PR per package to develop. A test that is red before the fix, the receipt (`scripts/receipt.py`) and the 26-case campaign at the candidate SHA in the PR body. Logging must cost nothing measurable when off; say what it costs when on.
- Public repo: no live-site dumps, HARs, cookies or full URLs with query strings in the repo or PR comments; summarise. Never load ebay.com live.
- Real window (Mac GUI) only 23:00–17:00 and only if ~/.claude/z-window.lock and ~/.claude/board-quiet.lock are free; prefer headless.
- Never merge your own PR, never force-push, no pings. Atlas lands on R1 CLEAR + green CI + Mac evidence.
- Stop rule: second consecutive session on a package with no pushed progress → set it blocked with a one-line decision packet and move on.
- Before stopping: append `## <date> <HH:MM> devtools <pkg>` to trench/devtools/digest-devtools.md (before → after, PRs with SHAs, blockers), update the state column here, commit and push atlas/z.
