# T6: devtools service thread (T6a + T6b + Prometheus R1 conditions + T6c so far)

Branch `atlas/dt-service` @ 3eca9c25, develop 68f4c8e1 merged in. Design: `T6-design.md` (lane hub), Prometheus R1 CLEAR with 7 conditions (exchange 10-26 10:04Z). Dev-tools lane, package T6.

**Goal (Pete 10-23):** detach devtools from what is displayed. The panel keeps its console, network and script history, and stays usable when the page is hung, crashed, mid-navigation or replaced. Only live DOM and computed-style snapshots need the page thread.

## T6a: console reads off the page thread
- **`DevtoolsCounters`** (`rustkit-engine/src/devtools_service.rs`) count devtools page commands and window wakes, per page and per process. `HIWAVE_DEVTOOLS_COUNTERS=1` logs the totals once a second.
- **One `devtools` thread per process**, started on first use. It answers console reads from the view's `Arc<Inspector>` ring. The window thread never takes the Inspector lock.
- `ContentThread::devtools_ask` and `RustKitView::devtools_ask` send `Console` to the service. `Attach`, `Highlight`, `NodeAt`, `DomTree` and `Element` stay page commands, sent only on user action.
- Red before: `content_thread::tests::an_open_panel_on_an_idle_page_costs_the_page_no_devtools_commands`. An idle page with the panel open for 2 s: **5 devtools page commands with develop's routing, 0 after.**

## T6b: push, not poll; history kept
- **Push watermark.** Every push moves an atomic watermark. The lock guard releases the lock, then stores the watermark, then signals the service only if a panel watches the view. With no panel this costs one atomic store and one load per lock that pushed.
- **#785's 250 ms `CONSOLE_POLL` is removed.** The panel asks only when the watermark is past what it has shown. **Idle panel: 0 wakes and 0 page commands per second.**
- **`doc` on every record** (bumped at each navigation start). The panel draws a divider per document and dims earlier documents.
- **Detach keeps history.**
- **Tab ring on by default:** `TAB_RING_CAPACITY = 2048` (Atlas raised it from 512 because one yahoo load lost `navigation_start`). `HIWAVE_DEVTOOLS_RING=0` turns it off.
- Red before (by mutation): `a_console_read_is_answered_while_the_page_thread_is_blocked` (`PageCmd::Block(3000)`), `an_open_panel_is_woken_when_the_view_records_and_not_otherwise`, `the_panel_reopens_with_history_marked_by_document`: **0/3** with the changes off.

## Prometheus's 7 R1 conditions
| # | condition | status | test |
|---|---|---|---|
| 1 | lost wakeup | The service re-reads watched watermarks under the inbox mutex before sleeping. 1 s backstop while a panel is open; no clock otherwise. | `devtools_service::tests::a_push_between_the_re_read_and_the_wait_still_wakes_the_panel` |
| 2 | page panic while holding the Inspector lock | Reads recover with `into_inner`. Answers carry `page_crashed` and the panel prints `page crashed`. | `content_thread::tests::a_page_thread_panic_holding_the_inspector_lock_does_not_blank_the_panel` |
| 3 | tab lifetime | Watches hold `Weak<Inspector>`. 20 tabs closed with their panels still marked open: **0 rings alive**. A full 2048 ring is about 301 KiB of payload per tab. | `devtools_service::tests::closed_tabs_free_their_rings_with_the_panel_still_open` |
| 4 | per-call console decisions, mid-eval dedupe, hot-loop cap, shape-only stacks | **not in this PR**: T6d | — |
| 5 | generation ids and deadlines on live queries | **started** (T6c below). Eval done; NodeAt/DomTree/Element/Highlight to come. | `content_thread::tests::a_devtools_eval_reached_past_its_deadline_is_cancelled_not_run_late` |
| 6 | `doc` stamped at request start | `open_requests` maps id → doc | `inspector_tests::a_network_answer_is_stamped_with_the_document_its_request_started_in` |
| 7 | redaction at record time, service-side second guard | `answer()` re-applies the URL rule | `devtools_service::tests::the_service_strips_a_query_that_got_past_record_time_redaction` |

Conditions 1, 2, 3, 6 and 7 together were red before: **0/5** with the changes off, 5/5 on.

