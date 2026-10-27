**Atlas 13:35 HOLD answered @ 5ea74e5e** (plain push on `atlas/dt-t6d`, no force-push). The held count now reaches the panel while the page is blocked.

**Must-fix: `console_held()` now has readers outside tests**
- **Devtools thread.** On each pass it already checks every watched view (on a signal, or the 1 s backstop). It now also posts a window wake when a view's held count differs from the count it last told the window about (`Watch.held_seen`).
  - This wake asks for no read and does not set `woken`, because a console read only follows new records. So a hung page whose count stops moving wakes nothing more.
  - The console answer also carries `held` (`DevtoolsConsole.held`, one atomic read, no page command).
- **Panel.** `pump` reads `inspector.console_held()` with one atomic load, as it already does for `watermark` and `page_crashed`. It shows **"K console lines held by a running script"** while the count is above 0 (`devtools_held_text`, `setConsoleHeld` in inspector.html), and hides the line at 0. The line also clears with the console.
- **Tests**
  - `devtools_service::a_held_console_count_wakes_the_panel_without_a_record`, deterministic, with no page:
    - A held count that moves with no new record wakes the window.
    - The console answer carries it.
    - An unchanged count posts no more wakes over 1.5 s.
    - Clearing the count wakes the window again.
  - `webview_rustkit::a_hung_scripts_held_console_lines_reach_the_panel_while_it_runs` is the panel-level test.
    - A headless view with the panel attached runs 300 calls, a 300 ms spin, 50 more calls, then a 2 s hang.
    - A reader thread sees a window wake after it first saw held lines, while the script still runs.
    - The panel's line text ends with "console lines held by a running script".
    - The second burst makes sure the wake it waits for comes after it looked.
    - `Devtools::pump` itself needs a wry `WebView`, so the test checks the two things pump reads and acts on, not the WebView call.
  - **Red before 2/2:** with the held-count wake turned off, both fail.

**Nits**
- **Held-count tests and the end-of-script flush.** Both tests now read the count, then delivered/records, then the count again, and keep the pair only if the two counts agree. The flush zeroes the count before it delivers anything, so a flush landing between the reads is skipped instead of failing the test.
- **The rate-cap cause flag.** It is now set by the latest hold: `wanted_live`, true or false. A drop with no live reader therefore names no cap.

**Results**
- hiwave-app `--bin hiwave`: 57 passed, 0 failed, three runs in a row (the first version of the view test failed once in a parallel run; it is now the two-burst version).
- rustkit-js `--lib`: 88 passed, 0 failed.
- Full engine suite `--features headless --lib`: 1118 passed, 0 failed, 6 ignored.
- Campaign: 26/26, mean 1.1078%. Every case is the same as at b36807e6.

The #809 leftovers (the in-time Unavailable hover, and the forget test) are **not** on #809, per Atlas 13:40. The hover fix and its test are parked on `atlas/dt-t6c-followups` @ cacf5917 for the follow-up PR after #809 lands. The forget test can't go through `page_changed`/`close()`, because both need a wry `WebView`. It calls the two helpers they call (`forget_page`/`forget_questions`).
