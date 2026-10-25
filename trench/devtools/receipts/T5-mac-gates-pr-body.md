# test: clean Mac gates (six macOS-only engine tests that failed on every Mac run)

Branch `atlas/dt-mac-gates` @ ff9de6a4 (7a908255 + a clean merge of develop @ 2026-10-24 18:37, 23 commits). Test-only: every hunk is inside a `#[cfg(test)]` module, so no engine line changed and the 26-case campaign cannot move (not re-run; the shipped code is byte-identical).

All six tests were red on every Mac run; Linux CI never runs them (`target_os = "macos"` or headless-only).

| test | why it failed | fix |
|---|---|---|
| referrer_tests ×3, image_loader_routing | #445 denies a cross-origin loopback fetch (`localhost:PORT` from a `127.0.0.1:PORT` page) by design; fbc6268f updated the background-image test, these four were never updated | expect the request absent; Referer values stay pinned in rustkit-net `security.rs` (d91d3210) |
| error_page_script_tests::navigating_away_drops_an_inserted_script_still_fetching | the fetch is on its own thread and can still be connecting when `load_url` returns | wait up to 1.5 s for the request, assert it is still unanswered (server answers at 2 s) (4fa6d6f8) |
| remote_font_tests::remote_web_fonts_are_fetched_concurrently | `load_html` leaves the page at about:blank; the private-address vet gives a page with no http(s) origin public-only, so all 8 faces failed `AddressDenied("127.0.0.1 resolves to 127.0.0.1")` (0 of 8 loaded) | set the test page's URL to the font host, so the fetches are same-origin loopback (7a908255) |

Also in 7a908255: `a_stalled_web_font_is_dropped_at_the_subresource_budget` passed only because of the same denial (failed at once, never reached the 500 ms budget). It now serves its page from the font host and asserts the face failed no sooner than 400 ms.

Red before: the font test on 4fa6d6f8 printed `AddressDenied` for all 8 faces, `left: 0 right: 8`.

## Acceptance: `cargo test -p rustkit-engine --features headless --lib`, 3 consecutive runs on the Mac

At ff9de6a4, 2026-10-24 18:39–20:07 ET (one background call, `trench/devtools/tools/suite3.py`):

| run | wall | load (1-min, min/median/max) | result |
|---|---|---|---|
| 1 | 1746 s | 11.5 / 12.2 / 14.4 | **1068 passed, 0 failed** (6 ignored) |
| 2 | 1772 s | 11.2 / 12.2 / 14.8 | **1068 passed, 0 failed** (6 ignored) |
| 3 | 1794 s | 11.3 / 12.4 / 20.5 | **1068 passed, 0 failed** (6 ignored) |

**0 failed in three consecutive runs.** Load stayed 11–13 from processes outside the lane (above the < 10 the plan asked for), yet none of the two load-bound classes seen on 10-23 (vm_interrupt wall-clock asserts at load 17+, the 120 s GPU-guard wait behind `grid_block_axis_align`) showed.

Earlier, at 7a908255 on 10-23 at load 17–24: 2 / 11 / 0 failed, all outside the six (those two classes).

Receipt: `scripts/receipt.py` output in trench/devtools/receipts/T5-receipt-ff9de6a4.md (log hashes).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
