<!-- gh pr create -R hiwavebrowser/hiwave-macos --draft --base develop --head atlas/z-ch3-a2-chrome-sink --title "CH3.A2 (part): HIWAVE_RUSTKIT_CHROME=1 boots the chrome in RustKit; ChromeUi + handle_chrome_ipc" --body-file trench/z/receipts/ch3-a2-pr-body.md -->
CH3.A2 (PLAN-z.md), first part. **Stacked on #901 (CH2.E9)**, merged in; land #901 first. Plan: `trench/z/ch3-a2-design.md` on the hub.

## Change
1. `refactor:` the WebKit chrome's ~420-line IPC closure is now `fn handle_chrome_ipc(body, proxy, state)`; the closure calls it. Pure move (the whitespace-stripped line multiset differs only by the signature and the call).
2. `refactor:` `trait ChromeUi { eval, place }`. The 35 `wry::WebView::evaluate_script/set_bounds` calls on the chrome, the seven `sync_*_to_chrome` helpers and `apply_layout` go through it. `WebView` implements it with the same calls.
3. `feat:` `HIWAVE_RUSTKIT_CHROME=1` (macOS, content thread on): `enum ChromeView { WebKit, RustKit(RustKitView) }`. The RustKit arm is a `RustKitView` at the chrome's bounds loading `chrome.html` with `JS_BRIDGE` as the head's first script (the WebKit view runs it as an initialization script). Each `MainEventsCleared`: `process_events`, every `take_ipc_messages()` body logged as `RustKit chrome IPC` and fed to `handle_chrome_ipc`, `render`. Rust→JS through `ChromeUi::eval` (`wry_evaluate_script` → content thread eval). Input on the chrome's NSView is **dropped** (it used to be impossible: there was no second RustKit view); routing it to the chrome is step 3b. Flag off: unchanged.
4. `WindowSurface::viewhost_id()`, `RustKitView::input_view()`: the id the NSView's input is tagged with.

Not RustKitChromeView (`webview_rustkit_chrome.rs`): it predates the content thread, has its own engine on the window thread, JS off, every setter a TODO. Left as dead code for A5 to delete.

## Real window (grant-free: app log + saved state; no input, no pixels)
New check `driver.py --checks a2_chrome_boots` (flag on): the app logs that the chrome is a RustKit view, and `RustKit chrome IPC body={"cmd":"get_sidebar_width"}` / `get_workspaces`, which chrome.html posts at boot.

| binary | result |
|---|---|
| develop `df02d853` `--release` | PASS 3 FAIL 3 (no RustKit chrome, no RustKit IPC) |
| branch `b752b147` `--release`, sha256 `eecd94c5…3aac5451` | a2_chrome_boots PASS 6/6; e9_redirect (flag off) PASS 5/5 |
| branch `4d602445` `--release` (after #901's timing fix), sha256 `776dddc6…85bf2c68` | a2_chrome_boots PASS 6/6; e9_redirect PASS 5/5 |

The log shows the round trip: the chrome posts `get_sidebar_width`, the app answers through `ChromeUi::eval`, and the chrome then posts `set_sidebar_width {"width":220}` (its stored width), then `get_workspaces`, `get_shelf`; "Syncing tabs/workspaces to Chrome UI" follow. **Not seen:** whether the RustKit chrome paints right (this seat has no Screen Recording), and clicks/keys (dropped by design until 3b). The A1 board measures the paint.

## Narrow runs at `4d602445`
- `hiwave-app`: 70 + 27 + 1 + 8 passed, 0 failed (7.8 s).
- `cargo check -p hiwave-app`: no new warnings (the dead `RustKitChromeView` ones are develop's).

## Next (3b, 3c)
- 3b: route `drain_input` events with `view == chrome.input_view()` to the chrome view (pointer, wheel, keys, focus) through the same dispatch as the content view's arm, which needs that ~150-line arm lifted into a function first (pure move, like step 1).
- 3c: gate "typing a URL navigates" needs input grants → Pete or a granted seat; the grant-free half can assert the `Navigate` IPC from a scripted `hiwave.navigate()` on the chrome via devtools eval.
- Risks to measure with the flag: two content threads (RSS), the chrome's timers on its own thread (idle CPU, `HIWAVE_STALL_LOG=1`).

Receipt fields: base develop `82893eac` (+ #901 `7903e602`), candidate `4d602445`, rustc 1.92.0, profiles test (debug) and `--release`, host Petes-MacBook-Pro (Z lane seat), no Chrome (no pixel claim), fixtures in-tree (`tools/real_window/pages/e9_final.html`).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
