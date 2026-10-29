## T8: network records off the page thread, part 2 (slot ticket, two `rustkit-net` workers, T7a carry-overs)

Dev-tools lane package T8 (the #815 hard gate plus the T7b items Atlas listed on 10-28 23:15). The design is `trench/devtools/T7b-design.md`, section G and items 8–11. The `rk-inserted-script` fold (B1a/B1b) is **not** in this PR; it stays for a later package.

### What changed
1. **Slot ticket on the page thread** (`rustkit-net` `policy.rs`). `FetchPolicy::reserve(&req, wait)` runs synchronously and does four things: the total budget, the shape check, the `queued` stamp, and **the request's place in its origin's FIFO slot queue**. It gets that place by polling `acquire_owned` once, with a no-op waker and outside the coop budget (`tokio::task::unconstrained`). `execute_reserved` runs the rest: the origin slot, the page slot, `granted`, the timeout and the cancel race. `execute_governed` is now `reserve` + `run_reserved`, so the page-polled callers behave as before.
   - **Contract:** same-origin slots go in `reserve` order. The page slot is not reserved, so across origins the order is grant order, as before (doc comment).
   - Dropping a `Reservation` gives up its place. The budget count is not refunded, as when a running request is dropped.
2. `start_live` reserves **on the page thread**, before it spawns. A budget or shape refusal is recorded there, through the same `denied()` path the task uses.
3. **Two workers.** `net_runtime()` builds `HIWAVE_NET_WORKERS` workers (1–8, default 2). `1` is T7a's current-thread runtime, kept for the A/B. The D1 doc comment is rewritten. `rustkit-engine`'s tokio dependency gains `rt-multi-thread`: before, only the dev-dependency had it, so tests passed and the parity-capture/app build failed. The parity build caught it.
4. **The network read stops cloning the ring.** `Inspector::network_for_current_doc()` clones only the current document's request/response/failure records. `devtools_network` pairs terminal records with their requests through a map instead of a scan. Both the service path and `Engine::devtools_network` use it.
5. **T7a nits carried:**
   - `brief_relative` prints `…` for a not-quite-scheme (`ht tp://u:pw@h`, `1http://…`, `-http://…`) and for an `@` before the first `/`;
   - control characters become spaces, so a specifier cannot forge a mirror line;
   - `scrub_url` writes `foo:/.//a@b` when cutting `;params` leaves a host-less path that starts with `//` (it used to re-read as user `a`, host `b`).
   - `data:` with no comma, `javascript:` bodies and the authority-`;` pin were already fixed and pinned in #815's later deltas (`brief_url_data_url_with_a_query_in_its_mime_prints_no_query`, `brief_url_javascript_url*`, `brief_url_cuts_semicolon_params_in_the_path_and_keeps_an_authority_semicolon`), so there was nothing left to fix there.

### Tests (red before)
| test | red how |
|---|---|
| 4 console_log nit tests (not-quite-scheme, `@` before `/`, control chars, `foo:/;x/a@b`) | red on develop d16d0f89 (4/4) |
| `policy::same_origin_slots_go_in_reserve_order_not_first_poll_order` (G2, multi-thread runtime, tasks spawned in reverse) | mutation (no first poll in `reserve`): `["/d","/c","/b","/a"]` |
| `policy::a_dropped_reservation_frees_its_place_in_the_origin_queue` (G3) | pin |
| `policy::reserve_refuses_over_budget_and_bad_shape_at_once` (G4), `a_reservation_is_send` | pin |
| `script_net_t7::the_slot_ticket_is_taken_on_the_page_thread_before_any_worker_runs` | mutation (no reserve in `start_live`): no failure record at return |
| `script_net_t7::answers_that_arrive_while_the_page_is_blocked_are_delivered_in_start_order` (T7 test 8) | mutation (reversed take in `settle_live`): `[3,2,1]` |
| `content_thread::a_navigation_mid_flight_closes_the_stream_the_server_sees` (T7 test 2, the server's side, < 1 s) | mutation (`AbortOnDrop` not aborting): the server never sees EOF |
| `devtools_service::the_network_read_clones_only_the_current_documents_requests` | pin: identical answer; full 2048 ring: 2048 records in 0.89 ms before vs 250 in 0.51 ms after (debug) |
| `script_net_t7::the_worker_count_is_one_to_eight_and_two_by_default` | parse pin |

G1 as designed (the T2 combined fixture 50× in a loop) is **not** in this PR. That fixture is ~30 s per run. It runs once in every suite run, now under 2 workers by default, and passed in the suite below.

### Evidence (Mac)
- `cargo test -p rustkit-engine --features headless --lib` @ 9f40d798: **1220 passed / 0 failed** (1073 s). The later commits are covered by targeted runs: `script_net_t7 devtools_service a_navigation_mid_flight the_slot_ticket answers_that_arrive`: 20/0; `console_log:: inspector`: 155/0.
- `cargo test -p rustkit-net --lib`: **104/0**.
- **Campaign 26/26, mean 1.1078%.** Every case is identical to T7a's (522532b9).

RECEIPT_HERE

### Gate receipt: two heavy tabs (cnn + yahoo in one process), parity profile, 8 interleaved rounds (off / w1 / w2 per round)
THREE_ARMS_HERE

- **Load caveat:** every round started at load 10.2–12.6, above the design's re-run threshold of 8. Load was never under 8 in this window, so these numbers are **indicative, not the gate**. A quiet-hour rerun goes to the next session (`trench/devtools/tools/three_arms.py <wt> 8 parity`).
- **Indicative reading:**
  - 2 workers is not slower than 1 thread: the paired medians are −3.5% (cnn) and −5.2% (yahoo), and both spreads straddle 0.
  - 2 workers vs off is within 5% on both pages.
  - Off-thread records are unchanged: cnn lists 111–112 network records in every arm, yahoo 265–269.
- `cargo check -p hiwave-app` @ df6a05af: clean (the `rt-multi-thread` feature fix reaches the app).
- **Not done:** the 20-site A/B with 2 workers vs off.

R1: Prometheus. R2: any non-author. Not for merge by the lane.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
