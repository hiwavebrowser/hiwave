# T7: network records off the page thread (design note, for Prometheus R1)

Written 2026-10-27 13:10 against develop + #810 (`atlas/dt-t6d` @ b36807e6). No code until R1.

## What is true today (read in code, not assumed)
- A script request's whole life is one `async fn execute` (`script_net.rs:294`). It calls
  `begin_request` (Request record, `doc` stamped from `state.doc`), then
  `policy.execute_waited(...)` inside `timeout_at(deadline)`, then `guard.response(...)` or `guard.fail(...)`.
- That future is polled **only by the page thread**. The live loop boxes it (`start_live`, `script_net.rs:244`),
  and `settle_live` polls it in slices on the view's current-thread runtime and `LocalSet`. `pump` polls it with `join_all`.
  rustkit-http has no thread of its own: even the h2 connection task is `tokio::spawn`ed onto the runtime that polls it.
- So when the page thread is blocked (a long script, `PageCmd::Block`), the request **makes no progress at all**:
  no bytes are read, and no record is written. Moving only the record writes would change nothing.
  The HTTP work has to run somewhere else.

## Proposal
1. **One network runtime per process.** A small multi-thread tokio runtime (2 workers, named `rustkit-net`),
   built lazily in rustkit-engine. A `Handle` reaches `start_live` and `pump` by the same path that
   carries `policy` and `loader` (both are already `Arc`).
2. **The request starts on the page thread and runs on the net runtime.**
   - `start_live` and `pump` call `begin_request` **synchronously**, at request start, on the page thread.
     This keeps the `doc` stamp, the scrub and the shape rule at record time, exactly as today.
   - Next, `handle.spawn` a task that owns the `RequestGuard`, `Arc<FetchPolicy>`, `Arc<ResourceLoader>` and the deadline.
     It runs `timeout_at(deadline, policy.execute_waited(...))` and writes `response`/`fail` **on the net thread**.
     It returns the `NetDelivery` through the `JoinHandle`.
   - The page side keeps a `LiveFuture` that awaits the `JoinHandle` and hands `(id, delivery)` to the page as now.
     Delivery into JS stays on the page thread, in take order; nothing about JS changes.
3. **How a record finds its tab without the page thread.** The guard already holds `Arc<Inspector>` and the request `id`.
   `finish_request` locks only that view's `Inspector` mutex (per view, already shared with the devtools thread)
   and pushes into the `doc` stamped at start.
   The devtools wake already runs from any thread (`records_arrived` in `Locked::drop`).
   No page-thread structure is touched.
4. **Navigation, cancel and view close.** The page side wraps the `JoinHandle` in an abort-on-drop guard.
   Whatever drops the `LiveFuture` today (a navigation clears `in_flight`, the view is destroyed, `pump` returns) aborts the task.
   The task's `RequestGuard` is then dropped unanswered on the net thread and records
   `cancelled`/"abandoned (navigation or view closed)" **in the doc it started in**, as today.
   The deadline and `in-flight cap` reasons are unchanged: `timeout_at` and the `SlotWait` run inside the task,
   so `queued_ms` is still measured where the wait happens.
5. **Locks on the page thread.** Same as today: one `Inspector` lock in `begin_request`, and none per response.
   The response and failure locks move to the net thread.
   No new per-request lock; the `JoinHandle` is lock-free.

## Risks R1 should look at
- **`Send`.** `execute_waited`'s future, `FetchPolicy`, `ResourceLoader` (cookie jar, cache, shield) and `SlotWait`
  must all be `Send + Sync`. Step 0 is a compile probe (`fn assert_send<F: Send>(_: &F)` on the future).
  If anything is `Rc`/`!Send`, I stop and report it here before any rewrite.
- **Ordering.** Records from the net thread interleave with page-thread records by `seq` (the lock order).
  A `response` can now land **before** a page-thread record that was made earlier but pushed later. Delivery order to JS is unchanged.
- **Scope.** Step 1 covers `script_net::execute` only (fetch, XHR, inserted and module scripts), which is the T6 Q3 case.
  Parser scripts, CSS, fonts and images (`lib.rs` 5456/5485/14317/14551/14994) use their own futures.
  They follow the same pattern once step 1 lands; they get a list here, not a silent omission.
- **Cost.** Two idle worker threads per process. The receipt reports the 20-site wall-clock A/B, plus RSS before and after.

## Acceptance (from the plan row)
- A content-thread engine test: a page starts `fetch('/slow')` (the server answers in 200 ms),
  then the page thread is put in `PageCmd::Block(1500)`. A reader thread must see the `response` record
  while the block is still running. Red on develop (no progress while blocked).
- campaign 26/26 unchanged.
- No new per-request lock on the page thread (shown by the code path above, and stated in the PR).
