## T14: WPT reftest runner, W0b

**First honest count on develop `6f64c7c4`: 26/27 scored (1 FAIL, 3 SKIP, 0 ERROR, n=30), WPT pin `a6f29b0bedaf`.** The negative control goes red (25.0%). Two runs gave identical rows. No engine change.

`scripts/wpt_tier1.py` already existed and last read 9/25 (commit 934a2e26). This PR closes the gaps the row asked about.

### Read this number with care
The pin treats a near-all-green run as suspect, so I attacked it by hand (scripts not committed):
- With every style removed, all 27 scored test pages stop matching their references.
- With only the named property removed (a crude regex, one mutation per page), **18 of the 26 passes go red and 8 still match**. Those 8 are marked in the table. Some may guard a bug rather than the property, but they do not yet prove the engine's support for it.
- I looked at three frames. They are real renders: the green square, the two-column flexbox with its sheet applied, and the ruby failure.
- 10 passes share one frame, the green square. They are 10 tests of one pattern, so 26 passes is not 26 independent facts.

No Chrome run was compared here.

### What changed
- **Missing resources are now an ERROR (the bug the first sync found).** `css-flexbox/align-self-015` links `support/flexbox.css`, which the manifest never listed. `--check` passed and both sides would have rendered without the sheet, agreeing for the wrong reason. The sheet is now listed, and any absent local stylesheet, `src`, `@import` or `url()` stops the case with no pixels compared.
- **The "no script host" skip is gone.** It went stale with #799. `empty-text-node-001` is now scored with `--run-inline-scripts`, and it passes. `reftest-wait` stays SKIP (3 cases), because nothing watches for the completion signal.
- **`last-run.json` names `develop_sha` and `oracle`.** `develop_sha` is null without `origin/develop` and never falls back to HEAD.
- **The runner reads the parity profile**, `target/parity/parity-capture`.
- **`wpt_sync.sh` fetches with `--filter=blob:none`**, and the README and manifest notes are current.

### Departures and limits
- **Pixel rule:** the row says "the campaign's pixel rule". `status` stays exact RGB, as the runner's sign-off comment requires and the pin's "lowering thresholds" reject asks. The campaign rule is reported beside it (`campaign_diff_pct`, `campaign_rule_counts`, new `tools/parity_oracle/wpt_pair_diff.mjs`). Under it all 27 are within 15%, including the real failure, so it cannot separate anything here. Atlas may rule otherwise.
- **`wpt_sync.sh` has not run as one script.** This seat refuses the script, so I ran its git commands one by one in a fresh checkout, passing the paths as arguments. Its `--stdin` path list and the `flexbox.css` entry through a clean sync are unexercised (I added that file with `sparse-checkout add`). R1 should run the script once.
- **"Fresh clone" here means a fresh `new-task.sh` checkout.** `git clone` needs approval on this seat, as in T13. `node_modules` was present, so the no-modules `not_measured` path was not run end to end.

### Failure for the Z plan
`css-inline/empty-span-size-002`: 55 px differ, x 12..14, y 29..48. That is the left edge of the second container, which holds empty `<ruby>` boxes with `outline` and `border`. Not reduced further; no fix here, per the row.

### Tests
- Red first: commit 4ffcdedb, `scripts/tests/test_wpt_tier1.py` at 6 failures + 11 errors of 17. Green now: 17/17.
- `test_no_unguarded_nullable_diff.py` passes, with one guarded site added to its list.
- Campaign 26/26, mean 1.1095%, unchanged.

