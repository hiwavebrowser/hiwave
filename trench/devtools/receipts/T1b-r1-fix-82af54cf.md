## R1 condition: mirror on, errors as shapes — new head 82af54cf

Prometheus's condition: with `HIWAVE_CONSOLE_LOG=1`, `attach` sets the runtime's error `keep_text=true`. Show that exception records and `console.error` stack records reach the Inspector as shapes only, or fix it here.

**The test found a real leak, and this head fixes it.**

- **New test** `inspector_engine_tests::with_the_mirror_on_errors_and_error_stacks_reach_the_inspector_as_shapes`. Setup: mirror on, `keep_error_text` off. Two named page functions run `console.error(new Error(...))` and then `throw new TypeError(...)`. The test asserts that no `console` or `script_error` record carries the page's message or a function name.
- **Before (58800963): red.**
  - `script_error.message` was the page's thrown text. `script_error` copied `report.message` as the runtime gave it, and with the mirror on the runtime keeps the text.
  - The `console.error` record was already shapes only.
  - Both stacks were already positions only (no function names).
- **Fix** (`inspector_glue::script_error`): the message is kept only when the Inspector itself keeps error text (`keeps_error_text()`). The mirror's own log line still gets the text from the runtime's report.
- **After: green.**
  - `inspector` tests: 90/90.
  - Full engine suite (`-p rustkit-engine --features headless --lib`, macOS): 1040 passed / 5 failed. The five are the Mac localhost set (referrer ×3, image_loader_routing, remote_web_fonts), the same as develop. They are fixed by the T5 branch, not by this PR.
- **Campaign:** not re-run. The change touches only what the Inspector records for `script_error`, with no paint or layout path. The earlier head read 26/26 at 1.11%.
