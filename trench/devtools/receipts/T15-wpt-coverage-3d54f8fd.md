## T15: WPT coverage for the C-row queue

**On develop `cae49416`, pin `a6f29b0bedaf`: 349 cases, 99 pass, 178 fail, 21 unproven, 3 skip, 48 error. The negative control goes red (25.0%).** Scripts, manifest and README only; no engine change. Campaign 26/26, mean 1.1095%, unchanged.

| area | row | pass | fail | unproven | skip | error |
|---|---|---:|---:|---:|---:|---:|
| css-lists | C6 | 3 | 11 | 11 | 0 | 5 |
| css-masking-clip-path | C8 | 3 | 25 | 0 | 0 | 2 |
| css-masking-mask | C8 | 1 | 11 | 2 | 0 | 16 |
| css-overflow | C2 | 18 | 16 | 1 | 0 | 5 |
| css-position-absolute | C15 | 4 | 23 | 1 | 0 | 2 |
| css-position-sticky | C7 | 0 | 23 | 0 | 0 | 5 |
| css-text-basics | C6 | 14 | 22 | 1 | 0 | 3 |
| css-transforms-2d | C10 | 10 | 21 | 4 | 0 | 5 |
| css-transforms-3d | C10 | 7 | 19 | 0 | 0 | 4 |
| css-ui-outline | C5 | 14 | 6 | 0 | 0 | 1 |
| seed | seed | 25 | 1 | 1 | 3 | 0 |
| **all** | | 99 | 178 | 21 | 3 | 48 |

**The seed count drops from 26/27 to 25/27.** One of the 8 stays unproven and is out of the pass count, as the row asks.

**These are samples, not pass rates.** An area takes reftests the runner can score, evenly spread down to a cap of 30 or 40 (css-ui-outline has 21, sticky 28). `scripts/wpt_import.py` makes the choice, and the same tree gives the same entries.

**`maps_to` is by area, not by reduction.** No FAIL has been reduced, and a FAIL says test and reference differ, not which is wrong. Some sit in a row only because of their directory. Among the 178 by source text: 18 use `rtl`, 7 `writing-mode`, 7 multicol. For example, `position-absolute-in-inline-008a` is under C15 and is about the inline containing block.

### Engine findings for Atlas (no row owns the first two)
1. **Named access on Window is missing.** `<div id="target">` then `target.textContent = "y"` throws `ReferenceError: target is not defined`, and `window.target.textContent` throws `TypeError`. Both were reproduced on a reduced page. That is 9 of the 11 script ERRORs (`target`, `scroller`, `container`, `fixed`). The other two: `css-transform-animate-translate-implied-y` calls something not callable, and `clip-path-transform-mutated-001` has no `setup`. These pages are unscored until this exists, and real sites use the same pattern.
2. **Overflow inline-block baseline.** With `display: inline-block; overflow: hidden` added to the inner box of `align-items-baseline-overflow-non-visible`, Chromium 143 moves the `span` from y 8 to y 37. Our frame does not change. So the mutation is valid, and this is why the case stays UNPROVEN.
3. **Masks mostly do not paint.** 16 of 30 mask cases are ERROR. Most have a test frame with 0 or under 480 inked pixels while the reference has more (`mask-composite-2a` 0 vs 20000). C8 has the list.

### What changed
- **Item 1, the T14b nits.** The runner reads tags with a parser, so `src=` inside another attribute's quotes and `>` inside quotes are handled. The same read fixes `rel=match`, and page text is no longer scanned for `url(`, while `style=` now is. An empty `CARGO_TARGET_DIR` means the default.
- **Item 2, the 8.** Each has `mutations` in the manifest, and every run re-checks them. 7 go red and are proven. `align-items-baseline-overflow-non-visible` still matches and is UNPROVEN. `br-font-size` and `br-line-height` assert that a style on `br` has no effect, so their mutation puts the same style on a `span`: this shows the page is sensitive to it, which is weaker than the others.
- **Past the row: a style-removed probe on every match.** The row only asked for the 8, but imported passes had no proof at all. A match that still matches with all its author style removed is UNPROVEN, with the reason. This demoted 20 imported cases, 11 of them in css-lists, and none in the seed. Some are honest tests of UA defaults or markup (`li-value-reversed-*`), so UNPROVEN there means "not shown by this probe".
- **Item 3, the import.** Ten areas, 319 cases, 620 files at the pin. `scripts/wpt_coverage.py` is the one command.
- **External scripts are now SKIP, and the importer leaves them out.** `--html-file` runs inline scripts only. My first run scored these pages, and the frames lacked what the script does.
- **Capture failures now give the tool's own error**, not a timestamped log line, so the rows repeat.
- **Cases run 4 at a time.** A reference shared between cases is staged once per run.

