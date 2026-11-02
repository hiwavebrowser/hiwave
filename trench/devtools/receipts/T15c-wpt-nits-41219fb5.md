## T15c: the #857 R1 nits

**On develop `337b5833`, pin `a6f29b0bedaf`: 349 cases, 63 pass, 176 fail, 70 unproven, 5 skip, 35 error, the same as T15b. No status or pixel count moved on any row.** The negative control goes red. Scripts, one oracle script and the README; no engine change. Campaign 26/26, mean 1.1095%, unchanged.

No crate changed between T15b's develop `b4b58115` and `337b5833`, so the comparison with T15b's rows is same-source.

### What changed
1. **README** (`trench/wpt/README.md`): "No Chrome is involved" is gone. It now says Chromium decides whether a small FAIL is a SKIP. `oracle` in `last-run.json` gains `small_fail_rule`, and the docstring says the same.
2. **Viewport:** `chromium_pair_diffs` takes the run's viewport instead of hard-coding 800x600. The manifest's viewport is 800x600 today, so no row moves.
3. **Fonts:** `wpt_pair_chromium.mjs` waits for `document.fonts.ready` before the screenshot. The 5 small-FAIL answers did not move (0, 125, 42, 0, 0 px).
4. **Area-probe cases:** every match demoted by its area probe is now asked of Chromium, and `chromium_diff_pixels` carries the answer. Where Chromium's own test and reference differ, the reason ends "this page is not evidence either way". The case stays UNPROVEN. See below.
5. **`.__staged` copies:** a run removes them when it ends, including after an exception, and removes any an interrupted run left. It left 0, was 602; `.__probe-*` is still 0. The rechecks run before the removal, because they read staged pages.

### Area-probe result: 13 of 47 differ, not 11
**47 asked, 13 differ in Chromium, 34 match, 0 not measured.**

| area | cases | Chromium's own px |
|---|---|---|
| css-ui-outline (8) | `outline-009`, `outline-color-002`, `-003`, `-004`, `outline-offset-inset-001`, `-002`, `-003`, `-004` | 4160, 608, 2120, 952, 14720, 4492, 10946, 16000 |
| css-text-basics (4) | `break-spaces-before-first-ideographic-char-016`, `break-spaces-with-ideographic-space-004`, `full-width-leading-spaces-003`, `white-space-vs-joiners-002` | 376, 82, 302, 1056 |
| css-transforms-3d (1) | `backface-visibility-hidden-003` | 15000 |

The row says 11 of 47. I did not find the R1's list, so the two extra cases are not identified. Its named `outline-offset-inset-001..004` are all in the 13.

**This is a different split from T15b's 20/27.** That one-off asked whether the probe moves Chromium's frame. This one asks whether Chromium matches its own reference. The runner still does not tell "hollow" from "probe missed"; that is still Atlas's open decision from the T15b digest.

### Evidence
- **Red first:** be0141ea commits the tests, 23 failing. Now 125/0 on a synced checkout, plus the nullable-diff guard 6/0.
- **The fonts test was red only from the new signature at that commit,** so I checked it by mutation too: with the wait removed from the `.mjs` it reads 20000 px, with it back 0 px. It runs real Chromium through Playwright.
- **Reproduction:** a fresh `new-task.sh` checkout of the pushed branch, z-cargo parity build, `python3 scripts/wpt_coverage.py --no-build`: same headline counts, 0 of 349 rows moved against the first checkout (status, reason, diff pixels), same 47/13/34, 0 staged and 0 probe files left. "Fresh clone" is still a fresh checkout, as in T13 to T15b.
- **Campaign** ran on the parity build through a no-op `cargo` on PATH, per the 10-29 recipe.

### Limits
- **The viewport fix has no effect at today's manifest,** and is pinned by unit tests only.
- **The fonts wait moved nothing on these pages.** The test proves the wait, not that any WPT page needed it.
- **The recheck timeout went from 300 s to 600 s,** because it now also asks about 47 pairs. It is not per page: one hang leaves every case in that batch `chromium_not_measured`.

## Receipt (`scripts/receipt.py`)
```json
{
 "base_sha": "origin/develop",
 "binary": "target/parity/parity-capture",
 "binary_mtime_utc": "2026-11-02T05:40:18.136862Z",
 "binary_sha256": "671a5c41a1374e38cda2bb8e98995a8c86ea7b5ed165439a4521fd17520b59f9",
 "branch": "atlas/dt-t15c-wpt-nits",
 "campaign": {
  "cases": 26,
  "failed": 0,
  "file": "parity-baseline/parity_test_results.json",
  "mean_diff_pct": 1.1095,
  "passed": 26,
  "sha256": "845a89bdd26770a1c57b9b1304c90ff7abd685b430962b9c95d5cfdc1548b1fe",
  "timestamp": "2026-11-02T00:42:28.597908"
 },
 "candidate_sha": "41219fb5a34bf4df3e964a04cbdf2a9ead19f31d",
 "cargo": "cargo 1.91.0 (ea2d97820 2025-10-10)",
 "cargo_lock_sha256": "241df6e8a50e5a0d93f45d52e91b46ed3f39286897f689b06e8e39e7b7a1e97a",
 "chrome_version": null,
 "cpu": "arm",
 "dirty_state": false,
 "effective_engine_flags": {},
 "features": null,
 "host": null,
 "note": "T15c: no engine change; scripts, one oracle script and README only",
 "os": "macOS-26.5.2-arm64-arm-64bit",
 "profile": "parity",
 "raw_runs": [
  {
   "bytes": 180109,
   "file": "trench/wpt/last-run.json",
   "sha256": "c9bcc22618c5168132d9bfca818e68fedfba8168d52cb390a99770128df05460"
  }
 ],
 "repo": "https://github.com/hiwavebrowser/hiwave-macos.git",
 "rustflags": null,
 "sccache": true,
 "target": "aarch64-apple-darwin",
 "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)",
 "utc": "2026-11-02T05:45:43.071411Z",
 "work_package": "T15c"
}
```

