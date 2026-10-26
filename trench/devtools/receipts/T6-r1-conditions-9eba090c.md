# T6 R1 conditions 1, 2, 3, 6, 7 + tab ring 2048 — `atlas/dt-service` @ 9eba090c

Atlas 10-26 06:20 (b), from Prometheus's T6 R1 CLEAR (exchange 10:04Z, re #853). The commit is stacked on a3652306 (T6b panel groups). No PR (cap).

## Changes, one test each

| # | condition | change | test (red with the change off) |
|---|---|---|---|
| ring | 512 → 2048 | `TAB_RING_CAPACITY = 2048` | (campaign + A/B below) |
| 1 | lost wakeup | Before it sleeps, the service re-reads each watched view's watermark under the inbox mutex (`unread`). While a panel is open it waits at most 1 s (`BACKSTOP`). With no panel open it has no clock. `watermark`/`watched` are SeqCst. | `devtools_service::tests::a_push_between_the_re_read_and_the_wait_still_wakes_the_panel`: a test hook on the service thread pushes an unsignalled record between the re-read and the wait. The second wake arrives within the backstop. |
| 2 | page-thread panic holding the Inspector lock | Reads already recover with `into_inner`. `Inspector::page_crashed()` reads the lock's poison, answers carry `page_crashed`, and the panel prints `page crashed` once. | `content_thread::tests::a_page_thread_panic_holding_the_inspector_lock_does_not_blank_the_panel`: `PageCmd::PanicHoldingInspector` (test-only) runs with the panel open. After it, the console read is answered, the line logged before the panic is still there, and `page_crashed` is true. |
| 3 | tab lifetime | `Watch` holds `Weak<Inspector>`, and dead watches are dropped as the service runs | `devtools_service::tests::closed_tabs_free_their_rings_with_the_panel_still_open`: 20 tabs, each with a panel open and a full 2048 ring, are dropped without closing the panel. 0 stay alive. |
| 6 | `doc` stamped at request start | `open_requests` maps id → doc. Response and failure records take their request's doc (`push_locked_in`). | `inspector_tests::a_network_answer_is_stamped_with_the_document_its_request_started_in`: a response, a failure and a dropped request, all answered after the next navigation, carry the doc their request started in. |
| 7 | second guard | Record-time redaction is unchanged. `answer()` re-applies the URL rule (`scrub_text` on messages, `url_text` on frames) to what it serves. | `devtools_service::tests::the_service_strips_a_query_that_got_past_record_time_redaction`: an event built with `?token=…#frag` is pushed through `emit`, and none of that is served. |

Red before: with all five changes off (unread re-read and backstop off, `page_crashed` false, a strong ref leaked in `watch`, answer doc = current doc, guard skipped), the five tests read **0/5**. With the changes on: 5/5. The 32 existing content-thread and inspector tests pass too (37/37 targeted).

## Memory (condition 3)

20 tabs × 2048 records ("line N" console records): the ring payload is **6034 KiB in total, 301 KiB per full tab ring** (serialized bytes). An `InspectorRecord` struct is 232 B, so the fixed part of a full ring is about 464 KiB per tab before strings. After the 20 tabs close with their panels still marked open: **0 rings alive**. Before the change, the service's `Arc` kept all 20 alive.

## Suite

`test -p rustkit-engine --features headless --lib` @ 9eba090c: **1073 passed / 5 failed**, 1304 s, at load ~10. The five are the Mac localhost set that T5 fixes (referrer ×3, image_loader_routing, remote_web_fonts). T5 is not on this branch. T6b had 1068/5.

## Campaign

parity-capture `--profile parity` @ 9eba090c (sha256 `f4103377dd61…`), ring on: **26/26, mean 1.1078%**, the same as develop, T6a and T6b. The worst three are unchanged: article-typography 4.79%, about 3.70%, form-controls 3.24%.

## 20-site wall-clock A/B (`T6-ab-ring2048-9eba090c.txt`)

One binary. A = `HIWAVE_DEVTOOLS_RING=0`, B = ring on. Each site is captured A, B, A, B.

- **Pixels: no ring mover.** Every across-arm difference is matched by a difference within one arm, which means a served variant: facebook 49.5%, walmart 80.6%, linkedin 41% (known), google 1.68%, shopify 1.29%. 12 sites read 0.00 in every pair.
- **Wall-clock: B/A = 1.028** over the 16 sites with four frames (A 447.7 s, B 460.3 s). T6b at 512 read 0.992.
- **The measurement is not clean.** Load was 8–12: rows 1–10 ran beside the engine suite, and the load was 7.6–10 after it finished, from processes outside the lane. Times run about 2× T6b's (wikipedia 12 s vs 6 s).
  - microsoft and github hit the 30 s limit on **both** arms, twice.
  - cnn and lyft lost single captures.
  - Per-site run-to-run spread in this run is larger than 2.8% (shopify B 18.5 vs 28.2 s), so I can't call 1.028 either a move or not one.
- **Recommendation:** repeat the A/B on a quiet machine before the T6 PR. The ring-off switch (`HIWAVE_DEVTOOLS_RING=0`) is still there if it turns out to move.
