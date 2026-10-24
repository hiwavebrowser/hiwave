# T6 design: devtools service thread (dev-tools lane, 2026-10-24, for Prometheus R1)

Goal (plan row T6, Pete 10-23): detach devtools from what is displayed. The panel keeps its console/network/script history and stays usable when the page is hung, crashed, mid-navigation or replaced. Only live DOM/computed-style snapshots need the page. Acceptance: with the Inspector open on an idle page, page-thread wakes per second **from devtools** = 0 (counter in the receipt); console/network reads served while the page thread is blocked in a long script; #785's rate limit removed.

## Today (develop ff6ad36a, after #785)
- Records already live outside the page's data: one `Arc<Inspector>` per view, `Mutex<State>` with a 4096-record ring (`inspector.rs:47, 390-446`). Redaction (shape-only, URL scrub) happens **at record time** (`inspector.rs:779-910`, `inspector_glue.rs:31-61`), so any thread can serve a snapshot without re-redacting.
- But every panel read goes through the page thread: `Devtools` → `PageCmd::Devtools{query, reply}` → `PageEndpoint::apply` → `Engine::devtools_*` (`webview_rustkit.rs:1068`, `page_protocol.rs:146-163, 523-540`). `Console{since}` is only `inspector.snapshot_since` (`devtools.rs:480-483`) yet costs a page command. #785 limits it with `CONSOLE_POLL` = 250 ms (`devtools_panel.rs:38`): about 4 page commands per second while the panel is open on an idle page.
- The page loop also wakes on its own about 20/s (sleep capped at 50 ms, `page_protocol.rs:926`). The metric is therefore devtools-caused wakes, not all wakes. No counter exists yet.
- Console lines from page script queue in rustkit-js and reach the Inspector only at a flush (end of an evaluation or job run, `rustkit-js/src/lib.rs:1051-1075`). A script that never returns has its lines stuck.
- Network records are written on the page thread, by `RequestGuard` in futures on the page runtime (`inspector.rs:938-1036`). An inserted script's response is recorded only when a live turn runs it (`script_net.rs:1316`).
- Records survive navigation (only the clock resets, `inspector.rs:558-571`) but carry no document id. They are wiped by `Attach(false)` on panel close (`inspector.rs:466-471`), and nothing is buffered before the panel opens.

## Shape
1. **Counter first.** `DevtoolsCounters` (atomics) counts page commands from devtools handled in `PageEndpoint::apply` plus window pokes from `devtools_wakes_window`. Exposed through a test hook and a `HIWAVE_DEVTOOLS_COUNTERS=1` once-per-second log line. Red test: an idle page with the panel attached, run for 2 s; develop reads about 8 devtools page commands, the target is 0.
2. **One `devtools` thread per process (the service).** It gets each view's `Arc<Inspector>` when the view is made (one extra reply field on view creation) and owns the read side:
   - console/error/script/lifecycle/network snapshots, served from the ring;
   - the per-document marks;
   - the shape-only check, kept as a second guard (`devtools.rs:201-211` moves here).
   It answers the window over a channel plus the event-loop proxy. The window thread never takes the Inspector lock: sinks run under it (`inspector.rs:374-379`), and a file sink would block the UI.
3. **Push, not poll.** `push_locked` bumps an `AtomicU64` watermark and signals a `Condvar`, after the lock is released. The devtools thread waits on it and posts to the window only when it has new records for an open panel. `CONSOLE_POLL` and `ConsolePoll` go. Cost when no panel is open: one atomic store per record, and the condvar is signalled only when a waiter exists.
4. **Live snapshots stay page commands**: `NodeAt`, `DomTree`, `Element`, `Highlight`, `Eval`, sent only on a user action. Each gets a deadline. Past it, the panel shows `page busy (in script N s)` from the last `script` record, keeps the previous tree greyed, and does not queue repeats (one outstanding query per kind).
5. **History across documents.** `InspectorRecord` gains `doc: u32` (the navigation number, bumped in `navigation_started`). The panel groups by document and keeps old documents until the ring evicts them. `Attach(false)` stops pushing to the panel but no longer clears.
6. **`diagnose` from the service.** `parity-capture --report` keeps its in-process path. The service can serve the same `event_causes` (T4) for an open tab later, but that is not in T6's acceptance.

## Packages
- **T6a**: counter + red test; the panel's console reads move to the service thread (shape 2 for console only). Acceptance: devtools page commands per second on an idle page = 0; the console still updates (existing panel tests).
- **T6b**: push watermark, `CONSOLE_POLL` removed, `doc` on records, no clear on detach. Test: a console read is answered with the page thread blocked in a host-side wait (a test-only `PageCmd::Block(ms)`).
- **T6c**: busy state and deadlines for live snapshots; one outstanding query per kind.
- **T6d** (needs Q2/Q3): console lines reach the Inspector during a long script; network records from the fetch side.

## Questions for Atlas / Prometheus
1. **Buffer before the panel opens.** A ring per tab from creation would give history the moment the panel opens (Pete's "keeps its history"). Cost: up to 4096 records per tab of memory, and every record built even with no panel. Today the lane rule is "nothing measurable when off". Proposal: on by default with a 512-record ring, measured in the T6b receipt (campaign + a 20-site A/B wall-clock); off if it moves anything.
2. **Console during a never-returning script.** Make `console.*` push straight to the Inspector per call when it is active, instead of at flush: one lock per console call, with the stack captured at the call. Or accept that a hung script's lines appear only if it returns, and say so in the panel.
3. **Network records while the page thread is blocked.** Reads are served (shape 2), but *new* request/response records cannot appear: the futures that write them run on the page runtime. Moving recording to the HTTP layer's threads is a rustkit-net change. Proposal: out of T6; the acceptance reads "served", not "updated".
