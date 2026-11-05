CH2.E9 (PLAN-z.md): the IPC push path, and the macOS wiring that tells the chrome what the RustKit content view committed.

## What was wrong

1. **Address bar, tab title, spinner, history on macOS.** The RustKit content view received the page's `Url`, `Title` and `LoadState` events and stored them, and nothing read them. The handlers that send `UpdateUrl` / `UpdateTitle` / `SetLoading` / `RecordVisit` exist only on the WebKit content view, which is built only off macOS (`main.rs` `#[cfg(not(target_os = "macos"))]`). So after a redirect the address bar and the saved tab kept the typed URL; the tab never got the page's title; `setLoading(false)` never reached the chrome; no history visit was recorded; back/forward state was never sent.
2. **`window.ipc.postMessage` from a RustKit view went nowhere.** Messages were pushed to a JS array (`window.__ipcQueue`) that only `Engine::drain_ipc_messages` could read, by running a script, and nothing called it. On the content thread the window cannot reach the engine anyway.

## Change

- `RustKitView::harvest` fills a `ChromeUpdates` (committed URL for http/https/file only, title, load started, load state, URL of a completed load). `take_chrome_updates()` hands it over once. The macOS loop, after `take_script_navigation`, sends `UpdateUrl` + `UpdateActiveTabUrl` + `NavigationStateChanged`, `UpdateTitle`, `SetLoading(true/false)` + `SyncShieldStats`, and `RecordVisit`. App documents (New Tab/about/report commit as `about:`/`data:`) keep the address the app gave them.
- `SetLoading(false)` injected four WebKit helper scripts into the content view. It is now off macOS only: on macOS those scripts never ran (no `SetLoading` was ever sent there), and they post to the WebKit IPC.
- `window.ipc.postMessage(m)` calls a host function `__rk_ipc_post` that pushes to a Rust-side queue in `DomBindings` (a non-string is sent as its JSON). `drain_ipc_queue` / `has_pending_ipc` run no script now. `Engine::drain_view_ipc(view)`. `PageEndpoint::after_page_change` → `report_ipc()` sends each message as the new `PageEvent::Ipc { payload, nav_id }` (content thread only, like focus and script navigation). `RustKitView::take_ipc_messages()` returns them in order.
- **Not wired to `ipc::commands::handle_message` for the content view, on purpose:** any web page can call `window.ipc.postMessage`, and the command set includes navigation, tabs, shelf, vault. Dispatch belongs to the app's own views (the RustKit chrome, CH3.A2; shelf, CH3.A4). The row's red ("a page posting `{cmd:'navigate'}` reaches `handle_message`") is met up to `take_ipc_messages`; A2 connects it for the chrome view only. Decision for Atlas/Pete: should `window.ipc` exist at all on web content views? Today every page sees `window.ipc` and `window.hiwaveChrome` (fingerprintable); removing them from content views is a one-line follow-up once A2 marks views as app-owned.
- `get_version` variant and the shelf's double `with_ipc_handler` from the row are WebKit-side and not touched here; they go with A2/A4.

## Red first

| commit | test | result |
|---|---|---|
| `05e26190` (red) | `webview_rustkit::tests::content_thread_the_chrome_is_told_the_committed_url_title_and_load_end` | FAILED: `url: None` vs `Some(".../final")` |
| `6a85a9d8` (fix) | same + `content_thread_an_app_document_reports_no_url` | ok |
| `085afb13` (red) | `content_thread::tests::the_window_is_sent_what_the_page_posts_on_window_ipc` | FAILED: `[]` vs the navigate payload |
| `7f07a992` (fix) | same + `webview_rustkit::tests::content_thread_the_window_takes_what_the_page_posts_on_window_ipc` | ok |

## Real window (grant-free: request log + saved state, no input, no pixels)

New check `tools/real_window/driver.py --checks e9_redirect`: the app restored on `/e9_start` (302 → `/e9_final.html`, title "E9 final"); asserts on `workspace_state.json`, which the address bar and tab strip are synced from.

| binary | sha256 | result |
|---|---|---|
| develop `df02d853`, `--release` | `1c5a8a27…1d7060` | PASS 3 FAIL 2: tab url stays `/e9_start`, no title |
| branch `6a85a9d8`+driver `560d5f18`, `--release` | `2ecf6fb9…5f446` | PASS 5 FAIL 0: tab url `/e9_final.html`, title saved |

Seat grants: accessibility/post_events/screen_capture false, so the address bar pixels themselves are not seen; Pete's hand test or a granted seat confirms the bar.

## Narrow runs at `7f07a992`

- `rustkit-engine --lib --features headless content_thread`: 46 passed, 0 failed, 2 ignored.
- `rustkit-bindings`: 438 + 1 passed, 0 failed.
- `hiwave-app`: 69/70 in a full run at load avg 16–19; `a_new_load_replaces_the_one_in_progress` (wall-clock `< 5 s`, same-thread path, which this PR does not touch apart from one host function at bindings creation) failed once in the full run and passed alone twice at 3.0 s. One earlier full run had it and `content_thread_a_url_bar_navigation_lands_within_100_ms…` failing, both passed alone. Not measured on develop at the same load.
- Merges cleanly with develop `82893eac` (`git merge-tree`).

Full gates, campaign and A/B are the batch's (this touches scripts: every page loses `window.__ipcQueue` / `window.__drainIpcQueue`, and `postMessage` is a host call).

Receipt fields: base `df02d853`, candidate `7f07a992`, toolchain rustc 1.92.0, profiles test (debug) and `--release` (app), host Petes-MacBook-Pro (macOS seat, Z lane), Chrome not used (no pixel claim), fixtures in-tree (`tools/real_window/pages/e9_final.html`, the 302 route in `driver.py`).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
