## T15b: make "proven" honest, and the scoring gaps from the #856 R1

**On develop `b4b58115`, pin `a6f29b0bedaf`: 349 cases, 63 pass, 176 fail, 70 unproven, 5 skip, 35 error. The negative control goes red.** Before this PR, same binary: 107 / 169 / 21 / 3 / 49. Scripts, one oracle script and the README; no engine change. Campaign 26/26, mean 1.1095%, unchanged.

The drop from 99 (the #856 number) has two parts. #853 and the other landings took it to 107 on this develop with the old runner. This PR takes 107 to 63.

| area | row | pass | fail | unproven | skip | error | old pass/fail/unproven/skip/error |
|---|---|---:|---:|---:|---:|---:|---|
| css-lists | C6 | 0 | 11 | 16 | 0 | 3 | 3/11/11/0/5 |
| css-masking-clip-path | C8 | 0 | 25 | 3 | 0 | 2 | 3/25/0/0/2 |
| css-masking-mask | C8 | 0 | 20 | 3 | 0 | 7 | 1/11/2/0/16 |
| css-overflow | C2 | 6 | 15 | 13 | 1 | 5 | 18/16/1/0/5 |
| css-position-absolute | C15 | 1 | 23 | 4 | 0 | 2 | 4/23/1/0/2 |
| css-position-sticky | C7 | 0 | 22 | 1 | 1 | 4 | 0/23/0/0/5 |
| css-text-basics | C6 | 9 | 22 | 6 | 0 | 3 | 14/22/1/0/3 |
| css-transforms-2d | C10 | 12 | 20 | 4 | 0 | 4 | 11/20/4/0/5 |
| css-transforms-3d | C10 | 10 | 11 | 5 | 0 | 4 | 14/11/0/0/5 |
| css-ui-outline | C5 | 0 | 6 | 14 | 0 | 1 | 14/6/0/0/1 |
| seed | seed | 25 | 1 | 1 | 3 | 0 | 25/1/1/3/0 |
| **all** | | **63** | **176** | **70** | **5** | **35** | 107/169/21/3/49 |

These are still samples of each area, not pass rates.

### Departure from the row: tab-stop-threshold-001 stays a FAIL
The row names this case as one that also differs in Chromium, from the R1's 129 px. **I could not reproduce that.** Chromium 143.0.7499.4 gives 0 px on every try: plain and deterministic launches, staged and unstaged pages, 800x600 and 1280x720, three rounds each. The rule in the row is implemented, and under that rule this case is a FAIL. R1: what was your setup? If a setup shows 129 px, the recheck should use it.

### Read UNPROVEN with this
**Of the 47 passes demoted by an area probe, 20 are shown hollow and 27 are not.** I ran the same probe in Chromium, as a one-off that is not part of the runner:
- **20 move Chromium's frame**, so the feature matters there and the engine ignores it: 12 outline (the same count as the R1), 3 lists, 2 clip-path, and 1 each in absolute, 3D and text.
- **27 do not move Chromium's frame**, so the probe does not touch what the page asserts, and those cases may be honest passes: 12 overflow, 4 3D, 4 text, 2 absolute, 2 outline, and 1 each in clip-path, mask and sticky.

The row's rule demotes both groups, so I kept it, and the README says UNPROVEN means "this run cannot tell". The runner cannot yet tell the two apart. **The overflow number in particular (18 to 6) understates that area:** all 12 are in the second group.

### What changed
1. **Area probe.** `AREA_PROBES` in `wpt_tier1.py` has one rule per area, appended last in the page on `*`, `*::before` and `*::after`. A pass that still matches is UNPROVEN and the reason names the probe. A test pins that every area in `wpt_import.AREAS` has a probe. The seed has none, only its own `mutations`. The README now says what PASS means.
   - **R1's check:** every css-ui-outline pass is now UNPROVEN, 14 of 14, and 0 PASS.
   - **R1's other four:** `clip-path-inline-004` and `clip-path-shape-004` are UNPROVEN. `transform3d-perspective-origin-001` is a PASS with the probe red: rotatex renders at this head. `preserve3d-pseudo-element` is an ERROR on both runners (finding 1).
2. **Zero-ink rule. 14 of the 49 ERRORs move:** 9 to FAIL (all mask), 4 to UNPROVEN and 1 to PASS (`transform-translate-004`). 35 remain: 24 zero-ink and 11 script errors. Zero ink means every pixel is white; a full frame of one other colour has ink.
3. **`.__probe-*` pages** are deleted after each capture, with their staged copies and cache entry. A run leaves 0, was 260.
4. **Chromium recheck.** New `tools/parity_oracle/wpt_pair_chromium.mjs`. The 5 FAILs under 0.1% were asked:
   - **Became SKIP:** `text-overflow-ellipsis-editable-div-with-caret` (125 px) and `position-sticky-table-pixel-rounding` (42 px).
   - **Stayed FAIL at 0 px in Chromium:** `empty-span-size-002`, `clip-path-inset-round-percent`, `tab-stop-threshold-001`.
   - A FAIL with no answer stays a FAIL with `chromium_not_measured`.
5. **Blind spots.** 6 UNPROVEN rows now say so in their reason: 4 with an SVG `transform` attribute, 2 that toggle a class from script.

### Engine findings for Atlas
1. **`preserve3d-pseudo-element` has zero ink in its test frame on this develop.** The R1 had it as a match at `cae49416`. It reads ERROR here under the old runner too, so it is not from this PR. Not bisected; #853 is the obvious first look.
2. **9 mask ERRORs were thin frames and are now scored FAILs**, 0.1% to 0.5%. The 7 remaining mask ERRORs are all zero ink.

### Evidence
- **Red first:** 8766046d commits the tests, 26 of 110 failing. Now 110/0, plus `test_no_unguarded_nullable_diff.py` 6/0.
- **Reproduction:** a fresh `new-task.sh` checkout of the pushed branch, `python3 scripts/wpt_coverage.py --no-build` after a z-cargo parity build: **0 of 349 rows moved** against the first checkout (status, reason, diff, Chromium pixels).
- **`wpt_sync.sh` ran whole on this seat for the first time,** through `wpt_coverage.py`: 620 files, `--check` OK. The README and the script's header now say so. "Fresh clone" is still a fresh checkout, as in T13 to T15.
- **Campaign** ran on the parity build through a no-op `cargo` on PATH, per the 10-29 recipe.

### Limits
- **The 27 above.** A per-case mutation or an automatic Chromium check of each probe would separate them; neither is in this PR.
- **Probe rules are mine,** apart from the three the row names. Only the outline, clip-path and transform areas have been read against an R1 result.
- **The SKIPs were not looked at by hand.** The numbers repeat across both checkouts. The caret page may be sensitive to caret blink timing.
- **`stage_html`'s root-absolute rewrite** still uses a regex, unchanged from T15.

## Receipt (`scripts/receipt.py`)
`branch` reads `HEAD` because the receipt ran in the detached fresh checkout; the branch is `atlas/dt-t15b-wpt-proof`.

```json
{
 "base_sha": "origin/develop",
 "binary": "target/parity/parity-capture",
 "binary_mtime_utc": "2026-11-01T23:47:57.619682Z",
 "binary_sha256": "76ba564f6343ba64dd24e510db8cef206841b87147b38abdc432f7efa9a9e028",
 "branch": "HEAD",
 "campaign": {
  "cases": 26,
  "failed": 0,
  "file": "parity-baseline/parity_test_results.json",
  "mean_diff_pct": 1.1095,
  "passed": 26,
  "sha256": "847852805d8b247ce1f71e268414ec8d3f7feffe645067424a0b019703653efd",
  "timestamp": "2026-11-01T18:49:26.507139"
 },
 "candidate_sha": "7aca4bb89a9e04940977537685ad35e40f759de0",
 "cargo": "cargo 1.91.0 (ea2d97820 2025-10-10)",
 "cargo_lock_sha256": "241df6e8a50e5a0d93f45d52e91b46ed3f39286897f689b06e8e39e7b7a1e97a",
 "chrome_version": null,
 "cpu": "arm",
 "dirty_state": false,
 "effective_engine_flags": {},
 "features": null,
 "host": null,
 "note": "T15b: no engine change; scripts, one oracle script and README only",
 "os": "macOS-26.5.2-arm64-arm-64bit",
 "profile": "parity",
 "raw_runs": [
  {
   "bytes": 176685,
   "file": "trench/wpt/last-run.json",
   "sha256": "9029ec30f266bb0f488fd942df22f192046a972867bae9e935071383c3e5c4c7"
  }
 ],
 "repo": "https://github.com/hiwavebrowser/hiwave-macos.git",
 "rustflags": null,
 "sccache": true,
 "target": "aarch64-apple-darwin",
 "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)",
 "utc": "2026-11-01T23:49:51.188463Z",
 "work_package": "T15b"
}
```

🤖 Generated with [Claude Code](https://claude.com/claude-code)
