Headless suite follow-up at 49d22b5d (owed from my earlier comment). Every run was single-threaded with `--features headless`, from new checkouts of 49d22b5d and of develop 95691f85.

**1. The six modules from the cap-cut run, on the candidate.** Run: `container_query consent_click control_percent_height control_semantics css_animations page_script_tests`, single-threaded. Load was 18 to 50.

Result: 87 passed, 6 failed.
- container_query, consent_click, control_percent_height, control_semantics and css_animations all pass. The 8 failures from these modules in the default-thread run were load timeouts.
- The 6 failures are all budget or wall-clock tests:
  - `page_script_tests::a_module_still_running_at_the_budget_is_stopped_at_its_next_host_call` ran 5.44 s.
  - `page_script_tests::a_script_still_running_at_the_budget_is_stopped_at_its_next_host_call` ran 4.89 s.
  - `page_script_tests::a_sheet_that_misses_the_budget_applies_when_it_arrives`: "the load waited for the late sheet".
  - `page_script_tests::a_stalled_subresource_is_dropped_at_the_subresource_budget`: 5.35 s against a 2.5 s bound. This is the test Talos saw as a Linux flake (T27).
  - `page_script_tests::scripts_are_fetched_while_the_subresources_load`: 7.74 s.
  - `error_page_script_tests::an_inserted_chunk_chain_past_the_budget_renders_on_the_live_loop`: the `/chunk-b.js load` event was missing before the budget cut.

**2. The same six by exact name, back to back on both arms.** Load was about 17 to 21 for both.

| test | develop 95691f85 | 49d22b5d |
|---|---|---|
| inserted chunk chain past the budget | ok | ok |
| module still running at the budget | ok | ok |
| script still running at the budget | ok | ok |
| sheet that misses the budget | FAILED | FAILED |
| stalled subresource dropped at the budget | FAILED (3.12 s) | FAILED (3.24 s) |
| scripts fetched while subresources load | FAILED (5.13 s) | FAILED (6.29 s) |

**Classification:** none of the failures is caused by this PR. Each arm shows the same pattern at the same load, and every failing assert is a wall-clock bound. A quiet-machine rerun is still owed, because the load never dropped below 15 this session. CSS var() has no path into load budgets. This PR changes the computed value of an unresolvable `var()` and `apply_initial_value`.