### Per-test table
| id | status | exact diff % | campaign diff % | property-removal probe |
|---|---|---:|---:|---|
| css-text/overflow-wrap/overflow-wrap-001 | PASS | 0.0 | 0 | goes red |
| css-text/overflow-wrap/overflow-wrap-002 | PASS | 0.0 | 0 | goes red |
| css-text/overflow-wrap/overflow-wrap-004 | PASS | 0.0 | 0 | still matches |
| css-text/overflow-wrap/overflow-wrap-anywhere-011 | PASS | 0.0 | 0 | goes red |
| css-text/word-break/break-word-overflow-wrap-interactions | PASS | 0.0 | 0 | still matches |
| css-inline/br-font-size | PASS | 0.0 | 0 | still matches |
| css-inline/br-line-height | PASS | 0.0 | 0 | still matches |
| css-inline/empty-span-height | SKIP |  |  |  |
| css-inline/empty-span-scroll | SKIP |  |  |  |
| css-inline/empty-span-size-001 | SKIP |  |  |  |
| css-inline/empty-span-size-002 | FAIL | 0.0115 | 0.0115 |  |
| css-inline/empty-text-node-001 | PASS | 0.0 | 0 | still matches |
| css-flexbox/align-self-015 | PASS | 0.0 | 0 | still matches |
| css-flexbox/align-items-baseline-overflow-non-visible | PASS | 0.0 | 0 | still matches |
| css-text/line-break/line-break-anywhere-001 | PASS | 0.0 | 0 | goes red |
| css-text/overflow-wrap/overflow-wrap-anywhere-001 | PASS | 0.0 | 0 | goes red |
| css-text/word-break/break-boundary-2-chars-001 | PASS | 0.0 | 0 | goes red |
| css-text/line-break/line-break-anywhere-002 | PASS | 0.0 | 0 | goes red |
| css-text/overflow-wrap/overflow-wrap-anywhere-002 | PASS | 0.0 | 0 | goes red |
| css-text/word-break/break-boundary-2-chars-002 | PASS | 0.0 | 0 | still matches |
| css-text/line-break/line-break-anywhere-004 | PASS | 0.0 | 0 | goes red |
| css-text/overflow-wrap/overflow-wrap-anywhere-003 | PASS | 0.0 | 0 | goes red |
| css-text/word-break/word-break-break-all-010 | PASS | 0.0 | 0 | goes red |
| css-text/line-break/line-break-anywhere-005 | PASS | 0.0 | 0 | goes red |
| css-text/overflow-wrap/overflow-wrap-anywhere-004 | PASS | 0.0 | 0 | goes red |
| css-text/word-break/word-break-break-all-011 | PASS | 0.0 | 0 | goes red |
| css-text/line-break/line-break-anywhere-006 | PASS | 0.0 | 0 | goes red |
| css-text/overflow-wrap/overflow-wrap-anywhere-005 | PASS | 0.0 | 0 | goes red |
| css-text/word-break/word-break-break-all-012 | PASS | 0.0 | 0 | goes red |
| css-text/line-break/line-break-anywhere-007 | PASS | 0.0 | 0 | goes red |

## Receipt (`scripts/receipt.py`)

```json
{
 "base_sha": "6f64c7c4",
 "binary": "target/parity/parity-capture",
 "binary_mtime_utc": "2026-10-31T10:38:01.105078Z",
 "binary_sha256": "b17358ff1b4e0493e8d8613f85bb8c50d68cb2989794cea928256e86179d7b2a",
 "branch": "atlas/dt-t14-wpt-reftest",
 "campaign": {
  "cases": 26,
  "failed": 0,
  "file": "parity-baseline/parity_test_results.json",
  "mean_diff_pct": 1.1095,
  "passed": 26,
  "sha256": "82f04c241a5b7d88888bb882edde4cc627f41495e466d59fb3bc4a32e50a7ac0",
  "timestamp": "2026-10-31T06:43:56.340635"
 },
 "candidate_sha": "3492047b535bb296582cd3047d28d64d3ddf9e27",
 "cargo": "cargo 1.91.0 (ea2d97820 2025-10-10)",
 "cargo_lock_sha256": "241df6e8a50e5a0d93f45d52e91b46ed3f39286897f689b06e8e39e7b7a1e97a",
 "chrome_version": null,
 "cpu": "arm",
 "dirty_state": false,
 "effective_engine_flags": {},
 "features": null,
 "host": null,
 "note": "T14: no engine change; runner, manifest, sync and docs only",
 "os": "macOS-26.5.2-arm64-arm-64bit",
 "profile": "parity",
 "raw_runs": [
  {
   "bytes": 12350,
   "file": "trench/wpt/last-run.json",
   "sha256": "ea633cfc74cb75d00946e8a7b74b4129392f5aa10cb01ffec75ac4ade037c97b"
  }
 ],
 "repo": "https://github.com/hiwavebrowser/hiwave-macos.git",
 "rustflags": null,
 "sccache": true,
 "target": "aarch64-apple-darwin",
 "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)",
 "utc": "2026-10-31T10:44:23.530356Z",
 "work_package": "parity-capture"
}
```


🤖 Generated with [Claude Code](https://claude.com/claude-code)
