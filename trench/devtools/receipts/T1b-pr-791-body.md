Dev-tools lane, package T1b (follow-up to the leak found on #784).

## Bug
With `HIWAVE_CONSOLE_LOG=1` (the tracing mirror), `inspector_glue::attach` skipped `set_console_redaction`, because the mirror logs the text the page wrote. The Inspector shared the same handler, so `console.message` reached the Inspector as page text even with `keep_console_text` off. That breaks the shape-only rule (Pete, 10-23). The bug is on develop, independent of #784.

## Fix
- rustkit-js: `JsRuntime::set_console_shape_handler` (and `DomBindings::set_console_shape_handler`). While one is set, each console call also builds a shape line (`describe::redacted_text`, the same as redaction) next to its line. At flush the shape handler gets it right after the console handler, for the same call. Covers the five logging methods and every `console_member` path (count/assert/time…), since they all go through `console_call`.
- engine glue: with the mirror on and `keep_console_text` off, the mirror gets the text line and the Inspector gets the shape line. The rest is unchanged: mirror off, or `keep_console_text` on.
- The console→Inspector body moved into `console_record` without change.

## Cost
Off (no shape handler): one `Cell<bool>` read per console call. On (mirror on, keep off, debugging only): one extra joined shape string per call.

## Red before
`inspector_engine_tests::the_console_mirror_does_not_put_page_text_in_the_inspector` (mirror forced on, default config vs `keep_console_text`). Before the fix:
```
left:  [["console Log secret-console-text 12 @inline#1:2:9", "console Info secret-label: 1 @inline#1:3:10"], [...same...]]
right: [["console Log <string len=19> <number> @inline#1:2:9", "console Info <string len=15> @inline#1:3:10"], ["console Log secret-console-text 12 ...", "console Info secret-label: 1 ..."]]
```
After: green. The test also asserts that the mirror still receives the text.

## Tests
- rustkit-js: all green (lib 82/82, incl. new `a_shape_handler_gets_shapes_beside_the_text_line`).
- rustkit-engine `--features headless --lib -- inspector console_log error_text`: 98/98 (336 s, includes GPU `inspector_page_tests`).

## Campaign (26 cases, binary built at 58800963, `--profile parity`)
Passed 26/26, mean 1.11% (1.1078, the same as develop/T1). Worst: article-typography 4.79%, about 3.70%, form-controls 3.24%. Inspector-only change; flat as expected.

## Receipt (`scripts/receipt.py`)
```json
{"binary_sha256": "fb53102b56df6d8cb5c2345d37eae18cc9dbd2034114f04b63641cf4582b5427",
 "branch": "atlas/dt-console-shape",
 "campaign": {"cases": 26, "failed": 0, "passed": 26, "mean_diff_pct": 1.1078,
              "file": "scratch/camp-cshape-58800963.json",
              "sha256": "fa7c284696852984d5c3b2b86daf8de52670811c0dbfc437821cdbcf55d01bfe"},
 "candidate_sha": "588009637c79941e265f59e8680a07bd61f64310",
 "cargo_lock_sha256": "d43bf3f40c046d3d625a2876c81a524fcaac59b37460f330942147537a4c8cb7",
 "dirty_state": false, "profile": "parity", "os": "macOS-26.5.2-arm64-arm-64bit",
 "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)", "utc": "2026-10-23T22:53:16Z",
 "work_package": "T1b-console-shape"}
```

Overlap: touches `inspector_glue.rs` / rustkit-js `diag.rs` like #784; whichever lands second merges develop.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