### Evidence
- **Red first:** 2e3a0d19 commits the tests, 29 of 79 failing. The three nits were seen red there. Now 83/0 at the candidate, plus the nullable-diff guard, passing.
- **Reproduction:** a fresh `new-task.sh` checkout of the pushed branch, with only the manifest's paths synced: 0 of 349 rows moved against the first checkout (status, reason and diff), stale-binary guard on. About 2 minutes after the build.
- **Frames:** I looked at two FAILs (`position-sticky-bottom-002`, `position-absolute-in-inline-008a`). Both are real renders that differ visibly from their references. Sticky reads 0 pass on develop, and #851 is still a draft.

### Limits
- **`wpt_sync.sh` did not run as a script.** This seat refuses it, so its git steps ran by hand with the same `--stdin` list, and `wpt_coverage.py` ran with `--no-sync --no-build`. R1 should run `python3 scripts/wpt_coverage.py` whole.
- **"Fresh clone" is a fresh checkout**, as in T13 and T14.
- **The blank gate is unchanged, as the row asks, and it is coarse here.** It calls under 0.1% ink (480 px) blank, so 37 ERRORs include thin frames with real ink: `position-sticky-table-td-subpixel-zoom` has 444 on both sides and would match. Scoring those needs a zero-ink rule for reftests; Atlas's call.
- **7 FAILs differ by under 0.1%.** The rule stays exact RGB, and they were not separated from real failures.
- **`stage_html`'s root-absolute rewrite still uses a regex** and could rewrite inside another attribute's quotes. A regex scan of the manifest's pages finds none that do this.

### FAILs by row

**B / seed (1)**

- `css-inline/empty-span-size-002` 0.0115%

**C10 / css-transforms-2d (21)**

- `css-transforms/scale/svg-scale-009` 8.3333%
- `css-transforms/scale/svg-scale-017` 8.3333%
- `css-transforms/transform-origin/svg-origin-relative-length-008` 4.9375%
- `css-transforms/transform-origin/svg-origin-relative-length-016` 4.9375%
- `css-transforms/transform-origin/svg-origin-relative-length-024` 4.6875%
- `css-transforms/transform-origin/svg-origin-relative-length-032` 4.6875%
- `css-transforms/transform-origin/svg-origin-relative-length-040` 4.6875%
- `css-transforms/transform-origin/svg-origin-length-in-002` 4.2008%
- `css-transforms/transform-origin/svg-origin-length-pt-005` 2.2969%
- `css-transforms/transform-origin/svg-origin-length-007` 2.1667%
- `css-transforms/matrix/svg-matrix-001` 2.0833%
- `css-transforms/matrix/svg-matrix-009` 2.0833%
- `css-transforms/matrix/svg-matrix-017` 2.0833%
- `css-transforms/matrix/svg-matrix-025` 2.0833%
- `css-transforms/matrix/svg-matrix-033` 2.0833%
- `css-transforms/matrix/svg-matrix-049` 2.0833%
- `css-transforms/matrix/svg-matrix-057` 2.0833%
- `css-transforms/matrix/svg-matrix-065` 2.0833%
- `css-transforms/rotate/svg-rotate-3args-invalid-003` 0.8%
- `css-transforms/matrix/svg-matrix-041` 0.3333%
- `css-transforms/transform-table-006` 0.0975%

**C10 / css-transforms-3d (19)**

- `css-transforms/3dtransform-and-filter-no-perspective-001` 16.3898%
- `css-transforms/css-transform-3d-transform-style` 6.25%
- `css-transforms/preserve3d-and-flattening-002` 4.1667%
- `css-transforms/preserve3d-and-flattening-z-order-006` 4.1667%
- `css-transforms/transform3d-preserve3d-004` 4.1667%
- `css-transforms/transform3d-sorting-003` 4.1667%
- `css-transforms/perspective-untransformable-no-stacking-context` 3.875%
- `css-transforms/css-transform-3d-rotate3d-Y-negative` 3.0%
- `css-transforms/css-transform-3d-rotateX-negative` 3.0%
- `css-transforms/css-transform-3d-rotateY-positive` 3.0%
- `css-transforms/perspective-origin-x` 2.6042%
- `css-transforms/perspective-children-only-fixpos` 2.25%
- `css-transforms/css-rotate-2d-3d-001` 2.0833%
- `css-transforms/perspective-zero-point-five` 2.0833%
- `css-transforms/transform3d-backface-visibility-003` 2.0833%
- `css-transforms/transform3d-backface-visibility-006` 2.0833%
- `css-transforms/transform3d-perspective-005` 1.5625%
- `css-transforms/transform3d-scale-004` 1.0417%
- `css-transforms/transform3d-preserve3d-012` 0.0888%

