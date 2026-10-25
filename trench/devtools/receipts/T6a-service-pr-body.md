# T6a: devtools service thread answers console reads (draft body; open when under the PR cap)

Branch `atlas/dt-service` @ 8356804c, on develop ff6ad36a. Design: `T6-design.md` (hub), shapes 1 and 2 for console only. Prometheus R1 on the design is still required before this becomes a PR (Atlas 10-24 21:00).

## Before
Every console read the open Inspector panel made was a `PageCmd::Devtools { Console }` that the page thread answered between its turns. #785's 250 ms `CONSOLE_POLL` makes that about four page commands a second on an idle page, and none at all while the page is in a long script.

## After
- **`DevtoolsCounters`** (`rustkit-engine/src/devtools_service.rs`). Per-page and process-wide atomics count two things: devtools page commands handled in `PageEndpoint::apply`, and window wakes posted for devtools answers. They are read through `ContentThread::devtools_counters()`. `HIWAVE_DEVTOOLS_COUNTERS=1` logs the process totals once a second from the devtools thread.
- **One `devtools` thread per process**, started lazily on the first console read. It answers console reads from the view's `Arc<Inspector>` ring. Records are redacted when recorded, so it serves them as they are. When the answer has something new it posts the window's live wake, the same rule as `devtools_wakes_window`. The window thread never takes the Inspector lock.
- The content thread's `Boot` carries the view's `Arc<Inspector>` and counters (this is the "one extra reply field on view creation").
- `ContentThread::devtools_ask` sends `Console` to the service. `Attach`, `Highlight`, `NodeAt`, `DomTree` and `Element` stay page commands, sent only on user action.
- `RustKitView::devtools_ask` uses it. The same-thread path reads the endpoint's Inspector the same way.
- Unchanged here (T6b): `CONSOLE_POLL` / `ConsolePoll`, the push watermark, `doc` on records, no clear on detach.

## Red-before test
`content_thread::tests::an_open_panel_on_an_idle_page_costs_the_page_no_devtools_commands`. The setup: an idle page, panel attached, console reads on the panel's 250 ms clock for 2 s, and one `console.log` at 1 s.
- With console reads routed to the page (develop's routing): **5 devtools page commands** in 2 s, so the test fails. The design note guessed about 8; this loop waits for each answer and for the 1 s eval, which is why it reads fewer.
- After: **0**, and the late line (`<string len=4>`) reaches the panel.

## Tests (8356804c, debug, `--features headless`, load 11-17 from foreign processes)
- engine `content_thread` 27/27, `devtools` 18/18, `inspector` 97/97, `page_protocol` 1/1;
- hiwave-app `devtools` 2/2 (both panel tests; hiwave-app builds).
- Full engine lib suite not run this session.

## Cost
- Off (no panel): nothing new on any page path. The thread starts only on the first console read. Each devtools page command adds two relaxed atomic adds.
- On: one channel send per console read, instead of a page command.

## Campaign (26 cases, parity-capture built at 8356804c, `--profile parity`)
Passed 26/26, mean 1.1078%, the same as develop. Worst: article-typography 4.79%, about 3.70%, form-controls 3.24%.

## Receipt (`scripts/receipt.py`)
```json
{"base_sha": "ff6ad36a", "binary_sha256": "f3e42ef7f6a6385ea645a66654b7fda87a1a9b79917cfb1836a257a08ca0caed",
 "campaign": {"cases": 26, "failed": 0, "passed": 26, "mean_diff_pct": 1.1078,
              "file": "scratch/camp-t6a-8356804c.json",
              "sha256": "3d1a1325c3b6a00a362954ce338635b4e9f5949ded10ab714e03d90f69c0837a"},
 "candidate_sha": "8356804c15abd07540ead6c9a625bc938c7c3f85",
 "cargo_lock_sha256": "d43bf3f40c046d3d625a2876c81a524fcaac59b37460f330942147537a4c8cb7",
 "dirty_state": false, "profile": "parity", "features": "headless",
 "os": "macOS-26.5.2-arm64-arm-64bit", "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)",
 "utc": "2026-10-25T04:51:41Z", "work_package": "T6a-devtools-service"}
```

Overlap: #792 (T2) and the T3 branch touch `rustkit-engine/src/lib.rs` module lists and `page_protocol.rs`. The hunks here are adjacent-line additions, so whichever lands second merges develop.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
