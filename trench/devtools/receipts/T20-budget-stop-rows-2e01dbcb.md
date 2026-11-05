# T20: repeated budget stops are one row (draft PR body, held at the PR cap)

Branch `atlas/dt-t20-budget-stop-rows` @ 2e01dbcb, base develop 82893eac.
Pete 11-04: "thousands of errors reported in the inspector" (959 identical
"Script stopped at the script budget" lines on reddit).

## What changes
1. **Log line and stop note**: one per (page, source) every 5 s, carrying
   `repeats=N`. Every stop still gets its `ScriptRecord` (the board's counts
   are unchanged).
2. **One stop text**: the stopped turn's error is one fixed engine line,
   "stopped at the script budget". The watchdog's interrupt (26 chars) and the
   host-call deadline refusal (63 chars) gave two hidden texts that split a run
   into rows. The stop's report is **the last exception queued when the turn
   ended**, read before the stop note runs (`queued_exception_reports`, new in
   rustkit-js/bindings). The note is page script (`console.warn` may be the
   page's own), and its own error came after the stop's.
3. **Inspector console**: `devtools_console_entries` folds a run of identical
   budget stops into one entry with `repeat`/`firstMs`/`lastMs`; the panel
   folds across polls, shows ×N with the first and last time, and its
   error/warn counts include repeats.
4. **Only budget stops fold** (`budgetStop` on the entry; same rule in engine
   `same_line` and panel `sameConsoleLine`). In shape-only mode,
   `console.log('a'/'b'/'c')` all read `<string len=1>`. Folding them would
   hide that the page made three calls.

## Red before
- 9dd722a0: the three T20 tests with the fix switched off, 3 of 3 engine tests
  and 1 panel test red. The red run shows Pete's pattern: a warn note, then
  the error, repeated 100 times.
- 0b69972b: `an_error_from_the_stop_note_is_not_taken_for_the_stop` (the page's
  `console.warn` throws) is red at 4d84750c:
  `[raw stop (63 chars) x1, fixed x3]`. That is the same shape as the loaded
  suite run on 11-05 02:10, which gave 101 error rows for 100 stops.

## Tests at 2e01dbcb
- budget_stop_group 3/3; devtools_tests + vm_interrupt + leaving_input +
  inspector 143/0 (1 ignored); content_thread incl. the panel-wake test and
  the Chart.js report page: green.
- Panel node tests (`scripts/tests/test_inspector_console_groups.py`) 8/8,
  including the new "identical page lines never fold" test.
- At the test's 5 ms budget, a loaded machine (load 12 to 27) also stops the
  engine's own `pointerover`/`mousemove` dispatch, which has no listener.
  These are real stops of other sources, and they end the pointermove run.
  The two pointermove tests count only pointermove's rows. The strict
  "1 note + 1 row ×100" check runs whenever no other source was stopped.
- Full engine suite at 2e01dbcb (load 9 to 27, 2905 s): **1599 passed, 23
  failed, 28 ignored**. 22 of the failures are the GPU test guard
  (`lib.rs:130`, "waited Ns for ... to finish with the GPU"). The 23rd is the
  wall-clock bound in
  `vm_interrupt_tests::a_pure_spin_in_a_load_script_is_stopped_at_the_load_budget`.
  All 23 pass when re-run by module with `--test-threads=1`: vm_interrupt +
  consent_click 16/0, and computed_read + background_image_fetch +
  adopted_sheets + author_svg_stroke + aspect_ratio_empty_block +
  abspos_percent_height_image 44/0.
- `cargo check -p hiwave-app`: clean.

## Campaign
26/26, mean 1.1095%, the same mean as #835/#838/T12.

## Cost
Logging off: unchanged (one `queued_exception_reports` read per stopped turn,
only when the turn was stopped). On: fewer lines.

## Receipt (`scripts/receipt.py`)

```json
{
 "base_sha": "82893eac",
 "binary_sha256": "d84d66b5c8eb9203c1b5c2a2f61a5bdf3d434f305782eba480961b7ba3b2a262",
 "campaign": {"cases": 26, "failed": 0, "mean_diff_pct": 1.1095, "passed": 26,
  "sha256": "3171b5a03c723fdf984c36e20945dd88b067d737c17505d5ec7e34bb3ab46769"},
 "candidate_sha": "2e01dbcbfa23629fce3984958004c0188a0b3cea",
 "cargo": "cargo 1.91.0 (ea2d97820 2025-10-10)",
 "dirty_state": false,
 "features": "headless",
 "profile": "parity",
 "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)",
 "work_package": "T20-budget-stop-rows"
}
```