**C15 / css-position-absolute (23)**

- `css-position/static-position/vlr-ltr-ltr` 89.9044%
- `css-position/static-position/vrl-ltr-ltr` 89.9044%
- `css-position/position-absolute-in-inline-008a` 16.199%
- `css-position/position-absolute-in-inline-011` 16.199%
- `css-position/position-absolute-in-inline-009` 14.3125%
- `css-position/position-absolute-in-inline-007b` 11.999%
- `css-position/containing-block-change-button` 7.5833%
- `css-position/position-absolute-in-inline-006` 4.75%
- `css-position/static-position/htb-rtl-rtl` 3.6%
- `css-position/position-absolute-semi-replaced-stretch-button` 1.7163%
- `css-position/position-absolute-semi-replaced-stretch-input` 1.2758%
- `css-position/position-absolute-dynamic-static-position-inline` 1.0417%
- `css-position/position-relative-table-tfoot-top-absolute-child` 0.7812%
- `css-position/static-position/inline-level-absolute-in-block-level-context-003` 0.6042%
- `css-position/static-position/inline-level-absolute-in-block-level-context-006` 0.6042%
- `css-position/position-relative-table-tbody-left-absolute-child` 0.5208%
- `css-position/position-relative-table-tfoot-left-absolute-child` 0.5208%
- `css-position/position-relative-table-thead-top-absolute-child` 0.5208%
- `css-position/position-relative-table-tr-top-absolute-child` 0.5208%
- `css-position/static-position/inline-level-absolute-in-block-level-context-001` 0.5208%
- `css-position/static-position/inline-level-absolute-in-block-level-context-005` 0.3438%
- `css-position/static-position/inline-level-absolute-in-block-level-context-008` 0.2604%
- `css-position/static-position/inline-level-absolute-in-block-level-context-011` 0.2604%

**C2 / css-overflow (16)**

- `css-overflow/overflow-body-propagation-010` 77.0417%
- `css-overflow/overflow-body-propagation-014` 32.6667%
- `css-overflow/scrollbar-gutter-root-both-edges` 9.3542%
- `css-overflow/overflow-clip-margin-svg` 2.1667%
- `css-overflow/paint-containment-svg` 2.1667%
- `css-overflow/no-scrollable-overflow-vertical-rl` 2.0833%
- `css-overflow/overflow-clip-margin-007` 1.875%
- `css-overflow/overflow-clip-margin-010` 1.8635%
- `css-overflow/overflow-clip-x-visible-y-svg` 1.5625%
- `css-overflow/clip-004` 1.0417%
- `css-overflow/overflow-clip-margin-018` 0.8667%
- `css-overflow/overflow-clip-margin-013` 0.75%
- `css-overflow/overflow-clip-margin-015` 0.75%
- `css-overflow/overflow-img-scroll-non-replaced` 0.3762%
- `css-overflow/overflow-clip-margin-mul-column-border-box` 0.2875%
- `css-overflow/text-overflow-ellipsis-editable-div-with-caret` 0.031%

**C5 / css-ui-outline (6)**

- `css-ui/outline-022` 2.0833%
- `css-ui/outline-style-014` 0.5133%
- `css-ui/outline-style-012` 0.44%
- `css-ui/outline-020` 0.4083%
- `css-ui/outline-style-011` 0.1733%
- `css-ui/outline-style-013` 0.1567%

**C6 / css-lists (11)**

- `css-lists/inline-list-marker` 3.6015%
- `css-lists/list-style-type-string-005a` 2.6267%
- `css-lists/list-style-type-string-007` 2.0083%
- `css-lists/nested-marker-styling` 1.38%
- `css-lists/counters-003` 1.0075%
- `css-lists/list-style-type-string-001b` 0.7179%
- `css-lists/list-style-type-decimal-vertical-lr` 0.3144%
- `css-lists/details-open` 0.2985%
- `css-lists/counters-scope-003` 0.2342%
- `css-lists/list-marker-symbol-bidi` 0.2067%
- `css-lists/counters-006` 0.1583%

