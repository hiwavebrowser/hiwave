# T44: the bare `while (true)` load test counts the script's stop, not a lifecycle step's

Branch `atlas/dt-t44-spin-log-once` @ 041d8910 (red 2900cef3), base develop 157e60e1. Test-only change, one file: `crates/hiwave-app/src/webview_rustkit.rs`. No app or engine change.

## Cause (from the code, plus a red fixture; not seen on the failing runs)

`content_thread_a_bare_while_true_in_a_load_script_is_stopped_and_the_log_says_why` failed twice under heavy load. #1015 failed at load about 20 and #1034 at 29, each with "no line says why the script ended". Neither run kept its log. The assertion is `why.len() == 1` over every `Script stopped at the script budget` line, so the failure means 0 lines or 2 or more.

- **Not 0 / not "late"** (the row's guess):
  - `log_script_stopped` runs on the page thread inside the load (`rustkit-engine` lib.rs ~9257), before the load's `LoadState::Complete` is sent.
  - `wry_load_url` sets `loading = true` synchronously.
  - Stale LoadState events are dropped by nav id (`stale()`, webview_rustkit.rs 1432).
  - So when the test sees the load end, the line is already in the log.
- **2 lines:**
  - Once `inline#1` spends the 15 s budget, each later lifecycle step (`event:DOMContentLoaded`, `event:load`, the load's `timers`) runs as a watchdog turn with `STOP_GRACE` = 50 ms (`with_script_js`).
  - The interrupt word fires on wall time, and `take_deadline_hit` reads it as a stop even if the step's own work finished.
  - A page thread held past 50 ms in that step (descheduled under machine load) therefore logs `Script stopped at the script budget source=event:load`. That is a second line.
  - The two other load spin tests (`…_never_ends_is_stopped_at_the_15_s_budget_and_logged`, `…pure_js_spin…`) count the same way (`budget_stops(&log).len() == 1`), so they share the flake.

## Red first (2900cef3)

A page with a `load` listener that runs 200 ms, before the bare loop (`PURE_SPIN_THEN_HELD_LOAD_PAGE`). It deterministically produces the line a held thread produces:

```
test …content_thread_a_bare_while_true_is_logged_once_when_a_lifecycle_step_is_stopped_too ... FAILED
assertion `left == right` failed: no line says why the script ended:
… WARN rustkit_engine: Script stopped at the script budget source=inline#2 elapsed_ms=15111 late_ms=0
… WARN rustkit_engine: Script stopped at the script budget source=event:load elapsed_ms=66 late_ms=0
```

The existing test's body moved unchanged into `assert_bare_spin_stopped_and_said(page, source)` for that commit.

## Fix (041d8910)

- `script_stops(log)` = `budget_stops` minus `event:*` and `timers`. The three load spin tests count it.
- The bare-loop check waits, bounded at 10 s, for its line instead of reading the log once. This is the row's ask. By the code above it should never wait, and it costs nothing when the line is there.
- On failure it prints the view's full log, so a recurrence shows which case it was.
- The held-load test also asserts its `event:load` line exists, so it cannot pass vacuously.

## Runs

| run | result |
|---|---|
| red commit, `content_thread_a_bare_while_true` filter | 2 passed, 1 failed (above) |
| fix, `content_thread_` filter | 22/0 |
| fix, `cargo test -p hiwave-app` (all binaries) × 2 under 24 `yes` hogs (load 5→35, 35→32) | 227+27+1+8, 0 failed, both runs |
| base, unit binary × 4 under 36 hogs (load 42–44) | 226/0 each: CPU hogs alone never reproduced the original flake |
| base, 3 spin tests at `taskpolicy -b` + 36 hogs | all 3 "the load never ended" at 40 s: too starved, a different failure |

Limit: the original failure was not reproduced from load alone. The cause is read from the code, and the fixture shows the same line through the same code path. If it recurs, the new message prints the log.

## Campaign and receipt

Campaign on parity-capture built at the candidate (`z-cargo build --profile parity`, 2m22s), no-op cargo shim, seed binary moved aside: **26/26, mean 0.4052 %** (unchanged; worst article-typography 3.49 %, form-controls 2.67 %, backgrounds 1.01 %).

```
base_sha 157e60e1  candidate_sha 041d89105ca8c25324dde99dd3a6b1fa2cb126ee  branch atlas/dt-t44-spin-log-once
binary target/parity/parity-capture sha256 a35cb899bfc029b569f5a7eb1d02ff40237a35de17e05d48c0d346c454b1e648
profile parity  dirty_state false  toolchain rustc 1.91.0 (f8297e351 2025-10-28)  os macOS-26.5.2-arm64
campaign: cases 26 passed 26 failed 0 mean_diff_pct 0.4052 (sha256 8a572cd89cf8039c…)
```

🤖 Generated with [Claude Code](https://claude.com/claude-code)
