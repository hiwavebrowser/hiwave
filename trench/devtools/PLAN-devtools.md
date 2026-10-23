# Dev-tools lane plan (macOS seat)

end_date: 2026-11-20
exit_metric: `diagnose https://www.yahoo.com/` explains why the below-fold feed is blank in under 5 minutes, with no hand digging (scored by Atlas)
owner: Dev-tools lane (Claude, launchd com.alephnull.trench-devtools). Stood up by Pete 2026-10-23 08:50 ET.

This lane reads ONLY this file. Orders from Atlas go in at the first `> **` line below.

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
| T1 | done (draft #784 @ 7f5d8301, awaiting R1) | **JS exception stacks.** Every uncaught exception, rejected promise and console.error from page script reaches the event log / receipt with message, stack (frames: function, script URL, line, col) and the script's origin (inline #n, src URL, inserted-by). | A test page that throws three frames deep shows all three frames with correct URL:line:col; on yahoo (headless live, 25 s) the #777 TypeError ("cannot convert 'null' or 'undefined' to object", chunk 7730) appears with its stack. Paste that stack in the PR body. |
| T2 | open | **Network facts.** One record per request: URL (origin+path, no query in logs), initiator (parser / inserted script / fetch / XHR / css / font / image), result (loaded status+bytes+ms, blocked by shield with list name and rule, timed out, capped by an in-flight/queue cap, cancelled by navigation). | Fixture with a shield-listed host, a timeout and a cap overflow shows each with the right result. On yahoo, answers Trace's #832 question: is the static-asset request blocked by our shield, and which list/rule. |
| T3 | open | **Script lifecycle per tab.** For each script: discovered, fetched (ms), parsed, ran (ms), load/error fired, over budget, stopped by watchdog, skipped (size cap, reason). Window-load/DOMContentLoaded holds and what held them. | Fixture covering each state; on cnn the consent script shows as an inserted script that held window load (the beb6f228 behaviour) without a bisect. |
| T4 | open | **`diagnose <url>` command** (headless, one page of text + JSON): page state (element count, doc height, scroll lock: body/html overflow+position, top fixed/overlay boxes covering the viewport with selector), T1 errors, T2 blocked/failed requests, T3 slow/stopped scripts, holds. Ranked "most likely cause" list at the top, facts only below. | yahoo diagnosis in under 5 min wall clock by someone who has never seen the page; cnn shows "scroll locked by fixed overlay <selector>" at the top. |
| T5 | in-progress (`atlas/dt-mac-gates` @ 4fa6d6f8: 5 of 6 fixed; remote_web_fonts left, see digest) | **Clean Mac gates.** The five localhost tests (referrer x3, image_loader_routing, remote_web_fonts) and error_page_script_tests::navigating_away_drops_an_inserted_script_still_fetching fail on every Mac run. Find why (IPv6 ::1 vs 127.0.0.1, sandbox, port reuse, timing) and fix the tests or the code. | `cargo test -p rustkit-engine --features headless --lib` 0 failed on the Mac, 3 consecutive runs. |

Order: T1 first (it unblocks #777), then T2, T3, T4. T5 may be taken whenever a session has under 45 min left.

## Rules
- Engine code is hiwave-macos. FRESH CHECKOUT per package: `~/Repos/.worktrees/new-task.sh dt-<pkg>-<HHMM> develop`; all cargo through `python3 ~/Repos/.worktrees/z-cargo.py <worktree> <args>`; never bare cargo; never touch ~/Repos/hiwave-macos. After push + passing acceptance: copy small text receipts to trench/devtools/receipts/ on the hub, then `~/Repos/.worktrees/done-task.sh <name>`.
- Branch `atlas/dt-<slug>`, one draft PR per package to develop. A test that is red before the fix, the receipt (`scripts/receipt.py`) and the 26-case campaign at the candidate SHA in the PR body. Logging must cost nothing measurable when off; say what it costs when on.
- Public repo: no live-site dumps, HARs, cookies or full URLs with query strings in the repo or PR comments; summarise. Never load ebay.com live.
- Real window (Mac GUI) only 23:00–17:00 and only if ~/.claude/z-window.lock and ~/.claude/board-quiet.lock are free; prefer headless.
- Never merge your own PR, never force-push, no pings. Atlas lands on R1 CLEAR + green CI + Mac evidence.
- Stop rule: second consecutive session on a package with no pushed progress → set it blocked with a one-line decision packet and move on.
- Before stopping: append `## <date> <HH:MM> devtools <pkg>` to trench/devtools/digest-devtools.md (before → after, PRs with SHAs, blockers), update the state column here, commit and push atlas/z.
