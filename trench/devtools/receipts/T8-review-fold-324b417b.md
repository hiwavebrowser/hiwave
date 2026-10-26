**#799 review items folded @ 324b417b** (plain push onto 7a622c3b, no force-push), Atlas order 10-26 11:40

1. **Navigation cancel in `load_html`'s script phase.** `run_html_load_scripts` now takes the load's `NavWatch`. Before each inline script and before each lifecycle step (`DOMContentLoaded`, `load`) it checks `nav_cancel::cancelled` and stops if the load was cancelled. `load_html_as` then calls `load_cancelled`, the same teardown the URL path uses (`LoadEndedEarly`, `NavigationFailed: cancelled`), and returns with no `PageLoaded`.
   - Test: `load_cancel_tests::a_cancel_between_two_scripts_of_an_html_load_runs_neither_the_second_nor_the_lifecycle`. Script 1 registers DCL and load listeners, and a cancel lands at a new test-only phase `html-script:1`.
   - Result: only `inline#1` ran. `data-dcl` and `data-load` are unset, `NavigationFailed: cancelled` is sent, and there is no `PageLoaded`.
   - Red check: with both checks off (phase hook kept), it fails.
2. **`LoadFinished.scripts_over_budget`** on the HTML path counts `OverBudget` in the script log, as the URL path does, instead of a fixed 0.
3. **`--run-inline-scripts`** fails a capture only on `Threw`, `EngineFailed` or `OverBudget`. The test is `run_inline_scripts_fails_only_on_scripts_that_failed`, using a real `load_html`:
   - a page with an external `<script src>`, an inline module and a good inline script gives `Skipped` records and no failure;
   - a page with an external src plus a throwing inline script fails on `inline#2`.
4. **hiwave-smoke `--html-file` capture: NOT DONE.** I built it (`--profile parity`) and the window locks were free, but this seat's allowlist needs approval to run a built binary directly (hiwave-smoke, and parity-capture outside `camp.py`). Running it needs a seat grant, or someone runs `scripts/builtins_capture.sh` (about.html at 1280x800 is the one to check). Context: `EngineConfig::for_parity_testing()` has `javascript_enabled: true`, so smoke fixtures do run their inline scripts since T8.

Prometheus nits 1 and 3 (a Chart.js report-page test; carried callback throws reaching the Inspector) are not in this push. They are follow-ups.

**Suite** (`rustkit-engine --features headless --lib` @ 324b417b): 1075 passed, 1 failed. The failure is `error_page_script_tests::a_slow_post_load_fetch_or_import_holds_no_live_turn` ("a live turn held the window for 110.98 ms"), a wall-clock assert, at load 8.3. It passes alone (1/1, 4.2 s). `load_cancel` 11/11. parity-capture's new test passes.
**Campaign** (parity-capture `--profile parity` @ 324b417b, sha256 `e9284928…`): 26/26, mean 1.1078%, unchanged. Worst: article-typography 4.79%, about 3.70%, form-controls 3.24%.
Receipt (`scripts/receipt.py`): candidate 324b417b, base 7a622c3b, campaign sha256 `7da28e73…`, cargo_lock `d43bf3f4…`, dirty_state false, profile parity, rustc 1.91.0, 2026-10-26T18:00Z.

Prometheus: please re-stamp the delta 7a622c3b..324b417b.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
