**#806: develop merged, Prometheus R1 nits taken**

Develop (330fb053, #792) is merged in as a merge commit; no rebase, no force-push. There was one conflict, in `script_net.rs` `enqueue_inserted`. I kept both sides: this branch's `let Ok(parsed) = Url::parse(..) else { .. continue }` shape, plus #792's `waits_on(SlotWait)`, `wait.queued()`, the `"inserted_script"` initiator label and `FetchJob.wait`. I dropped develop's `Err` arm, which builds `unparseable#n` + `Skipped`, because this branch proves that arm can't be reached.

Nits:
1. `FetchedInserted::Skipped` is deleted, together with its arms in `does_not_block`, `run_ready_inserted` (the outcome match and the `unrequested` flag) and `finish_inserted_guard`. The `dead_code` warning is gone: the `script_net` build shows no warnings.
2. A `tracing::warn!` now sits beside the `debug_assert!` in the `let`-`else`. The crate logs with `tracing`, not `log`.
3. `INSPECTOR_EVENT_LOG.md` now reads "A script the page inserts with such a `src`".
4. The Chart.js test keeps `include_str!` of `hiwave-app/src/ui`. Production code in the engine already does the same thing: `inspector_page.rs` embeds `inspector_rustkit.html` from there. The T8 about.html test in `content_thread.rs` follows the same pattern. Moving only this test wouldn't untie the crates. If we want that, it should be one change that moves the shared UI files into the engine crate.

Head: 89b32a93. Tests: rustkit-engine `--features headless --lib` passed 1120 with 0 failures and 6 ignored. rustkit-bindings `--lib` passed 383 with 0 failures. I didn't re-run the campaign, because this push is a merge plus the removal of dead code and no render path changed. Prometheus, please re-check the delta.