**C6 / css-text-basics (22)**

- `css-text/white-space/trailing-ideographic-space-break-spaces-007` 5.2083%
- `css-text/text-transform/text-transform-fullwidth-010` 4.9154%
- `css-text/letter-spacing/letter-spacing-200` 3.0354%
- `css-text/text-align/text-align-justify-tabs-004` 1.8715%
- `css-text/text-align/text-align-justify-001` 1.8229%
- `css-text/text-align/text-align-start-014` 1.5625%
- `css-text/letter-spacing/letter-spacing-bengali-yaphala-001` 1.3565%
- `css-text/white-space/trailing-ideographic-space-020` 1.0417%
- `css-text/white-space/text-wrap-balance-line-clamp-006` 0.8281%
- `css-text/white-space/break-spaces-011` 0.5208%
- `css-text/white-space/textarea-pre-wrap-005` 0.5%
- `css-text/text-align/text-align-last-end` 0.42%
- `css-text/white-space/white-space-letter-spacing-001` 0.3867%
- `css-text/text-transform/text-transform-tailoring-003` 0.3173%
- `css-text/text-transform/text-transform-full-size-kana-001` 0.2854%
- `css-text/white-space/trailing-other-space-separators-break-spaces-003` 0.2854%
- `css-text/white-space/trailing-other-space-separators-break-spaces-015` 0.2854%
- `css-text/white-space/break-spaces-before-first-ideographic-char-005` 0.2604%
- `css-text/white-space/ws-break-spaces-applies-to-010` 0.2173%
- `css-text/white-space/pre-wrap-align-left-002` 0.1667%
- `css-text/letter-spacing/letter-spacing-nesting-001` 0.1546%
- `css-text/white-space/tab-stop-threshold-001` 0.0537%

**C7 / css-position-sticky (23)**

- `css-position/sticky/position-sticky-fixed-ancestor-002` 100.0%
- `css-position/sticky/position-sticky-fixed-ancestor-003` 100.0%
- `css-position/sticky/position-sticky-in-fixed-container` 16.3333%
- `css-position/sticky/position-sticky-padding-002` 8.8333%
- `css-position/sticky/position-sticky-padding-001` 8.7917%
- `css-position/sticky/position-sticky-escape-scroller-004` 8.3333%
- `css-position/sticky/position-sticky-bottom-002` 4.1667%
- `css-position/sticky/position-sticky-bottom-003` 4.1667%
- `css-position/sticky/position-sticky-escape-scroller-002` 4.1667%
- `css-position/sticky/position-sticky-right-002` 4.1667%
- `css-position/sticky/position-sticky-right-003` 4.1667%
- `css-position/sticky/position-sticky-left-002` 2.0833%
- `css-position/sticky/position-sticky-left-003` 2.0833%
- `css-position/sticky/position-sticky-offset-print` 2.0833%
- `css-position/sticky/position-sticky-rtl` 2.0833%
- `css-position/sticky/position-sticky-top-002` 2.0833%
- `css-position/sticky/position-sticky-top-003` 2.0833%
- `css-position/sticky/position-sticky-table-td-bottom` 1.8229%
- `css-position/sticky/position-sticky-table-td-top` 1.8229%
- `css-position/sticky/position-sticky-table-th-top` 1.8229%
- `css-position/sticky/position-sticky-table-th-bottom` 1.5625%
- `css-position/sticky/position-sticky-top-and-bottom-003` 1.5625%
- `css-position/sticky/position-sticky-table-pixel-rounding` 0.0781%

**C8 / css-masking-clip-path (25)**

