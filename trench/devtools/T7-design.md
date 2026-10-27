# T7: network records off the page thread (design note, R2 for Prometheus delta R1)


Written 2026-10-27 13:10 against develop + #810 (`atlas/dt-t6d` @ b36807e6). Revised 2026-10-27 ~16:30 ET
against develop f3f281a3 after Prometheus R1 HOLD (#1101): B1-B4 taken, S1-S8 taken, A1 adopted. No code until CLEAR.

## What is true today (read in code, not assumed; lines are develop f3f281a3)
- A script request's whole life is one `async fn execute` (`script_net.rs:294`). It calls
  `begin_request` (Request record, `doc` stamped from `state.doc`), then
  `policy.execute(...)` inside `timeout_at(deadline)`, then `guard.response(...)` or `guard.fail(...)`.
- That future is polled **only by the page thread**. The live loop boxes it (`start_live`, `script_net.rs:244`),
  and `settle_live` polls it in slices on the view's current-thread runtime and `LocalSet`. `pump` polls it with `join_all`.
  The h2 connection is per request (no pool), and its driver is `tokio::spawn`ed onto whichever runtime polls the request.
- So when the page thread is blocked (a long script, `PageCmd::Block`), a live script request **makes no progress at all**:
  no bytes are read, and no record is written. Moving only the record writes would change nothing.
  The HTTP work has to run somewhere else.
- **There is already one off-page network thread, and the first draft was wrong to say there was none.**
  Dynamically inserted external scripts (`drive_inserted_scripts`) fetch on `rk-inserted-script`: a
  current-thread runtime + `LocalSet` (`fetch_sender`, `script_net.rs:1154`), a bounded queue
  (`MAX_INSERTED_FETCH_QUEUE`), a `Semaphore(MAX_INSERTED_FETCHES_IN_FLIGHT)`, `FetchCancel`, `set_diag_nav` at task
  start (`run_fetch_job`, `:1195`) and `poke_live_turn()` on completion. Their bytes do progress while the page is blocked.
  But their `RequestGuard` rides `InsertedJob` (`:1087`) and is answered by `finish_inserted_guard` inside
  `run_inserted` on the page thread (`:1338`), so their **Response record still waits for the page**, and its
  `duration_ms` includes the page wait. That is a T7 defect in its own right (B1a).
- Module scripts do not go through `execute` either: `fetch_module` (`:493`, `begin_request` at `:502`) is its own
  page-polled future, started by `start_live_modules` / `pump_modules` (B1b).
- Step 0 is cleared (Prometheus, #1101): `FetchPolicy`, `ResourceLoader`, `SlotWait` are `Send + Sync`,
  `RequestGuard` is `Send`, and `async move { execute(..) }` is `Send` (probe compiled clean, `Rc<u8>` negative
  control failed E0277, probe reverted). The same probe is re-run in the PR for `fetch_inserted`'s future and
  `fetch_module`'s future before either is moved (A1, step 2).

## Proposal
1. **One network runtime per process, and it is the only off-page network executor (A1 adopted).**
   A small multi-thread tokio runtime (2 workers, named `rustkit-net`), built lazily in rustkit-engine behind a
   `OnceLock<Option<Handle>>`. A `Handle` reaches `start_live` by the same path that carries `policy` and `loader`.
   `rk-inserted-script` migrates onto it (step 2) and its `LocalSet` thread is deleted, so there is one cap, one
   shutdown story and one diag-context rule. Two executors would have meant two of each; that is the justification
   Prometheus asked for, and the answer is not to have two.
2. **The request starts on the page thread and runs on the net runtime.**
   - `start_live` calls `begin_request` **synchronously**, at request start, on the page thread.
     This keeps the `doc` stamp, the scrub and the shape rule at record time, exactly as today.
     Request < terminal is therefore guaranteed per id: begin is synchronous before spawn.
   - Next, `handle.spawn` a task that owns the `RequestGuard`, `Arc<FetchPolicy>`, `Arc<ResourceLoader>`, the deadline
     and a **diag context** (see 6). It runs `timeout_at(deadline, policy.execute(...))` and writes `response`/`fail`
     **on the net thread**. It returns the `NetDelivery` through the `JoinHandle`.
   - The page side keeps a `LiveFuture` that awaits the `JoinHandle` and hands `(id, delivery)` to the page as now.
     Delivery into JS stays on the page thread, in take order; nothing about JS changes (test 8).
   - **Wake on completion (S1).** The task calls `poke_live_turn()` after writing its record, so JS delivery does not
     wait for the next scheduled live turn (`settle_live` slice 2 ms, `LIVE_REQUEST_TIMEOUT` 30 s).
   - **`pump` is unchanged in step 1 (S8).** `pump` is awaited synchronously by the page, so moving its requests gains
     nothing for the Q3 case. It follows later only for uniformity, with its own justification.
3. **How a record finds its tab without the page thread.** The guard already holds `Arc<Inspector>` and the request `id`.
   `finish_request` locks only that view's `Inspector` mutex (per view, already shared with the devtools thread)
   and pushes into the `doc` stamped at start. The `records_arrived` wake (`Locked::drop`, SeqCst watermark, only when
   watched; #803) is thread-agnostic, so a net-thread record wakes the devtools service with no page involvement (S6).
   No page-thread structure is touched.
4. **Navigation, cancel and view close.** The page side wraps the `JoinHandle` in an abort-on-drop guard.
   Whatever drops the `LiveFuture` today (a navigation clears `in_flight`, the view is destroyed) aborts the task.
   The task's `RequestGuard` is then dropped unanswered on the net thread and records
   `cancelled`/"abandoned (navigation or view closed)" **in the doc it started in**, as today.
   - **Abort is cooperative (B3c).** A task that finished first has already written `response 200` while the page drops
     the delivery. So **a Response record is not proof of JS delivery**; parked deliveries cleared on navigation already
     allow this today, and the note says so. What must hold under the race is **exactly one terminal record per id**:
     the task owns the guard, `response`/`fail` consume it, and the unwind/abort drop path records only if it was never
     answered (the guard's `debug_assert`). Test 4 loops the race.
   - **Late cancel records carry the old doc (S3).** `open_requests` keeps the start doc and is not cleared on
     navigation, so a cancel record that lands after the new document commits is stamped with the OLD doc. The panel
     reader (5) filters by doc, so it never shows in the new page's list. Test 2 asserts it.
   - **View close (S5).** Each task holds `Arc<Inspector>` only until its abort is processed. The abort-on-drop guard
     fires in the view's drop; tokio processes an abort at the task's next poll, which for an idle socket wait is the
     next wake of that worker, bounded by the runtime being alive and unblocked. Test 3 asserts the `Weak<Inspector>`
     upgrade fails within a bound after close.
   - **Process exit.** The static runtime is never shut down. In-flight tasks die unrecorded at exit; the ring is gone
     with the process, so nothing reads them. Stated, not fixed.
   - The deadline and `in-flight cap` reasons are unchanged: `timeout_at` and the `SlotWait` run inside the task,
     so `queued_ms` and the `in-flight cap` reason (#792) are still measured where the wait happens (test 5).
5. **The reader (B4).** `devtools.rs` serves element, tree and console answers; it has **no network answer** today.
   T7 adds the service-side one: a `DevtoolsNetwork` answer that lists this view's records for the **current doc**
   (grouped by id, Request then terminal, filtered by `doc`), read through the devtools service under its T6c busy
   state and deadlines. That is the stated reader, and the acceptance test reads through it (not a raw Inspector
   snapshot: lesson of #810 `console_held`). The panel HTML renders it in the same PR if the change is the one list;
   otherwise the rendering is a named follow-up and the PR body says so. The service answer is not optional.
6. **Diag context on the net runtime (B2).** `log_request`/`log_denial` and the `HIWAVE_CONSOLE_LOG` mirror stamp
   `rustkit_js::diag_nav()` from thread-locals (`DIAG_NAV`/`TURN`/`JOB`), and the mirror's test hooks
   (`console_log::force_for_test`, `install_sink`, `console_log.rs:34`) are thread-local too. On a work-stealing
   runtime a task can move between workers between polls, so **set-once at task start is not enough** (it is enough on
   `rk-inserted-script` only because that runtime is current-thread). T7 wraps the spawned future in a
   `DiagContext` future (the `tracing::Instrumented` shape): it captures the nav id, and under `cfg(test)` the mirror's
   force flag and sink, on the page thread at spawn, and installs them around **every poll**, restoring the worker's
   previous values after. Net-side mirror lines then carry the right nav id (test 11), and a test's sink sees them
   (tests 7 and 11) with no global sink, so parallel tests stay isolated.
7. **Failure semantics (B3).**
   - **Task panic (B3a).** The task body runs `policy.execute(...)` under `catch_unwind(AssertUnwindSafe(..))` with the
     guard held **outside** the unwind scope, so the guard is not dropped during unwind and does not record
     "abandoned", which would be false. On `Err(_)` the task records `guard.fail(<engine stage>, "engine failure:
     request task panicked")` (a fixed engine reason, never page text) and returns `NetDelivery::Error(NETWORK_ERROR)`.
     The page side also maps `JoinError::is_panic()` to `NetDelivery::Error` as the belt to that brace. Other requests
     are unaffected (test 10). The stage is `Policy` unless the lane finds a better fit; adding a `FailureStage`
     variant is append-only on the wire but is a schema change and is not done in T7.
   - **Runtime build or spawn fails (B3b).** `OnceLock<Option<Handle>>` holds `None` when the runtime could not be built,
     and `spawn` can fail after a shutdown. Both fall back to **today's page-polled path** (the kill-switch path in 8),
     never `expect()`.
8. **Kill switch and reach (S6).** With the ring off (default) and no panel, `begin_request` returns `None`, the task
   carries no guard and writes no records, but the net runtime still runs **every page's live script requests**, so T7
   changes all browsing, not just devtools. `HIWAVE_NET_RUNTIME=0` selects today's page-polled path, for bisects and the
   20-site A/B; the receipt runs both. Requests started before the panel attached have no guard, as today. Test 9.
9. **Bounds (S2).** In flight is capped by policy (`page_slots` 24 / `origin_slots` 6), but tasks parked on `SlotWait`
   would be unbounded in a process-wide runtime. T7 adds a **per-view cap on spawned tasks** (`MAX_LIVE_NET_TASKS`,
   lane picks the number and states it, the inserted path's queue is the precedent). Past it, `start_live` does not
   spawn: it records `guard.fail(Policy, "too many script requests")` synchronously on the page (the inserted path's
   scrubbed reason) and returns an error delivery. Test 5 covers both caps.
10. **Locks on the page thread.** Same as today: one `Inspector` lock in `begin_request`, and none per response.
    The response and failure locks move to the net thread. No new per-request lock on the page thread; the
    `JoinHandle` is lock-free. Shown by diff in the PR.
11. **Sink I/O under the view lock (S4).** `push_locked_in` calls `sink.record` under the `Inspector` lock, and
    `RollingFileSink` does file I/O there. After T7 net workers do that I/O holding the lock the page thread takes in
    `begin_request`. Today the page thread does the same I/O under the same lock, so the page's own hold is not longer;
    what is new is contention. The receipt **measures** max and p99 lock hold with the file sink on and 24 requests in
    flight. Moving sink I/O out of the lock (record under the lock, write after) is the fix if p99 is over 1 ms, as a
    named follow-up; not in T7 unless the number forces it.
12. **Privacy is unchanged and stays so (S7).** The URL is scrubbed in `begin_request` (`scrub_url`: query, fragment and
    `;` params dropped unless `keep_url_query`). Fail reasons go through `guard.fail`/`scrub_text`; the MIME is the
    fixed name. The net-side paths use **only** `guard.response`/`guard.fail` with fixed reasons, never a formatted
    string. Shield `blocked_by` stays list/rule only, under `--shield`. Test 7 runs a `?token=SECRET` URL and a failure
    reason containing a URL from the net thread and greps every record and mirror line.

## Steps (two PRs, one note)
- **Step 1 (PR T7a): the live path.** Runtime + `DiagContext` + task cap + panic/fallback semantics + kill switch +
  `DevtoolsNetwork` service answer + tests 1-11. `pump`, parser scripts, CSS, fonts and images
  (`lib.rs` 5456/5485/14317/14551/14994) stay on their own futures; listed, not silently omitted.
- **Step 2 (PR T7b): fold `rk-inserted-script` in (A1, B1a).** The Send probe re-run on `fetch_inserted`'s future and
  `fetch_module`'s future first. Then `FetchJob` carries the `RequestGuard`, `run_fetch_job` answers it on the net
  runtime (so the Response record and `duration_ms` no longer wait for the page), the `LocalSet` thread and its queue
  are deleted, and the per-view task cap and the shutdown story from step 1 cover it. `fetch_module` moves in the same
  PR if its probe passes, else it is listed for T7c. Test 12 and the thread-count receipt.
- Two PRs because each R1 surface stays readable (the #810 lesson), and step 1 is the Q3 case on its own.

## Required tests (Prometheus #1101, all taken)
1. Acceptance: `fetch('/slow')` (server answers in 200 ms), `PageCmd::Block(1500)`; read through the devtools service
   while blocked; a queued eval is still pending (proves the block); the record's `doc` equals the start doc.
   Red on develop.
2. Navigate mid-flight: exactly one `cancelled` record, old doc, no response after it, absent from the new doc's
   service list; the server sees the stream closed.
3. View close mid-flight: one terminal record; `Weak<Inspector>` upgrade fails within a bound.
4. Abort-vs-complete race loop: exactly one terminal record per id, no double-answer assert.
5. Over cap: N > `origin_slots` with a deadline gives `in-flight cap` records with `queued_ms`, recorded while the page
   is blocked; over the spawned-task cap gives `too many script requests` with no task spawned.
6. Shield block recorded off-thread (`blocked_by` list/rule, only under `--shield`).
7. Privacy from the net thread: `?token=SECRET` URL and a failure reason containing a URL; no query in any record or
   mirror line.
8. JS delivery order unchanged (completions in reverse order, same callback order as develop).
9. Ring off and no panel: no guard, no records; requests still work. `HIWAVE_NET_RUNTIME=0`: today's path, same results.
10. Injected task panic: error to JS, an engine failure record (not "abandoned"), other requests unaffected.
11. `HIWAVE_CONSOLE_LOG` net lines carry the right nav id, captured through the test sink.
12. (T7b) Inserted-script Response recorded while the page is blocked.

## Receipts
- campaign 26/26 unchanged; 20-site wall-clock A/B with `HIWAVE_NET_RUNTIME` on and off; RSS and thread count before
  and after (T7a: +2 workers; T7b: -1 `rk-inserted-script`); `Inspector` lock hold max/p99 with the file sink on
  (item 11); "no new per-request page-thread lock" shown by diff.

## Prometheus line references (develop f3f281a3)
`execute` :294 and `start_live` :244 as cited; `fetch_module`'s `begin_request` is :502 (cited :508);
`finish_inserted_guard` in `run_inserted` is :1338 (cited :1349). Same code, lines drifted.
