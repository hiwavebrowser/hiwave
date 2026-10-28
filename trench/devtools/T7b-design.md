# T7b: slot order by construction, two workers, the inserted-script fold (design note, for Prometheus/Atlas R1)

Written 2026-10-28 12:40-13:30 ET against `atlas/dt-t7a` @ 295816ff (#815, both R1 CLEAR, R2 stamp pending,
not landed). Per Atlas 10-28 10:05: #815 is open, so this session is the design only; no T7b code until #815 lands
and this note has R1. Line numbers are 295816ff.

## Scope (Atlas 10:05 list + the T7 note's step 2)
- **G (hard gate, PR body of #815):** slot ticket in `begin()` on the page thread, then 2 workers; two-tab rerun.
- **T7b proper:** fold `rk-inserted-script` into the net runtime (B1a, test 12); `fetch_module` too if its Send probe
  passes (B1b); test 8 (JS delivery order); the network read stops cloning the ring; test 2 asserts the server sees the
  stream close; Atlas's 15:54 `scrub_url` shape guard (`foo:/;x/a@b`).
- **Two PRs, G then T7b.** G is the D1 ruling's gate and changes the policy crate; its receipt is a timing receipt.
  T7b is a privacy/records surface. Same #810 lesson as T7a/T7b: each R1 stays readable. T7b does not start until G
  passes its gate.

## What is true at 295816ff (read in code)
- The policy's slots are tokio FIFO semaphores taken **inside the task**: `execute_governed` (`rustkit-net
  policy.rs:549`) bumps `total`, runs `validate_shape`, stamps `SlotWait::queued`, then awaits the origin semaphore
  (`:575`), then the page semaphore (`:577`). A request's place in the origin queue is fixed by its **first poll**.
  On one current-thread `rustkit-net` (`script_net.rs:275`, D1) first polls happen in spawn order; with 2 workers they
  race (T2 combined fixture: `/hang/4` capped instead of `/hang/6`).
- Three callers reach those semaphores: `finish` (`script_net.rs:582`, XHR/fetch), `fetch_module` (`:779`, dynamic
  `import()`), and the load path's module fetch (`lib.rs:5473`). All go through `execute_waited`.
- Inserted scripts do **not** use the policy semaphores: `fetch_sender` (`:1425`) is a process-wide mpsc queue (512)
  drained by **one dispatcher loop** that takes a `Semaphore(8)` permit per job in queue order, then `spawn_local`s
  `run_fetch_job` on the `rk-inserted-script` current-thread `LocalSet`. `set_diag_nav` is set once per job (`:1469`),
  which is only right on a current-thread runtime. The `RequestGuard` stays on the board's `InsertedJob` and is answered
  by `finish_inserted_guard` (`:1752`) when the page runs the script, so Response and `duration_ms` wait for the page.
- The network read (`devtools_service.rs:306`, `Engine::devtools_network` `devtools.rs:581`) calls
  `snapshot_and_doc(0)`: it **clones every record in the ring** (console included, up to 2048) under the Inspector
  lock, then filters by doc and matches terminals with `iter_mut().find` (O(n^2) in requests).

## G: slot ticket, then two workers
1. **`FetchPolicy::reserve(&self, req: &ScriptRequest, wait: Option<&SlotWait>) -> Result<Reservation, Denial>`**,
   synchronous, called by `begin()` on the page thread. It does, in today's order, everything whose outcome depends on
   order: the `total` budget bump, `validate_shape`, `SlotWait::queued`, and **registers in the origin semaphore's
   queue**: it builds `origin_sem.acquire_owned()` (an owned, `Send`, `'static` future), boxes it, and polls it once
   with a no-op waker. tokio's batch semaphore is FIFO by registration, and the async fn's first poll registers the
   waiter (or takes a free permit at once). The boxed future goes into the `Reservation`, which the task owns.
   - **No lost wake:** if a permit is assigned to the node before the task runs, the task's first poll (every spawned
     task is polled at least once) re-polls the same future, which replaces the no-op waker and sees the permit.
   - **Drop:** dropping the `Reservation` (abort, navigation, view close, over the task cap) drops the `Acquire`, which
     unlinks the waiter or returns the permit; the budget count is not refunded, as today when a governed request is
     dropped after `fetch_add`.
   - **The page slot is not reserved.** It is taken after the origin slot, in the task, as now: holding a page slot
     while queued on an origin would let one busy origin starve the page (the comment at `:561`). So the order
     **contract is per origin, by `begin()` order**. Across origins the page-slot order is grant order, as it is today
     between origins whose grants land on the same turn; nothing in the fixtures or the fetch spec orders that. Stated
     in the doc comment.
   - `execute_reserved(loader, Reservation, wait)` runs the rest (origin await, page slot, `granted`, timeout, `run`).
     `execute_waited` becomes `reserve` + `execute_reserved` for the callers that still start in the task, so
     `lib.rs:5473` and the page-polled fallback behave exactly as today.
   - A `Denial` from `reserve` (budget, shape) is recorded by `begin()` on the page synchronously, with the same stage
     and reason the task records today, so the record does not change. Test G1 pins it.
   - **Fallback if R1 rejects the no-op-waker poll:** a per-origin turnstile (ticket number taken in `begin()`, the task
     waits for `next == ticket` before its first `acquire`, a drop guard advances it). More code and a skip-on-drop
     case; I would rather not, but it needs no reliance on tokio's registration-on-first-poll.
