T21: parity-capture `--html-file` runs timer, frame and ResizeObserver callbacks with `--live-ms`

Branch `atlas/dt-t21-file-timers`, base develop c959570f. Red b1ffabe0, fix 946bf0cf. This file is the draft PR body; open it with `gh pr create --draft --base develop` when open PRs < 8.

## What was wrong
`Engine::load_html_as` runs the file's inline scripts, then DOMContentLoaded and `load`, and stops. It has no timer horizon (the URL load runs `run_timers(horizon)` after `load`). parity-capture never turned the live loop for a file either: `run_live` was only in the `--url` branch, and `--live-ms` on a file was silently ignored. So a `setTimeout(fn, 0)`, a `requestAnimationFrame` and a ResizeObserver's first delivery never ran for a file page (board 11-04; Atlas's 11-05 07:10 second witness: Chart.js resize on report.html).

## Change (parity-capture only, no engine change)
- With `--html-file` and `--live-ms N`, the capture turns the same `run_live` loop a URL capture turns (the app's pacing, `Engine::pump_live`) for N ms after the load, and reports `live_stats`.
- `--live-ms` turns on script for a file, as `--run-inline-scripts` does. A live loop with script off has nothing to run.
- No `--live-ms` means no change: the board's fixture capture (script off) and `--run-inline-scripts` captures are what they were. Two tests pin this.

## Tests
- Red first @ b1ffabe0: `a_file_capture_with_live_ms_runs_timers_frames_and_resize_observers` FAILED ("setTimeout(0) callback did not run": the three boxes stayed 10 px). The two guard tests passed at the red commit and still pass.
- Fix @ 946bf0cf: one file page, three boxes. Each gets its height (137/149/163 px) only from its own callback: `setTimeout(…,0)`, `requestAnimationFrame`, `ResizeObserver`. All three are in the `--dump-layout` geometry; `live_stats.timer_callbacks >= 2`.
- `a_file_capture_without_live_ms_is_the_boards_static_capture`: no script ran, no `live_stats`.
- `a_file_capture_with_inline_scripts_only_is_unchanged`: `--run-inline-scripts` alone still runs no timer.
- `cargo test -p parity-capture --profile parity` (z-cargo): **75 passed, 0 failed**.

## Campaign
26/26, mean 1.1095%, the same as the T12/T20 receipts. Run on the z-cargo parity build: `target/release/parity-capture` was symlinked to it and a no-op cargo shim was first on PATH. The checkout's stale seed release binary (05:08) was moved aside first, not used.

## Witness, and its limit
`crates/hiwave-app/src/ui/report.html` captured alone, with `--run-inline-scripts`, with and without `--live-ms 1500`: 14 boxes both ways, `timer_callbacks` 0. With no report data injected the page sets no timer, and Chart.js canvases need #905 (canvas 2D, not on develop). So this witness shows nothing either way. The board's report case is the real check once #905 lands: run it with `--live-ms`.

## Cost
Off (no `--live-ms`): none, the same code path. On: N ms of wall clock plus the turns, as for `--url`.

## Receipt (`scripts/receipt.py`)
```json
{
 "base_sha": "c959570f",
 "binary_sha256": "7c7a9b39b0ff97e7c261c22b16a643836b5bc305dd8cc3005060494fe261b8cc",
 "branch": "atlas/dt-t21-file-timers",
 "campaign": {"cases": 26, "failed": 0, "mean_diff_pct": 1.1095, "passed": 26,
  "sha256": "e56166d9c3771b7d5cc8b28382b292ab670065d782057054fac5165b94ce5b6a"},
 "candidate_sha": "946bf0cf921d0f380858c5723ffeb480862f1bbf",
 "cargo": "cargo 1.91.0 (ea2d97820 2025-10-10)",
 "dirty_state": false,
 "profile": "parity",
 "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)",
 "work_package": "T21-file-live-loop"
}
```

🤖 Generated with [Claude Code](https://claude.com/claude-code)