## T6c so far
- `PageCmd::DevtoolsEval` carries a deadline. A page that reaches it late answers `EVAL_CANCELLED` and never runs it. The page also skips it if the panel has already dropped the receiver.
- The panel gives up after 5 s and drops the receiver, so a late reply is discarded.
- Red before: the late eval ran.
- **Left:** deadlines and generation ids for NodeAt/DomTree/Element/Highlight, one outstanding query per kind, and the 'page busy (in script N s)' state. The panel checks its deadline only on a live wake, so on a hung page with no wakes the cancel shows at the next wake.

## develop merge (68f4c8e1)
- One conflict, in `inspector.rs` `State`. I kept T6's `open_requests` id → doc map alongside T3's lifecycle fields and `ScriptEnd`.
- T3's two tests that assumed nothing records by default now turn the ring off (`ring_off()`):
  - `a_page_throwing_any_engine_message_is_a_page_record_with_no_text` (456 errors plus a script record per script outgrow 2048);
  - `with_nobody_listening_no_script_record_is_built`.
- Under the full suite, the lost-wakeup test's global hook could be taken by another test's service pass before this test's read. It is now set after the read, and still runs between the re-read and the wait (3eca9c25).

## Gates at 3eca9c25
- `cargo test -p rustkit-engine --features headless --lib`: **1107 passed, 0 failed**, 6 ignored.
- Targeted `script_lifecycle inspector devtools content_thread page_protocol`: 165/165. hiwave-app `devtools` 2/2.
- **Campaign 26/26, mean 1.1078%**, unchanged from develop. Worst: article-typography 4.79%, about 3.70%, form-controls 3.24%.

## Cost of the ring
- **2048 ring, 20-site wall-clock A/B at 9eba090c:**
  - No pixel mover. Every across-arm difference also shows within one arm (served variants).
  - Wall-clock B/A 1.028 over 16 sites, but at load 8-12. microsoft and github hit the 30 s limit on both arms, so they are out of the A/B (Atlas 10-26 08:50).
- At 512 (T6b, eb8bcc65) it read 0.992 with no mover.
- **Quiet A/B: PENDING.** Atlas's rule is load under 4; this session's load was 7-9 throughout. The ring stays on by default, and `HIWAVE_DEVTOOLS_RING=0` turns it off if the quiet A/B moves.

## Overlap
T3 (#797) is in through develop. #792 (T2) touches `inspector.rs` (network records) and `docs/INSPECTOR_EVENT_LOG.md`. Whichever lands second merges develop.

<details><summary>scripts/receipt.py</summary>

## Receipt (`scripts/receipt.py`)

```json
{
 "base_sha": "68f4c8e1",
 "binary": "target/parity/parity-capture",
 "binary_mtime_utc": "2026-10-26T23:28:28.239119Z",
 "binary_sha256": "482e928140947aaf3008eaccd1d06d4faf05cf157888dd53c54acd0740657e43",
 "branch": "t6pr-1905",
 "campaign": {
  "cases": 26,
  "failed": 0,
  "file": "scratch/camp-t6-3eca9c25.json",
  "mean_diff_pct": 1.1078,
  "passed": 26,
  "sha256": "bedaa14fe5aa703edf3b919919545e82e9e57b93113a3ca85b7b66295d6d74a8",
  "timestamp": "2026-10-26T19:28:41.418262"
 },
 "candidate_sha": "3eca9c25ca5ac8ac8c8cacf537e56afc17c237b6",
 "cargo": "cargo 1.91.0 (ea2d97820 2025-10-10)",
 "cargo_lock_sha256": "d43bf3f40c046d3d625a2876c81a524fcaac59b37460f330942147537a4c8cb7",
 "chrome_version": null,
 "cpu": "arm",
 "dirty_state": false,
 "effective_engine_flags": {},
 "features": "headless",
 "host": null,
 "note": "T6a+T6b+R1 conditions+T6c start, develop merged",
 "os": "macOS-26.5.2-arm64-arm-64bit",
 "profile": "parity",
 "raw_runs": [],
 "repo": "https://github.com/hiwavebrowser/hiwave-macos.git",
 "rustflags": null,
 "sccache": true,
 "target": "aarch64-apple-darwin",
 "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)",
 "utc": "2026-10-26T23:29:36.221750Z",
 "work_package": "T6"
}
```


</details>

🤖 Generated with [Claude Code](https://claude.com/claude-code)
