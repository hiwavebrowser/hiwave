# T37: i0a key shortcuts judged on the app's own answer, not the hwdrive subprocess

Branch `atlas/dt-t37-key-ack` @ 4c1a5d30 (red 23481b94, fix 71b8a6ca, pin 4c1a5d30), base develop f3103247. Tooling only: `tools/real_window/{driver.py, hwdrive.swift, README.md, tests/test_key_ack.py}`. No Rust change. **No PR yet: PR cap (31 open, cap 8). This file is the PR body.**

## Problem

`expect_controls` timed Cmd+T and Cmd+W from before the `hwdrive key` subprocess was spawned until the driver's 100 ms log poll saw the app's line. That time includes the process spawn, hwdrive's two 30 ms post sleeps and up to 100 ms of polling, and none of that is the app's work. So i0a_close flipped from FAIL 308/266 ms to PASS 157/160 ms between two runs with no code change (T36 #1008 disclosure). This is the same class of bug T36 fixed for resize.

## Change

- **`hwdrive key`** now also prints `req_epoch` and `post_ms`. `req_epoch` is the wall-clock time just before the key-down is posted, in Unix seconds, on the clock the app log's UTC stamps use. `post_ms` is the time spent posting both events. The events and the sleeps are unchanged.
- **`driver.py`** adds `key_request_epoch(out)` and `log_answer_ms(log, pattern, t0)`. The second returns the first app line that matches the pattern and whose own UTC stamp is at or after `t0`, in ms after `t0`.
  - `key()` in `expect_controls` asserts that this figure is under 200 ms.
  - A line stamped before the key-down never counts, so an earlier tab's line cannot pass the check.
  - A key line with no `req_epoch` (an hwdrive from before T37) fails closed: "no req_epoch from hwdrive: the key cannot be timed".
  - The detail line reports the subprocess wall time and `post_ms` beside the answer, for information.
- README: the controls paragraph says how keys are timed.
- Departure from the row: the row suggests an ack from the tab strip or an AX change. The RustKit chrome exposes no AX tree (T39 / A8), so the ack used here is the app's own log line, timed by its own stamp. This is the same clock T36 uses for the page view's `relayout cause=resize`.

## Tests

- `tests/test_key_ack.py`, 8 tests. At 23481b94 (tests only), **5 of 7 were red**: the parser tests, the judged-on-stamp test, the slow-answer test and the fail-closed test. The two that passed were the no-answer and stamped-before guards, which develop passes vacuously.
- At 4c1a5d30: **47/47** for `python3 -m pytest tools/real_window/tests/` (test_key_ack 8, plus the existing resize_ack, budget_stop, record, profile_isolation and sidebar_switch tests).
- Mutation: with the `when >= t0` stamp filter dropped, 2 tests go red: `..._stamped_after_the_request` and `a_line_stamped_before_the_request_is_not_the_answer`.
- Pin: a real app log line in its coloured form (tracing's ANSI codes, as in the 10-14 run logs) is timed correctly after `App.log_text()` strips the codes, and it is not matched raw.
- Campaign: **26/26, mean 0.405 %**. It ran on the seed `target/release/parity-capture`, built from base develop f3103247, with a no-op cargo shim on PATH. No Rust changed, so this binary is the candidate's engine.

## Receipt (`scripts/receipt.py`)

```
candidate_sha 4c1a5d30d16a47ec0b8b98af6d64ba991b772692  base_sha f3103247  branch atlas/dt-t37-key-ack
profile release (seed build of the base; no Rust change)  dirty_state false  toolchain rustc 1.91.0 (f8297e351 2025-10-28)
binary target/release/parity-capture sha256 16b49a41ae382883…
campaign: cases 26 passed 26 failed 0 mean_diff_pct 0.4051 (sha256 6329cae08819bced…)
note: tooling only (tools/real_window); no Rust change
```

## Owed, not run on this seat

- **`swiftc` was not run.** The lane seat refuses `swiftc`, so the hwdrive change is not compiled here. It is 7 lines that reuse the `Date()` / `DispatchTime` pattern already used by `resize`. `driver.py` builds hwdrive itself at the start of every real-window run, so the first run compiles it.
- **The real-window witness.** On a seat with the grants, run `driver.py --app <hiwave> --checks i0a_close` twice. The Cmd+T and Cmd+W lines should read "app answered N ms after the key; subprocess wall M ms" with N well under M, and N should be stable across the two runs. The lane seat has no Accessibility or post-event grant.