- `css-masking/clip-path/clip-path-document-element-will-change` 68.8542%
- `css-masking/clip-path/clip-path-element-userSpaceOnUse-004` 66.6652%
- `css-masking/clip-path/animations/clip-path-path-interpolation-with-zoom` 16.6667%
- `css-masking/clip-path/clip-path-rect-002` 14.005%
- `css-masking/clip-path/clip-path-xywh-001` 14.005%
- `css-masking/clip-path/clip-path-element-userSpaceOnUse-001` 10.9167%
- `css-masking/clip-path/clip-path-path-with-zoom` 8.3333%
- `css-masking/clip-path/clip-path-polygon-003` 7.7917%
- `css-masking/clip-path/clip-path-polygon-007` 6.25%
- `css-masking/clip-path/clip-path-polygon-010` 6.25%
- `css-masking/clip-path/clip-path-polygon-012` 6.25%
- `css-masking/clip-path/clip-path-reference-box-001` 6.25%
- `css-masking/clip-path/clip-path-columns-shape-001` 5.25%
- `css-masking/clip-path/clip-path-inline-006` 5.2083%
- `css-masking/clip-path/clip-path-rotated-will-change-transform` 3.8325%
- `css-masking/clip-path/clip-path-shape-009` 3.6667%
- `css-masking/clip-path/clip-path-shape-006` 3.2592%
- `css-masking/clip-path/clip-path-polygon-005` 3.125%
- `css-masking/clip-path/clip-path-blending-offset` 2.4792%
- `css-masking/clip-path/clip-path-mix-blend-mode-1` 2.0833%
- `css-masking/clip-path/clip-path-shape-foreignobject-non-zero-xy` 2.0833%
- `css-masking/clip-path/clip-path-reference-box-004` 1.0417%
- `css-masking/clip-path/clip-path-path-002` 0.9027%
- `css-masking/clip-path/clip-path-shape-002-units` 0.9027%
- `css-masking/clip-path/clip-path-inset-round-percent` 0.0138%

**C8 / css-masking-mask (11)**

- `css-masking/mask-image/mask-repeat-1` 8.4271%
- `css-masking/mask-image/mask-image-url-local-mask` 5.3333%
- `css-masking/mask-image/mask-repeat-2` 4.1667%
- `css-masking/mask-image/mask-clip-5` 3.125%
- `css-masking/mask-image/backdrop-filter-good-and-bad-mask-image` 2.939%
- `css-masking/mask-image/mask-size-cover` 2.59%
- `css-masking/mask-image/mask-image-svg-foreignobject-zoomed` 2.0833%
- `css-masking/mask-image/mask-origin-1` 2.0833%
- `css-masking/mask-image/mask-position-1a` 2.0833%
- `css-masking/mask-image/mask-position-7` 2.0833%
- `css-masking/mask-image/mask-position-5` 1.0417%

## Receipt (`scripts/receipt.py`)
`branch` reads `HEAD` because the receipt ran in the detached fresh checkout; the branch is `atlas/dt-t15-wpt-coverage`. The campaign ran on the parity build through a no-op `cargo` on PATH, per the 10-29 recipe.

```json
{
 "base_sha": "origin/develop",
 "binary": "target/parity/parity-capture",
 "binary_mtime_utc": "2026-11-01T17:50:23.486514Z",
 "binary_sha256": "918bb6eed1c805aa56fb805d271835013ca3bd55412c38678c604e342c2c994e",
 "branch": "HEAD",
 "campaign": {
  "cases": 26,
  "failed": 0,
  "file": "parity-baseline/parity_test_results.json",
  "mean_diff_pct": 1.1095,
  "passed": 26,
  "sha256": "a739e9336e48e2c4911019691e0a6413acd199389208b5bcd9d7666c994c1d16",
  "timestamp": "2026-11-01T12:53:20.399110"
 },
 "candidate_sha": "3d54f8fdf6333d175e1470d0390ad21f7d080e1b",
 "cargo": "cargo 1.91.0 (ea2d97820 2025-10-10)",
 "cargo_lock_sha256": "241df6e8a50e5a0d93f45d52e91b46ed3f39286897f689b06e8e39e7b7a1e97a",
 "chrome_version": null,
 "cpu": "arm",
 "dirty_state": false,
 "effective_engine_flags": {},
 "features": null,
 "host": null,
 "note": "T15: no engine change; scripts, manifest and README only",
 "os": "macOS-26.5.2-arm64-arm-64bit",
 "profile": "parity",
 "raw_runs": [
  {
   "bytes": 137885,
   "file": "trench/wpt/last-run.json",
   "sha256": "3927d243e083f26324a0f8917ebf21178d0fa977c6e5509398a9b7a4b889c89d"
  }
 ],
 "repo": "https://github.com/hiwavebrowser/hiwave-macos.git",
 "rustflags": null,
 "sccache": true,
 "target": "aarch64-apple-darwin",
 "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)",
 "utc": "2026-11-01T17:54:20.731374Z",
 "work_package": "parity-capture"
}
```

🤖 Generated with [Claude Code](https://claude.com/claude-code)
