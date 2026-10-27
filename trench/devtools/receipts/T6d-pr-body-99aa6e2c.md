T6d of the devtools service plan (`T6-design.md`, Atlas Q2 on 10-24, Prometheus T6 R1 condition 4). Network records from the fetch side are T7 and are not part of this PR.

**What changes.** Console calls were held in `rustkit-js` until the script ended, and only then flushed to the handler. A panel on the devtools thread therefore saw nothing of a long or hung script's console: exactly the case it is for. Now:
- `JsRuntime::set_console_live(Some(predicate))`, with a `DomBindings` passthrough. **The decision is made per console call** (condition 4). When the predicate says a reader is there, the call goes to the console and shape handlers at once, from inside the native `console.*`. Calls held from before go first, so each call is handed over **once and in order**. When it says no, the call is held for the flush as before. The flush path with nobody listening is unchanged.
- The engine (`inspector_glue::attach`) sets the predicate to `inspector.is_active()`. With the panel open, each call becomes a `console` record when it is made, and the devtools thread is woken by the watermark (T6b). The page is never asked.
- **Hot-loop cap.** At most 200 live hand-overs per second. Past that, calls are held (1024 at most, oldest dropped, as before). A `warn` line, `K console calls dropped (more than 1024 held)`, now comes ahead of the next calls handed over. Before this, dropped calls vanished without a count; that applies to the flush path too.
- **Stacks are still shape-only.** Live calls go through the same handlers as the flush: with the mirror on and console text off, the Inspector gets the shape line and nameless stacks (`nameless()`), unchanged. The dropped line is engine text.
- The Inspector's sinks now run inside the console call. The only non-test sink is parity-capture's `CollectingSink`, which only pushes onto a Vec.

**Tests (red before).**
- `a_live_console_call_reaches_the_handler_while_the_script_runs` (rustkit-js): a 300 ms spin between two calls. Before, both arrived together at the flush; red with `set_console_live` a no-op.
- `a_console_line_is_read_while_the_script_that_logged_it_still_runs` (engine): a reader thread sees the `console` record at least 400 ms before a 600 ms script ends. Red with the `attach` line removed.
- `a_reader_arriving_mid_script_gets_each_call_once_in_order`: the dedupe test for a panel attached mid-evaluation. Off for two calls, then on: a, b, c, d, once each, and the predicate asked once per call.
- `a_hot_loop_is_capped_and_says_how_many_were_dropped`: 3000 calls; delivered plus dropped equals 3000, and the newest call is kept.
- `with_live_off_the_calls_still_wait_for_the_flush`.
- The existing `console_lines_waiting_for_a_flush_are_bounded` now expects the dropped line (3976) ahead of the 1024 kept.

**Cost.** Off (nobody listening): one `Rc` clone and a borrow per console call, and nothing else. On: the record is made at the call rather than at the flush, the same work moved earlier, plus one `Instant::now()` per call for the cap.

**Results.** rustkit-engine `--features headless --lib` passed 1116 with 0 failures and 6 ignored. rustkit-js `--lib` passed 86 with 0 failures. rustkit-bindings `--lib` passed 382 with 0 failures. The campaign is 26/26 with mean 1.1078%, the same as develop.

## Receipt (`scripts/receipt.py`)

```json
{
 "base_sha": "origin/develop",
 "binary": "target/parity/parity-capture",
 "binary_mtime_utc": "2026-10-27T11:40:29.635526Z",
 "binary_sha256": "92592b9808d8476918e555a83da8697d028a8d5b7a2a295c24e6fd0f0c6d0c67",
 "branch": "atlas/dt-t6d",
 "campaign": {
  "cases": 26,
  "failed": 0,
  "file": "scratch/camp-t6d-99aa6e2c.json",
  "mean_diff_pct": 1.1078,
  "passed": 26,
  "sha256": "137614b6900d27802052bac79309131a5d0493b74868500452095d16e28aaea3",
  "timestamp": "2026-10-27T07:40:45.081776"
 },
 "candidate_sha": "99aa6e2cee2db3c6ec65cec1c5eb4080b9c592db",
 "cargo": "cargo 1.91.0 (ea2d97820 2025-10-10)",
 "cargo_lock_sha256": "45b66585b4e1b9edd2288f242beb611d830a021f02fb81a571f534cfbe131294",
 "chrome_version": null,
 "cpu": "arm",
 "dirty_state": false,
 "effective_engine_flags": {},
 "features": null,
 "host": null,
 "note": "engine suite 1116/0, rustkit-js 86/0, bindings 382/0",
 "os": "macOS-26.5.2-arm64-arm-64bit",
 "profile": "parity",
 "raw_runs": [],
 "repo": "https://github.com/hiwavebrowser/hiwave-macos.git",
 "rustflags": null,
 "sccache": true,
 "target": "aarch64-apple-darwin",
 "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)",
 "utc": "2026-10-27T11:41:55.183908Z",
 "work_package": "T6d"
}
```

🤖 Generated with [Claude Code](https://claude.com/claude-code)
