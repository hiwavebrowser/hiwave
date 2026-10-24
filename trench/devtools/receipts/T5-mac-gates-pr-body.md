# test: clean Mac gates (six macOS-only engine tests that failed on every Mac run)

Branch `atlas/dt-mac-gates` @ 7a908255 (merges clean onto develop @ the 20:45 fetch, 19 behind). Test-only: every hunk is inside a `#[cfg(test)]` module, so no engine line changed and the 26-case campaign cannot move (not re-run; the shipped code is byte-identical).

All six tests were red on every Mac run; Linux CI never runs them (`target_os = "macos"` or headless-only).

| test | why it failed | fix |
|---|---|---|
| referrer_tests ×3, image_loader_routing | #445 denies a cross-origin loopback fetch (`localhost:PORT` from a `127.0.0.1:PORT` page) by design; fbc6268f updated the background-image test, these four were never updated | expect the request absent; Referer values stay pinned in rustkit-net `security.rs` (d91d3210) |
| error_page_script_tests::navigating_away_drops_an_inserted_script_still_fetching | the fetch is on its own thread and can still be connecting when `load_url` returns | wait up to 1.5 s for the request, assert it is still unanswered (server answers at 2 s) (4fa6d6f8) |
| remote_font_tests::remote_web_fonts_are_fetched_concurrently | `load_html` leaves the page at about:blank; the private-address vet gives a page with no http(s) origin public-only, so all 8 faces failed `AddressDenied("127.0.0.1 resolves to 127.0.0.1")` (0 of 8 loaded) | set the test page's URL to the font host, so the fetches are same-origin loopback (7a908255) |

Also in 7a908255: `a_stalled_web_font_is_dropped_at_the_subresource_budget` passed only because of the same denial (failed at once, never reached the 500 ms budget). It now serves its page from the font host and asserts the face failed no sooner than 400 ms.

Red before: the font test on 4fa6d6f8 printed `AddressDenied` for all 8 faces, `left: 0 right: 8`.

## Acceptance: `cargo test -p rustkit-engine --features headless --lib`, 3 consecutive runs on the Mac

At 7a908255, 2026-10-23 20:41–22:07 ET, machine load 17–24 (another lane's work on the Mac):

| run | wall | result | failures |
|---|---|---|---|
| 1 | 1704 s | 1031 passed, 2 failed | `vm_interrupt_tests::a_pure_spin_in_a_load_script_is_stopped_at_the_load_budget`, `…a_spin_after_the_load_budget_is_spent_is_still_stopped`: "the load took 3.31 s / 3.44 s" against a `BUDGET_MS + 2000` wall-clock bound |
| 2 | 1853 s | 1022 passed, 11 failed | all 11 (`frame_commit_tests::a_noop_represent_keeps_the_held_commit`, grid_fixed_track ×4, grid_in_flex ×5, grid_auto_repeat_percent ×1) are the GPU test guard: "waited 120s for `grid_block_axis_align_tests::grid_items_and_rows_are_aligned_on_the_block_axis`" |
| 3 | 1641 s | **1033 passed, 0 failed** | none |

The six tests this PR fixes passed in all three runs. The failures in runs 1 and 2 are two load-bound classes outside T5's list: wall-clock budget asserts, and the 120 s GPU-guard wait behind the ~100 s grid_block_axis_align test. **Owed: three runs on a quiet machine (load < 10) for the strict "0 failed ×3".**

Receipt: `scripts/receipt.py` output in trench/devtools/receipts/T5-receipt-7a908255.md (log hashes).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
