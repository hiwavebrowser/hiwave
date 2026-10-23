## fix: #730 follow-ups

Follow-ups (a)-(f) to #730 (M4 PR2, content thread), from #730's delta R1 NITs and Prometheus's R1 CLEAR notes on `c98cec06`. Branch `atlas/z-m4-followups`, cut from `c98cec06`; develop is merged in once #730 is on develop. One commit per item, each with a test that is red without it.

| item | commit | what | test (red before) |
|---|---|---|---|
| (a) | `cfedb581` | The window hears focus that a script moved (`focus()`, `blur()`, a timer, autofocus): the endpoint reports any focus change after each page change, script run and input (content thread only). The window clears `page_focused` when it starts a navigation or loads HTML. | `content_thread::tests::the_window_hears_focus_a_script_moved_and_a_new_document_has_none` (no report); `webview_rustkit::tests::content_thread_a_new_document_starts_with_no_focused_field` |
| (b) | `a748f3d2` | `ViewControl::end_uncommitted(nav_id)`: the not-committed/not-cancelled check and `clear_all` under `nav_lock`, as `cancel_nav` does. Before, a newer navigation's cancel + stop landing between the check and the clear was undone. | `control::tests::a_cancel_racing_the_end_of_an_uncommitted_navigation_keeps_its_stop` (red with the same method written lock-free) |
| (c) | `e5cd3f03` | A failed navigation sends the committed document's URL as its last `Url`, so the address bar shows the page on screen again. | `content_thread::tests::a_failed_navigation_puts_the_shown_documents_url_back` |
| (d) | `1f0c6f09` | The process-wide inserted-script fetch queue is 512, not 64 (a burst of 100: load=64 error=36 before). The in-flight cap stays 8. Per-view bounds come with M6. | `inserted_script_live_tests::a_burst_of_a_hundred_inserted_scripts_all_load` |
| (e) | `a1dc4ac4` | A 204/205 navigation is aborted as HTML says: the page stays (it used to be replaced by an empty document) and the load ends with Complete, not Failed. A navigation is reported Failed at most once (an empty error response sent two). | `content_thread::tests::a_204_navigation_leaves_the_page_as_it_is_and_reports_no_failure`; `content_thread::tests::a_failed_navigation_is_reported_failed_once` |
| (f) | `29fbb606` | A stopped inserted-script `load`/`error` listener marks its own element's record (by index in the pump that ran it), not the last record with the same URL. The owed-event queue is a `VecDeque`. | `script_net_tests::a_stopped_listener_marks_its_own_scripts_record_not_another_with_the_same_url` (red with the by-URL match) |

Not changed (watch item): the inserted-fetch in-flight cap stays 8. It moves to 24 only if Trace's A/B shows yahoo's feed below the fold not filling.

Behaviour change with the flag OFF too: (e)'s 204/205 abort is in the engine's load path, so a 204 no longer blanks the page on either path. Downloads: the engine has no navigation-download path (`DownloadStarted` is never sent), so a download is the same Ok-without-commit case once it exists.

## Gates
@@GATES@@

🤖 Generated with [Claude Code](https://claude.com/claude-code)
