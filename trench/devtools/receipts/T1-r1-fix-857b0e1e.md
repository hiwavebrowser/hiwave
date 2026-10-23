**#784 R1 HOLD answered: new head `857b0e1e`** (one commit on 7f5d8301, no force-push)

**Must-fix: done.** Error text reaching the Inspector now follows the Inspector's own `keep_error_text`, never the console mirror.
- `Inspector::stack_text` drops function names unless `keep_error_text`. That covers `script_error.stack`, `console.stack` and `console.error_stack`, since all three go through it.
- `inspector_glue::script_error` drops `message` unless `inspector.keeps_error_text()`. This also closes the `script_error.message` path you noted on develop.
- The runtime still keeps its text while `HIWAVE_CONSOLE_LOG` is on, for the tracing log only.
- Red-before test `the_console_mirror_does_not_put_error_text_in_the_inspector`: mirror forced on, `keep_error_text` off. It asserts `message: null` and positions-only stacks for `script_error`, `console.stack` and `console.error_stack`, and that the page's message text and function names appear nowhere in the records. At 7f5d8301 it failed with `"message":"secret-message"` and `at inner (…)`, `at three (…)` in the records.

**Nits:**
1. Forged frame: confirmed possible before the fix. `function_name` now drops a computed name holding a control character, `(` or `)`, so the frame keeps its position without a name. Test: `a_computed_function_name_cannot_forge_a_frame`.
2. `inserted_by` is gated on `report.located`, like `location`. Test: `an_eval_throw_does_not_borrow_its_scripts_inserter`.
3. GPU-backed `inspector_page_tests`: 17/17 in one clean run (277 s).
4. Docs: `INSPECTOR_EVENT_LOG.md` now says that names and messages follow `keep_error_text` only, and covers the dropped computed names and the `inserted_by` gate.

**Tests at 857b0e1e (Mac):**
- engine `inspector`/`console_log`/`error_text` filters: 104/104
- `inspector_page_tests`: 17/17
- `rustkit-js`: all suites green

**Campaign:** 26/26, mean 1.11%, worst article-typography 4.79%. It is unchanged from 7f5d8301, as expected: Inspector-only change.

**Pre-existing, outside this PR (flagging, not fixing here):** with `HIWAVE_CONSOLE_LOG` on, `attach` skips `set_console_redaction`. The Inspector's `console.message` therefore carries the page's console text even when `keep_console_text` is off. It is the same mirror-overrides-Inspector shape, and it is on develop too. The fix needs the runtime to build both a text line (for the mirror) and a shape line (for the Inspector), which changes `ConsoleHandler` and `console_member`. I'd rather do that as its own small PR than grow this one; say if you want it here instead.

Receipt (`scripts/receipt.py`):
```json
{
 "base_sha": "7f5d8301c9db30109f52116dcd14a034cd93e3a9",
 "binary": "target/release/parity-capture",
 "binary_sha256": "751420ba7cee746656a49b386fbb47b4d1f973bfccb8fb397e8074ae59f34cc2",
 "campaign": {"cases": 26, "failed": 0, "mean_diff_pct": 1.1078, "passed": 26, "file": "scratch/camp-t1r2-857b0e1e.json", "sha256": "dd4d21b41a27c9f994a4c98f1c1c67d45d12e19b45785f1c9be7fbce7ca2009e"},
 "candidate_sha": "857b0e1ea9f2c92ca4b2e5b04e5e8fcff719f2d6",
 "cargo": "cargo 1.91.0 (ea2d97820 2025-10-10)",
 "cargo_lock_sha256": "d43bf3f40c046d3d625a2876c81a524fcaac59b37460f330942147537a4c8cb7",
 "dirty_state": false,
 "os": "macOS-26.5.2-arm64-arm-64bit",
 "profile": "release",
 "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)",
 "utc": "2026-10-23T17:18:58.637501Z",
 "work_package": "T1"
}
```
(`profile` reads `release` because the campaign tool copies the binary to `target/release/`; it was built with `--profile parity`.)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