2. **`fetch_module` (`:765`) reserves in its start too** (it runs on the page today, so this is only the shared API),
   so when T7b moves it the ticket is already right.
3. **Two workers.** `net_runtime()` builds `new_multi_thread().worker_threads(n)` with `n` from
   `HIWAVE_NET_WORKERS` (default 2; `1` = today's current-thread runtime, for the A/B). `DiagContext` is already
   per-poll, which is what a work-stealing runtime needs. The doc comment on D1 is rewritten.
4. **Tests (G).** G1: the T2 combined fixture under 2 workers, **50 runs in one test binary invocation** (loop), 0
   mis-capped; red with `reserve` reverted to first-poll registration (by mutation, stated; a race is not reliably red
   in one run, so the receipt quotes the mis-cap count over 50 runs before and after). G2: N > `origin_slots`
   same-origin requests started in order A..N with the page then blocked: `SlotWait::granted` order equals start order.
   G3: a reservation dropped while queued (navigation) frees its place; the next request gets the slot (no stuck queue).
   G4: a budget/shape refusal is recorded on the page with today's stage and reason.
5. **Gate receipt (#815 body):** parity or release build, cnn + yahoo in one process, **>= 8 interleaved rounds per
   arm** (ABCABC..., not AAA..BBB..), arms `HIWAVE_NET_RUNTIME=0` / `HIWAVE_NET_WORKERS=1` / `=2`, paired diffs per
   round, median and spread. Pass: 2 workers is not slower than 1 thread beyond the paired spread, and 2 workers vs
   off is under 5% on both pages. Load is quoted; a round under load > 8 is re-run, not dropped silently. Plus the
   20-site A/B with 2 workers vs off once (pixels + wall clock), the full suite, campaign 26/26. If 2 workers does not
   pass, G lands the ticket alone with 1 thread and T7b proceeds on 1 thread; that is a ruling for Atlas, not mine.

## T7b proper
5. **Send probe first** (as in T7a step 0): `async move { run_fetch_job(job).await }` and `fetch_module`'s future,
   compiled against `tokio::spawn` with an `Rc` negative control; reverted. If `fetch_module` fails, it is listed for
   T7c and the PR says so.
6. **Fold `rk-inserted-script` in (B1a).**
   - The dispatcher loop moves unchanged onto the net runtime as **one spawned task** (it is the one place that orders
     inserted fetches, so permits still go in queue order with 2 workers); its jobs are `spawn`ed, not `spawn_local`ed,
     each wrapped in `DiagContext` with the job's `nav_id` (the set-once at `:1469` goes).
   - `FetchJob` carries the `RequestGuard` (`dropped_as(Cancelled, "abandoned (navigation or view closed)")`), and
     `run_fetch_job` answers it **on the net thread** right after `fetch_inserted`, with the body of
     `finish_inserted_guard`. `InsertedJob.guard` is deleted, so one owner, one terminal record. The queue-full path in
     `spawn_inserted_fetch` gets the job back from `try_send` and answers its guard on the page, as today.
   - Navigation: a job still queued is skipped by the dispatcher (`continue`) and dropped, so its guard records
     `cancelled` in its start doc; a job in flight sees `cancel` and returns, same. Neither double-records:
     `cancel_inserted_jobs` no longer holds a guard. Test 12b.
   - The `Semaphore(8)` and the 512 queue stay as they are (process-wide; per-view bounds stay M6's). The thread, its
     `LocalSet` and the `expect()`s go; if the net runtime is `None` (switched off or not built), inserted fetches run
     on today's `rk-inserted-script` path, kept behind the same switch for the A/B. Deleting that path is a follow-up
     once the switch has had a release.
   - `duration_ms` for an inserted script now ends at arrival, not at the page's run. The T3 `script` record keeps its
     own fetched/ran times, so the "waited for the page" figure is still visible there.
7. **`fetch_module` (B1b), if the probe passes:** `start_live_modules` spawns like `start_live` (begin + reserve on the
   page, task on the net runtime, oneshot + poke, `AbortOnDrop`, same `MAX_LIVE_NET_TASKS` count). `pump_modules` and
   `lib.rs:5473` stay page-polled (awaited synchronously, nothing gained), as `pump` did in T7a.
8. **Test 8 (JS delivery order).** Three fetches answered in reverse (300/100/0 ms), page blocked 500 ms, then one
   turn: callback order equals the page-polled path's (`force_page_polled_for_test`), under 1 and 2 workers. It is a pin,
   so it is shown red by mutation (reverse `settle_live`'s take order), stated as such.
9. **The network read stops cloning the ring.** `Inspector::network_for_current_doc()` walks the ring under the lock and
   clones only `Request`/`Response`/`Failure` records whose `doc` is the current doc; `devtools_network` pairs them with
   a `HashMap<u64, usize>`. `snapshot_and_doc` stays for any other caller (or goes, if none). Receipt: lock hold of one
   network read on a full ring (2048: ~1900 console + 150 network) before and after, and a pin that the answer is
   identical on the T7a test pages.
10. **Test 2: the server sees the stream close.** The test server records when the `/hang` connection's read returns
    EOF or errors; the test asserts it within 1 s after the navigation (the T7a C4 bound). Red if `AbortOnDrop` is
    removed.
11. **`scrub_url` shape guard (Atlas 15:54).** When the cleaned URL has no host and its path starts with `//`, prefix
    `/.`, so `foo:/;x/a@b` stays a path (`foo:/.//a@b`) and does not re-read as userinfo + host. One test row, red first.
    It is in inspector.rs, shared with every record, so it rides T7b rather than a T7a delta.

## Tests and receipts (T7b)
- 12 (T7 note): an inserted script's Response is recorded while the page is blocked (`PageCmd::Block`), with
  `duration_ms` < block length; red on #815's head. 12b: navigation with one inserted job queued and one in flight gives
  exactly one `cancelled` each, in the old doc. 8, 9's network-read pin, 10 and 11 as above.
- Receipts: campaign 26/26 at the candidate; 20-site A/B with `HIWAVE_NET_RUNTIME` on vs off; threads (-1
  `rk-inserted-script`); the network-read lock hold before/after; full suite.

## Open questions for R1
- Q1: is the no-op-waker first poll in `reserve` acceptable, or the turnstile?
- Q2: per-origin FIFO as the stated contract, cross-origin page-slot order unspecified: agreed?
- Q3: keep the `rk-inserted-script` path behind the switch for one release, or delete it in T7b?
