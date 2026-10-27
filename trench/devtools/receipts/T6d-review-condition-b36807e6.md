**Review condition + Prometheus nits answered @ b36807e6.** This was a plain push on `atlas/dt-t6d`. No develop merge was needed, because the PR was CLEAN.

**Condition (hot loop, then hang): made visible, not delivered.**
- **Why it isn't delivered.** Boa has no page-side drain hook. Its interrupt is a stop word checked at loop back-edges, not a callback with access to the runtime's `Diagnostics`. Draining from it would mean a Boa change, so I didn't attempt delivery.
- **What changed: an atomic held count.** The runtime keeps the number of held calls in an `Arc<AtomicUsize>` that the view's `Inspector` owns (`Inspector::console_held()`, one atomic load, no page, no lock).
  - The glue hands the counter to each document's runtime at attach (`set_console_held_counter`), and the runtime stores `console.len()` there on every hold.
  - The counter returns to 0 on every take (a live hand-over or the flush).
  - The panel already reads the Inspector directly (as it does for `page_crashed`), so it can show "K console lines held by a running script" from this.
- **The panel line itself is not in this PR.** It would go in `devtools_panel.rs`, which #809 rewrites, so it is a one-line follow-up after both land. It also needs the window to wake while the page is hung, which is the same question as #809's busy line.
- **Tests:**
  - rustkit-js `calls_held_past_the_live_cap_are_counted_while_the_script_hangs`: 300 calls, then a 500 ms spin. While the spin runs, a reader thread sees `held + delivered == 300` with held > 0. The count is 0 after the flush, and all 300 are delivered.
  - Engine `console_calls_held_by_a_hung_script_are_counted_without_the_page`: the same through a real page, the glue and `Inspector::console_held()`, with a reader thread on the Inspector's records.

**Prometheus nits**
1. **`LiveConsole` snapshot: fixed.** `JsRuntime` now keeps the `set_console_live` predicate and rebuilds the live delivery in `set_console_handler`, `set_console_shape_handler` and `set_console_live`. Calls go to the handlers set last, whatever the order. Test: `live_calls_go_to_the_handler_set_last_whatever_the_order` (live set first, handler A, then handler B; B gets both calls live and A gets none).
2. **The dropped line names the rate cap.** When the live cap held the calls, the line reads `K console calls dropped (more than 1024 held; console rate cap)`. The flag travels with the held calls, so the flush path says it too. The hot-loop test asserts it.
3. **600 ms test.** The spin is now 1000 ms, with the same 400 ms early threshold, so the margin is 600 ms.

**Review nits**
1. **The cap counts hand-overs, not records.** The `MAX_CONSOLE_LIVE` doc, the `set_console_live` doc and INSPECTOR_EVENT_LOG.md now say so: about 1,224 records a second at most.
2. **The 100 ms flush test** now asserts order and a gap under 250 ms. A live hand-over would be a whole 300 ms spin apart.
3. **The bound that could never fail** (lib.rs:1814) is replaced by `dropped > 0` plus the rate-cap wording check.
4. **Private doc link.** The `set_console_live` doc no longer links `diag::MAX_CONSOLE_LIVE`.
5. **Sink panic note:** acknowledged, no change.

**Red before:** 2/2. With the setter rebuild and the counter turned off, both new rustkit-js tests fail.

**Results**
- rustkit-js `--lib`: 88 passed, 0 failed (86 + 2).
- rustkit-bindings `--lib`: 382 passed, 0 failed.
- rustkit-engine `--lib inspector` filter: 110 passed, 0 failed.
- Full engine suite `--features headless --lib`: 1117 passed, 0 failed, 6 ignored (1116 + 1 new).
- Campaign: 26/26, mean 1.1078%. Every case is the same as at 99aa6e2c (log diff: only paths and the timestamp changed); log in `receipts/camp-t6d-b36807e6.log`.
