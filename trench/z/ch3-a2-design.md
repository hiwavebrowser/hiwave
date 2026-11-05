# CH3.A2 — wire the RustKit chrome view: plan (Z lane, 2026-11-05 00:50 ET)

Written after CH2.E9 (#901), which A2 stacks on. Read-only survey of develop df02d853; no code yet.

## What exists
- `webview_rustkit_chrome.rs` (`RustKitChromeView`): its own `Engine` on the window thread, JS off, loads `chrome_rustkit.html` (not `chrome.html`), every setter a TODO, no input, no caller. **Recommend: don't build on it.** It predates the content thread (#743), input routing, devtools and the E9 IPC path.
- `RustKitView` (`webview_rustkit.rs`) already has all of it: content thread, pointer/keys/focus, `load_html_internal`, `execute_script_sync`/`thread.eval`, and now `take_ipc_messages()` (E9). The chrome is a second `RustKitView` with `blocked_counter: None`.
- The WebKit chrome: `main.rs:839` `WebViewBuilder::new().with_html(CHROME_HTML).with_initialization_script(JS_BRIDGE).with_ipc_handler(..)`. The handler is a ~300-line closure over `chrome_proxy`/`chrome_state` that turns `IpcMessage`s into `UserEvent`s and `handle_message` calls.
- Rust→JS: 27 `wry::WebView::evaluate_script(&chrome_for_events, ..)` sites plus the seven `sync_*_to_chrome(state, chrome: &WebView)` helpers.
- `JS_BRIDGE` builds `window.hiwave.*` on `window.ipc.postMessage(JSON.stringify(..))`: works unchanged on the RustKit `window.ipc` (strings pass through as-is since #901).

## Steps (each a small, test-passing commit)
1. **`ChromeSink`** trait in main.rs (`fn eval(&self, js: &str)`), impl for `wry::WebView` and `RustKitView` (`thread.eval`, fire-and-forget). Change the `sync_*` helpers and the 27 sites to `&dyn ChromeSink` / `chrome_for_events.eval(..)`. Pure refactor, no behaviour change; red is not applicable, app tests + real-window smoke must stay identical.
2. **Lift the IPC closure** at `main.rs:845` into `fn handle_chrome_ipc(body: &str, proxy, state)`; the wry handler calls it. Pure refactor.
3. **Flag** `HIWAVE_RUSTKIT_CHROME=1` (macOS): build a `RustKitView` at `chrome_bounds`, run `JS_BRIDGE`, then `load_html_internal(CHROME_HTML)` (JS_BRIDGE must run per document: inject it as a document-start script or prepend it to the HTML; check which `load_html_internal` supports). The WebKit chrome is not created. Each `MainEventsCleared`: `for body in chrome.take_ipc_messages() { handle_chrome_ipc(&body, ..) }`, `chrome.process_events()`, `chrome.render()`. Window input in the chrome strip goes to this view (today viewhost routes clicks to the content view only: check `rustkit_viewhost` hit routing for a second view).
4. **Red/gate:** a real-window check `a2_chrome_boots` (grant-free): app with the flag, restored on a fixture page; assert the log shows the chrome document committed and a `Chrome IPC:` line for the chrome's startup `get_tabs`/`get_workspaces` (the chrome asks on load), and that `workspace_state.json` is unchanged. Typing a URL needs input grants → Pete/granted seat.
5. A3 (composition: chrome above content, pass-through) is separate; A2 keeps the current side-by-side layout.

## Risks to name in the PR
- Two content threads (chrome + page) double the engine's memory and threads; measure RSS with the flag.
- The chrome's `setInterval`s run on its own content thread; check idle CPU with the flag (`window_stall` log).
- `handle_message` is only fed from views that load the app's own HTML; never from the content view (#901 note).
