## T17: parity-capture follows one script navigation

Branch `atlas/dt-t17-script-nav`, base develop b813ba0c. Red **c525fd85**, fix **010be089**. parity-capture only, no engine change.

### What changes
- A URL capture now takes the page's navigation ask (`location` set or `assign`, `link.click()`, `form.submit()`, `<meta http-equiv=refresh>`) after the load and after every live turn, using `Engine::take_script_navigation_with_replace`, which the app already uses. It loads the first ask into the view. Later asks are counted, not followed (`navigations_not_followed`).
- A new result field, `followed_navigation`, has four parts: `to` (origin and path only, no query, fragment or userinfo), `during` (`load` or `live`), `at_ms` (from the first load's start) and `replace`.
- The live clock restarts on the landed page, so its timers count from its own load, and the window runs to its original end.
- **A challenge page is judged where it lands.** With `--live-ms`, a non-2xx first page that may still navigate is no longer failed at once. The status check runs after the window, on the page the capture landed on. A 403 that never navigates still fails, with the same message as before. Without `--live-ms`, the check is unchanged except that a navigation asked during the load is followed first.
- `--report` reads only the landed page's records, from the last `navigation_start`. So `settled` is not forced to "changing", and the site is the landed page's site.
- `--no-follow-navigation` gives the old capture.
- `follows_script_navigation` is on for URL captures that follow (the app's setting), so the load does not wait for images that a leaving page's scripts added.

### Tests
- **Red at c525fd85** (the scaffold adds only the flag and the result fields), 4 of 4 failing:
  - `a_script_navigation_during_the_capture_is_followed_one_hop`: `location.assign('/two')` from a 500 ms timer. The frame stayed page one (red) and there was one `navigation_start`.
  - `a_meta_refresh_during_the_capture_is_followed_one_hop`
  - `a_second_script_navigation_is_counted_not_followed`
  - `no_follow_navigation_captures_the_first_page`: the count was 0, not 1.
- **Added with the fix, each red by mutation** (follow off, or the report slice off):
  - `a_navigation_asked_in_the_live_window_is_followed_there`
  - `a_challenge_page_is_judged_where_it_lands` (403 to page two is ok and green; a 403 that stays put fails with the old message)
  - `the_report_of_a_followed_capture_is_of_the_landed_page`
- `cargo test -p parity-capture --profile parity`: **79/0**.
- Clippy reports nothing on the new lines. The crate already fails rustfmt on develop, so I did not reformat it.

### Departure from the row
The row's red asks for a script that navigates "after 500 ms". The load runs page timers up to its 5 s virtual horizon (`timer_horizon_ms`), so a 500 ms timer's ask is seen as the load returns (`during: "load"`), not in the live window. A separate test covers the live-window path: a script inserted by a timer, whose fetch is answered 300 ms late, does the navigating.

### Campaign
26/26, mean **1.0896%**, run on the parity build (release path symlinked to `target/parity/parity-capture`, no-op cargo shim). The campaign uses `--html-file`, which never enters the new path, so the change cannot move it. I did not run a develop arm. The last lane figure was 1.0931% at develop 232fca86, and develop is b813ba0c now.

### Not done
- **No live witness.** This seat cannot run a built binary without approval, so the reddit D1 capture is not in this receipt. The next run with approval, or Atlas, should run `parity-capture --url https://www.reddit.com/ --live-ms 15000 --event-log …` and quote `followed_navigation` and the two `navigation_start` URLs, shape only.
- `live_stats` cover both pages' turns. `script_stats` are the landed page's.

### Receipt (`scripts/receipt.py`)

```json
{
 "base_sha": "b813ba0c",
 "binary": "target/parity/parity-capture",
 "binary_mtime_utc": "2026-11-06T05:58:01.570112Z",
 "binary_sha256": "3892225cdd5202d397db513a49ea0ff592198e14b04dda518174a64f7f62bb9a",
 "branch": "atlas/dt-t17-script-nav",
 "campaign": {
  "cases": 26,
  "failed": 0,
  "file": "parity-baseline/parity_test_results.json",
  "mean_diff_pct": 1.0896,
  "passed": 26,
  "sha256": "cdd743226688ef3efc88623f310bf1e6085e4767130f4308d97c778f69508bfb",
  "timestamp": "2026-11-06T00:58:47.305401"
 },
 "candidate_sha": "010be0891e0e45818c37d7b60ad0323fa761675e",
 "cargo": "cargo 1.91.0 (ea2d97820 2025-10-10)",
 "cargo_lock_sha256": "36360f8f04d56d938a5d58455c21b1feb791b309cc1dc7eddd356856f9a28e0d",
 "chrome_version": null,
 "cpu": "arm",
 "dirty_state": false,
 "effective_engine_flags": {},
 "features": null,
 "host": null,
 "note": "T17: URL-mode script navigation follow; file-mode captures (the campaign) take no new path",
 "os": "macOS-26.5.2-arm64-arm-64bit",
 "profile": "parity",
 "raw_runs": [],
 "repo": "https://github.com/hiwavebrowser/hiwave-macos.git",
 "rustflags": null,
 "sccache": true,
 "target": "aarch64-apple-darwin",
 "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)",
 "utc": "2026-11-06T05:58:59.097449Z",
 "work_package": "parity-capture"
}
```

🤖 Generated with [Claude Code](https://claude.com/claude-code)
