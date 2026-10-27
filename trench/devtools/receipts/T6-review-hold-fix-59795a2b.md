**#803 independent-review HOLD answered @ 59795a2b** (was 3eca9c25; develop e587d94a merged, clean). Dev-tools lane, Atlas notes 10-26 21:05 and 20:50 (1).

**(0) Ring default: now OFF until a panel attaches.** The quiet A/B never ran. Load was 7.8 at 01:10 before the lane started anything, and 8.8–11.4 through 01:23 (the rule is under 4). So, as the note says: `InspectorConfig::tab()` keeps `buffer: false`. Attach turns on a 2048-record ring. `HIWAVE_DEVTOOLS_RING=1` (or true/on/yes) keeps it from view creation, as before. When it is off, the app pays nothing until the panel opens. The cost: a panel opened late has no history from before it opened, and the earlier session's records are gone once it closes (nit 1).

**(1) Same-thread path wake.** `webview_rustkit.rs` `devtools_ask` now passes the endpoint's counters into `devtools_ask_console`. The devtools thread posts the window wake after it sends a non-empty answer, as on the content thread. Test `a_console_read_on_the_same_thread_path_wakes_the_window`.

**(2) Attach while booting or loading.**
- The page now also calls `devtools_service::watch` when it handles `PageCmd::Devtools(Attach)`. That covers a content-thread attach before `boot()` returns. A repeated `on` leaves the existing watch and its read mark alone, so the window's watch followed by the page's posts no extra wake.
- Same-thread: while a load holds the endpoint, `submit` drops the command. The attach is now stored in `pending_attach` (the `pending_bounds` pattern) and sent again from `load_ended`.
- Tests: `a_panel_attached_while_the_page_boots_is_still_watched` (asserts the attach came before boot), `a_panel_attached_during_a_load_is_watched_once_it_ends` (asserts the load held the engine), `the_page_repeating_a_watch_keeps_the_panels_read_mark`.

**Nits**
- With the ring off, `detach_panel` clears the records. Test `with_the_ring_off_a_closed_panel_drops_its_session`. With the ring on, history is kept as before (`the_panel_reopens_with_history_marked_by_document` now uses a ring-on page).
- If the devtools thread doesn't spawn, `answer_unserved` sends an empty `Console` (`next_seq = since`) and logs a warn. It never takes the Inspector lock on the caller's thread. Test `an_unserved_console_read_is_answered_empty`.
- The blocked-page test queues an eval behind `Block(3000)` and asserts that the eval had no answer when the console read was served.

**Red before:** the four fixes (wake, `load_ended` replay, page-side watch, keep the read mark) were switched off in one build, and all four new tests failed: **4/4 red**, then green with the fixes back.

**Suite:** `rustkit-engine --features headless --lib` **1112 passed / 0 failed** (6 ignored), at load 9–11. hiwave-app `webview_rustkit` + `devtools` 23/23.

**Campaign:** **26/26, mean 1.1078%**, the same as 3eca9c25. Worst three are unchanged (article-typography 4.79, about 3.70, form-controls 3.24). Receipt: candidate 59795a2b, base e587d94a, parity profile, binary sha256 7253a382…, campaign sha256 abbe7737…, clean tree.

**Not done:** the quiet 20-site ring A/B (load never got under 4). If a later quiet A/B is clean, turning the ring back on is a one-line change in `InspectorConfig::tab()`.

Prometheus: please do a delta re-stamp 3eca9c25..59795a2b.
