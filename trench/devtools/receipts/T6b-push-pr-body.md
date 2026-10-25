# T6b: devtools push watermark, no console poll, doc marks, tab ring

Branch `atlas/dt-service` @ eb8bcc65, stacked on T6a (8356804c), on develop ff6ad36a. **No PR yet:** the cap is still 9 open of 8, and Prometheus R1 on `T6-design.md` comes before any T6 PR.

## Why
After T6a the page thread answered no console reads, but the open panel still asked every 250 ms (#785's `CONSOLE_POLL`). Closing the panel emptied the view's buffer, so a panel opened late, or reopened, had no history. Records did not say which document they came from. All three are in the T6 design (shapes 3 and 5) and in Atlas's 10-24 07:50 decisions (Q1: a 512-record ring per tab, on by default unless the A/B moves something).

## What changed
- **Push watermark** (`rustkit-engine/src/inspector.rs`).
  - Every push moves an atomic watermark (the `seq` the next record gets).
  - The Inspector lock is now a guard (`Locked`). It releases the lock first, then stores the watermark. If a panel watches the view, it then signals the devtools thread.
  - Cost with no panel: one atomic store and one atomic load per lock that pushed.
- **Devtools thread** (`devtools_service.rs`).
  - One condvar now carries both console reads and record signals.
  - While a panel is open, its view is watched. When the view records past what the panel last read, the window is woken once, and not again until the panel reads.
  - `Attach(true)` / `Attach(false)` start and stop the watch, through `ContentThread::devtools_ask` and `RustKitView::devtools_ask`.
- **Panel** (`hiwave-app/src/devtools_panel.rs`).
  - `ConsolePoll` and `CONSOLE_POLL` are removed.
  - `pump` asks for console lines only when the view's watermark is past what it has shown. That check is one atomic load; the window never takes the Inspector lock.
  - `main.rs` no longer schedules a panel wake.
- **`doc` on records.** `InspectorRecord.doc` and `DevtoolsConsoleEntry.doc` name the document: 0 before the first navigation, bumped at each navigation start.
  - The event-log JSON gains `"doc"` after `"seq"` (`#[serde(default)]` reads old logs).
  - The panel's HTML does not group by document yet; the field is in its payload.
- **No clear on detach.** `Attach(false)` puts recording back to the view's default and keeps what was recorded (`Inspector::detach_panel`).
- **Tab ring.** `EngineConfig::default()` now keeps a 512-record ring per view (`InspectorConfig::tab()`, `TAB_RING_CAPACITY`). `HIWAVE_DEVTOOLS_RING=0` leaves it off until a panel attaches. parity-capture inherits it, so the campaign and the A/B exercise it.
- **Test hook.** A test-only `PageCmd::Block(ms)` holds the page thread in a host-side wait.

## Tests (red before)
New, in `content_thread::tests` unless noted:
- `a_console_read_is_answered_while_the_page_thread_is_blocked`: the page thread sits in `Block(3000)`, and a console read must be answered within 1 s with the line logged before the block.
- `an_open_panel_is_woken_when_the_view_records_and_not_otherwise`, with the panel watching:
  - 1 s on an idle page: 0 window wakes and 0 page commands;
  - three console lines and no read: exactly 1 wake;
  - after a read, a new line: exactly 1 wake;
  - no console read reaches the page.
- `the_panel_reopens_with_history_marked_by_document`: attach, page 1 logs, detach, page 2 logs, attach. Both lines are there, and page 2's `doc` is greater than page 1's.
- `inspector_engine_tests::a_tab_keeps_a_small_ring_from_the_start`.

Red before, shown by mutating eb8bcc65 (detach clears the ring; the watch never registers; console reads go to the page as on develop): **0 passed, 3 failed**.
- the blocked read: "no console answer while the page was blocked";
- reopen: "the first page's line was forgotten";
- wake: "one wake for unread lines" (0 wakes).

Three existing tests pinned the old behaviour and now say what T6b does:
- `devtools_tests::console_records_only_once_attached_and_reads_since` is renamed `console_reads_since_and_closing_forgets_nothing`;
- `inspector_engine_tests::with_nobody_listening_nothing_is_recorded` and `a_sink_alone_turns_recording_on` now build with the ring off;
- `devtools_panel`'s poll test is replaced by `an_open_panel_asks_for_the_console_only_when_the_view_recorded`.

Runs at eb8bcc65:
- engine `content_thread devtools inspector page_protocol`: 144 passed, 0 failed;
- hiwave-app devtools 2/2; parity-capture event_log 2/2.

Full engine lib suite (`cargo test -p rustkit-engine --features headless --lib`):
- at T6a 8356804c: 1064 passed, 5 failed (load 11.5-28.3);
- at eb8bcc65: **1068 passed, 5 failed** (load 11.7-14.8, 1787 s).

The five are exactly the Mac localhost tests T5 fixes on `atlas/dt-mac-gates` (referrer x3, image_loader_routing, remote_web_fonts), which this branch does not include.

## Cost of the ring (Atlas Q1 gate)
- **Campaign:** 26 cases, parity-capture built at eb8bcc65 with `--profile parity`, ring on. Passed 26/26, mean 1.1078%, the same as develop and T6a. Worst three unchanged: article-typography 4.79%, about 3.70%, form-controls 3.24%.
- **20-site wall-clock A/B** (`ab5.py`, live top-20, 1280x800, 30 s limit). One binary; A = `HIWAVE_DEVTOOLS_RING=0`, B = ring on; each site captured A, B, A, B. Table in `receipts/T6b-ab-ring-eb8bcc65.txt`.
  - **Wall-clock:** sum of per-site means 205.0 s off, 203.4 s on (0.992). Per-site differences go both ways: the largest are shopify +2.6 s and microsoft -2.8 s. Load was 11-12, from this session's own Aleph indexer (below).
  - **Frames:** 0 failures in either arm. No site differs between arms beyond its own spread within an arm.
  - The one apparent mover was linkedin: 2.64% in all four cross pairs with 0.00% inside each arm. It is linkedin's own variation, not the ring. Two reruns and two controls (off vs off, on vs on) show the same 2.64% / 1.55% / 41% splits with no ring difference involved: linkedin serves at least three page variants, one of them an 18-script page.
  - Script-record counts match in every site except youtube, shopify and cnn, which also vary inside an arm.
  - **Verdict: the ring moves nothing measurable, so it stays on by default.** `HIWAVE_DEVTOOLS_RING=0` is the off switch.

## Receipt (`scripts/receipt.py`)
```json
{"base_sha": "8356804c", "binary_sha256": "64e0fb0bc770285171ec95491c0f27d57d2bc8c8ad0747f8ad311e9463b7cd89",
 "campaign": {"cases": 26, "failed": 0, "passed": 26, "mean_diff_pct": 1.1078,
              "file": "scratch/camp-t6b-eb8bcc65.json",
              "sha256": "6f53dbd16a149da124aa98060c22d5f88e0ea9c965989fe9c0c5ab2e8061ecdf"},
 "candidate_sha": "eb8bcc656d1d25a8f47ca23f2a3414abd4051de6",
 "cargo_lock_sha256": "d43bf3f40c046d3d625a2876c81a524fcaac59b37460f330942147537a4c8cb7",
 "dirty_state": false, "profile": null, "features": null,
 "os": "macOS-26.5.2-arm64-arm-64bit", "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)",
 "utc": "2026-10-25T11:24:01.708729Z", "work_package": "T6b-devtools-push"}
```
`profile` and `features` read null because the binary was copied out of `target/parity/` to `scratch/pc-t6b` before the A/B. It was built with `-p parity-capture --profile parity`. Full JSON: `receipts/T6b-receipt-eb8bcc65.json`.

Overlap: the same files as T6a (`page_protocol.rs`, `lib.rs` module list), plus `inspector.rs` (#792 T2 and T3 add recording calls but do not touch `push_locked` or `State`). Whichever lands second merges develop.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
