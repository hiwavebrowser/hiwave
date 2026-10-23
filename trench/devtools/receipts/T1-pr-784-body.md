**Draft. Dev-tools lane, package T1 (JS exception stacks).** Unblocks #777.

## What it adds to the event log
- **Function names in stacks.** With `keep_error_text` (`parity-capture --event-log-error-text`), a `script_error` frame reads `    at name (url:line:col)`. Without it, frames stay positions only, as before: a function name is page text. Boa's placeholders (`<main>`, `<anonymous>`) are dropped, and names are capped at 128 characters.
- **`console.error` stacks.** Two new `console` fields, recorded only for `console.error` (and a failed `console.assert`) while error reports are on:
  - `stack`: where the call was made.
  - `error_stack`: the first Error argument's own frames, i.e. where it was thrown. They are read through the realm's own `Error.prototype.stack` getter, never a `stack` the page set.

  This is the case that blocked #777: Next.js catches the TypeError and hands it to `console.error`, so no `script_error` is ever raised.
- **`script_error.inserted_by`.** When the innermost frame's script is a `<script src>` that page script inserted, this field holds the location of the insertion call. It comes from a new `JsRuntime::register_host_function_with_caller`, which only `__rustkit_dom_inserted_script` uses.
- Every new field is appended and defaults to `null`. `docs/INSPECTOR_EVENT_LOG.md` is updated.

**Cost.**
- Off (nobody listening, the default): nothing. No new work runs unless error reports are on, and the inserter walk runs only when a page inserts a `<script src>`.
- On: one walk of the VM's frames per `console.error`, one `stack` getter call when an Error is among its arguments, and one frame walk per inserted `<script src>`.

**Known deviation.** A call frame is placed at its `(` (Boa's place, already documented for the existing stacks). Chrome places it at the callee's name. The innermost (throw) frame matches Chrome.

## Tests (red before)
New tests in `rustkit-engine` `inspector_engine_tests`:
- `a_deep_throw_shows_every_frame_and_where_its_script_was_inserted`: a script inserted by `inline#1` throws three frames deep. The stack reads `inner (/deep.js:8:8)`, `middle (/deep.js:5:8)`, `outer (/deep.js:2:9)`, `/deep.js:10:6`, and `inserted_by` is `inline#1:3:46`.
- `a_deep_throw_keeps_positions_only_without_error_text`: the same page without error text gives positions only.
- `console_error_carries_its_callers_stack`: `console.error` has the caller's stack; `console.log` has none.
- `a_caught_error_logged_with_console_error_keeps_where_it_was_thrown`: #777's shape, `try { one() } catch (e) { console.error('boundary', e) }`.

**Red before.** With the three switches turned off in place (names dropped, console stacks not walked, `note_inserted` a no-op), all 4 fail: `0 passed; 4 failed`. The tests read fields that do not exist on develop, so they cannot compile there.

**Green on the Mac** (`z-cargo`, debug):
- New tests: 4 passed.
- `rustkit-engine --features headless --lib -- inspector_engine_tests inspector_tests console_log`: 68 passed, 0 failed.
- `rustkit-js --lib`: 377 passed. `rustkit-bindings --lib`: 81 passed.
- The GPU-backed `inspector_page_tests` were not part of these runs. In one combined run they panicked waiting on the GPU test guard, behind a concurrent lane's build.

## Acceptance: yahoo, headless live
Command: `parity-capture --url https://www.yahoo.com/ --live-ms 25000 --event-log … --event-log-error-text`, built at this branch with #777 (`32f2c2f1`) merged locally (not part of this PR).

**#777's two TypeErrors** (`cannot convert 'null' or 'undefined' to object`, message length 46) now arrive as `console` errors with their throw sites. Paths are under `www.yahoo.com/_nca/_next/static/chunks/`; there are no query strings.

1. The `__next_s` loader's catch, `console.error` at `7730-….js:1:6322`. Thrown at:
   ```
   at 7730-cb9f75c635e817e4.js:1:6198
   at 7730-cb9f75c635e817e4.js:1:6074
   ```
2. The error-boundary path, `console.error` at `7730-….js:52:1849`. Thrown at:
   ```
   at webpack-4ad9b97e72f1a3ed.js:1:13395
   at webpack-4ad9b97e72f1a3ed.js:1:15693
   at webpack-4ad9b97e72f1a3ed.js:1:1251
   at webpack-4ad9b97e72f1a3ed.js:1:1236
   at c (7730-cb9f75c635e817e4.js:52:24764)
   at 7730-cb9f75c635e817e4.js:52:40816
   at 7730-cb9f75c635e817e4.js:52:41027
   at t (7730-cb9f75c635e817e4.js:52:42078)
   ```
   The TypeError is raised inside the webpack runtime (`__webpack_require__`'s helpers) while chunk 7730's `c` loads a module. The `console.error` call itself comes through React (`87c73c54-….js`, 30+ frames of `ua`/`uk`). #777's next step is to read `webpack-….js:1:13395`.

**Without #777** the same run on this branch alone shows one `SyntaxError` from chunk 7730 (`1:6278`, `1:6074`), the bug #777 fixes.

## Campaign (26 cases, binary built at 2ec901a4)
Passed 26/26, failed 0, mean diff 1.11%. Worst three: article-typography 4.79%, about 3.70%, form-controls 3.24%. This change touches no layout or paint code.

## Receipt (`scripts/receipt.py`)

```json
{
 "base_sha": null,
 "binary": "scratch_dt/pc-2ec901a4",
 "binary_mtime_utc": "2026-10-23T14:01:47.531776Z",
 "binary_sha256": "97c126331cb54d48ca910a5c1d03280810496c15e359f9afbe45e784c4534082",
 "branch": "atlas/dt-js-stacks",
 "campaign": {
  "cases": 26,
  "failed": 0,
  "file": "scratch/camp-t1-2ec901a4.json",
  "mean_diff_pct": 1.1078,
  "passed": 26,
  "sha256": "8fb4cd82b6d38405926153a694ed081c0dc18807482055eda96dc0e3bf7fb092",
  "timestamp": "2026-10-23T10:03:23.864510"
 },
 "candidate_sha": "7f5d8301c9db30109f52116dcd14a034cd93e3a9",
 "cargo": "cargo 1.91.0 (ea2d97820 2025-10-10)",
 "cargo_lock_sha256": "d43bf3f40c046d3d625a2876c81a524fcaac59b37460f330942147537a4c8cb7",
 "chrome_version": null,
 "cpu": "arm",
 "dirty_state": false,
 "effective_engine_flags": {},
 "features": null,
 "host": null,
 "note": "binary built at 2ec901a4; 7f5d8301 after it is docs-only",
 "os": "macOS-26.5.2-arm64-arm-64bit",
 "profile": null,
 "raw_runs": [],
 "repo": "https://github.com/hiwavebrowser/hiwave-macos.git",
 "rustflags": null,
 "sccache": true,
 "target": "aarch64-apple-darwin",
 "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)",
 "utc": "2026-10-23T14:07:12.495460Z",
 "work_package": "T1"
}
```

🤖 Generated with [Claude Code](https://claude.com/claude-code)
