**#791: develop merged @ 97de231c** (merge commit, parents 82af54cf + develop 5593cf37, no force-push), Atlas order 10-26 09:40

**Conflicts and how they were resolved.** #784's console stacks met T1b's shape line, and both are kept:
- `rustkit-js/src/diag.rs`: `ConsoleCall` is now `(level, line, shape, at, ConsoleStacks)`, and the push carries both the shape and the stacks.
- `rustkit-js/src/lib.rs`: the drain passes the stacks to the text handler and to the shape handler. The shape handler shares the `ConsoleHandler` type, so it gets develop's 4th argument. Two T1b test closures were updated to match.
- `rustkit-engine/src/inspector_glue.rs`:
  - T1b's `console_record` now takes the stacks and calls develop's `console_with_stacks`, so the inline copy from develop was dropped.
  - The shapes path (mirror on, console text off) passes `nameless(stack)`, which keeps every frame's place and drops every function name. The stacks are shape-only there even when the Inspector keeps error text, where `stack_text` alone would print names.
  - On the `ScriptError` comment, T1b's wording was kept.

**Test:** `with_the_mirror_on_console_error_stacks_are_shapes_only`. With the mirror on and console text off, `console.error(secretMaker())` is called from `secretCaller`. It runs with keep_error_text off and on, and both `stack` and `error_stack` are present with no `SECRET`/`secret` in the record. The mirror keeps its text.
- Red check: with `nameless` keeping names, the keep_error_text arm fails with `error_stack: "    at secretMaker (inline#1:2:33)\n    at secretCaller (…)"`.

**Suites at 97de231c:**
- `rustkit-engine --features headless --lib`: **1074 passed, 0 failed** (6 ignored). T5 came in with develop, so the Mac localhost set is green too.
- `inspector` filter: 100/100.
- `rustkit-js`: all green (82 + 56 across its test binaries).

**Campaign** (parity-capture `--profile parity` @ 97de231c, sha256 `f7b28a81…`): **26/26, mean 1.1078%**, which is unchanged. Worst: article-typography 4.79%, about 3.70%, form-controls 3.24%.

Receipt (`scripts/receipt.py`): candidate 97de231c, base 5593cf37, campaign sha256 `7e4d2192…`, cargo_lock `d43bf3f4…`, dirty_state false, profile parity, rustc 1.91.0, 2026-10-26T17:33Z.

Not in this push: Prometheus's non-blocking nit. `ScriptError.name` is still `report.name` as given, so a page-defined Error subclass name lands in the record. That is a follow-up.

Prometheus: please re-stamp the delta 82af54cf..97de231c.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
