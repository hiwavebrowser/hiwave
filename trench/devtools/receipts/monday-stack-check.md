# Monday stack check (2026-10-26 00:35-01:05 ET, devtools lane)

Order: Atlas 10-25 20:15. Local only, nothing pushed. Checkout `~/Repos/.worktrees/dt-stack-0035`,
branch `local/monday-stack-0035` @ 9dde5667. The checkout is kept because done-task.sh refuses
unpushed commits, and this stack must not be pushed.
Load at start 2.78. This seat can't list processes: `ps` and `top` both need approval.

## Stack (develop ff6ad36a, then `--no-ff` in landing order)
| # | branch | head | merge | result |
|---|---|---|---|---|
| 1 | LW `atlas/dt-live-wake` | 93d75eb4 | 17f4e0a7 | clean (LW is 18 behind develop) |
| 2 | T3 `atlas/dt-script-life` | e1aceaa0 | b1e92a01 | clean |
| 3 | T4 `atlas/dt-diagnose` | c7ee3505 | c2b86d5a | clean (auto-merge parity-capture main.rs) |
| 4 | T5 `atlas/dt-mac-gates` | ff9de6a4 | 261c3c50 | clean (auto-merge engine lib.rs) |
| 5 | T8 `atlas/dt-inline-script` | 43169252 | 810fd44f | **1 textual conflict**, see A |
| 6 | T6 `atlas/dt-service` | a3652306 | 6a6eb306 | clean textually; **2 test failures**, see B |

### A. T8 vs T4: `crates/parity-capture/src/main.rs`, `struct Args` (one hunk)
T4 adds `--report` / `--report-text` just above `run_inline_scripts`. T8 rewrites the doc comment
on `run_inline_scripts`.
Resolution: keep T4's two args, then T8's doc comment. It's comments and args only, with no logic.
T8 lands after T4, so T8's develop merge does this.

### B. T3 vs T6: two T3 tests, no textual conflict
T6 makes every view keep a 512-record ring by default (`EngineConfig::default().inspector =
InspectorConfig::tab()`). T3's tests were written when nothing recorded by default.
1. `script_lifecycle_tests::with_nobody_listening_no_script_record_is_built`: `!inspector.is_active()`
   fails because the ring is a listener. T6 already moved its own equivalent test to `ring_off()`.
2. `inspector_engine_tests::a_page_throwing_any_engine_message_is_a_page_record_with_no_text`:
   `left: 406, right: 456`. The test has 153 scripts, and each now adds a T3 `script` record.
   456 errors plus those records outgrow 512, and the ring's first record is seq 108.

Resolution, belonging to **T6's develop merge after T3 lands**: both tests turn the ring off. Diff:
```diff
--- a/crates/rustkit-engine/src/inspector_engine_tests.rs
@@ fn a_page_throwing_any_engine_message_is_a_page_record_with_no_text() {
-    let (engine, view, _server) = load_page(EngineConfig::default(), vec![Route::html("/", page)]);
+    // 456 errors plus a script record per script outgrow the tab ring: keep
+    // the full buffer.
+    let (engine, view, _server) = load_page(ring_off(), vec![Route::html("/", page)]);
--- a/crates/rustkit-engine/src/script_lifecycle_tests.rs
@@ fn with_nobody_listening_no_script_record_is_built() {
-    let mut engine = Engine::new(EngineConfig::default()).expect("engine");
+    // The tab ring off (`HIWAVE_DEVTOOLS_RING=0`): the ring is a listener.
+    let config = EngineConfig { inspector: InspectorConfig::default(), ..EngineConfig::default() };
+    let mut engine = Engine::new(config).expect("engine");
```
I didn't commit to `atlas/dt-service`: a merge commit there would pull T3 in before T3 lands.
With the fix, the two tests plus T3's lifecycle tests pass 6/6.

**Question for Atlas (product, not a merge fix):** one yahoo load writes 562 records (request 196,
response 188, T3 `script` 114, relayout 38, ...). With T3 + T6, a panel opened after the load has
lost the first ~50 records, including `navigation_start`. `diagnose` is unaffected because it reads
the event-log sink, not the ring. Raise `TAB_RING_CAPACITY`, or keep it at 512?

## Results on the merged stack
- Engine suite (`rustkit-engine --features headless --lib`) @ 6a6eb306, before the fix:
  **1079 passed, 2 failed (B1, B2), 6 ignored**, 962 s. The Mac localhost five pass (T5 is in the
  stack). Nothing else failed.
- After the fix (9dde5667): the two failures plus `script_lifecycle_tests` pass 6/6. I didn't re-run
  the full suite; the change is test-only, two lines.
- parity-capture tests: 35/35.
- Campaign (parity profile, binary sha256 `4218c775…`): **26/26, mean 1.1078%**, the same as
  develop. Worst: article-typography 4.79%, about 3.70%, form-controls 3.24%.

## T4 acceptance read (yahoo, cold, on the stack)
`scripts/diagnose.py https://www.yahoo.com/ --binary target/parity/parity-capture` (live 25 s,
no shield):
**wall clock 31.0 s** (two runs, 31.0 s each). The top lines were the same both times.
Top cause, quoted:
> 1. [R10] the first viewport has no text and no image (154 elements, document 800px tall)
> 2. [R5] the page's own script: uncaught SyntaxError in https://www.yahoo.com/_nca/_next/static/chunks/7730-fa1a767b0fc46f30.js:1:6278 (x2); then 0 fetch/XHR to www.yahoo.com

Lines 3-4 are R5 logged Error/TypeError in chunk 87c73c54. Line 5 is R4: no page script ran
until t=4.6 s. Line 6 is R4: one s.yimg.com script still open at the end. "Not checked: R6 shield",
because T2 (#792) isn't in this stack.
Reading: R10 is the symptom and R5 line 2 is the cause. 7730:1:6278 is the #777 innerHTML bug
(Next `__next_s`), and after it the page makes 0 fetches to its own host (Chromium makes 22).
Difference from the T4d read (10-24, LW+T3): back then the page was blank (R10) only with #777
applied too. Today it's blank without #777. I haven't found the cause: it's either a newer yahoo
build or something in T5/T8/T6. Not bisected.
