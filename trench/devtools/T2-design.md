# T2 network facts: design note (2026-10-23 13:30, develop @ 6e25ea3a)

## What already exists (do not rebuild)
- `InspectorEvent::Request { id, url, method, resource_type, initiator }`, then exactly one
  `Response { status, mime, encoded_size, decoded_size, from_cache, duration_ms }` or
  `Failure { stage, reason, duration_ms }` (`rustkit-engine/src/inspector.rs`). URLs already go
  through `scrub_url` (no query, fragment or params).
- `FailureStage` already has Timeout, Policy, Cancelled and OverBudget. `RequestGuard` records a
  failure when a request is dropped unanswered, and an over-budget failure when it is dropped past
  a deadline.
- `policy::Denial` maps to stages: Timeout, BudgetExhausted, Shield and Cancelled.

## Gaps against the acceptance
1. **A headless run has no shield.** `ShieldInterceptHandler` lives in `hiwave-app/src/shield_adapter.rs`.
   `parity-capture` calls `Engine::new` with no interceptor, so `diagnose`/headless yahoo can never
   show a shield block. That is the #832 question itself.
2. **A block names no list or rule.** `InterceptAction::Block` becomes `NetError::Blocked` (a unit
   variant, 16 sites) and then `"blocked by the shield"`. The adblock call returns only a bool
   (`AdBlocker::should_block`). Lists are concatenated (`get_all_filter_lists`), and the engine is
   built with `from_rules`, so `BlockerResult.filter` is `None`.
3. **Two verdict sources look the same.** The EasyList worker gives one verdict. Before it is
   ready, or when the 250 ms hop times out, the interim `BLOCKED_DOMAINS` floor gives another.
   The record must say which one. On a cold start yahoo's first subresources hit the floor.
4. **Initiator is coarse:** `parser` / `css` / `script` / `navigation`. The plan wants parser,
   inserted script, fetch, XHR, css, font and image. `RequestDestination` already has
   Fetch/Xhr/Font/Image, and inserted scripts are known from T1 (`InsertedScript.inserted_by`).
5. **A cap overflow is not distinct.** In-flight and queue caps need their own reason, separate
   from `BudgetExhausted`; check where the per-origin in-flight cap queues versus refuses.

## Change (smallest first, each its own commit, one PR `atlas/dt-net-facts`)
A. **Block reason through the net layer.** Add `InterceptAction::BlockedBy(BlockReason)` and
   `NetError::BlockedBy(BlockReason)`, with `BlockReason { source: &'static str /* "easylist" | "easyprivacy" | "domain-floor" */, rule: Option<String> }`.
   Keep the unit `Block`/`Blocked` variants so the 16 sites stay unchanged. `net_error_kind` maps
   `BlockedBy` to `"policy"`. `Failure` gets an appended `blocked_by: { list, rule } | null`
   (default null). Rule text is public filter-list text, not page data, so the shape-only rule
   allows it. Cap it at 256 characters.
B. **Rule and list from adblock.** Build with `Engine::from_rules_debug`. It keeps raw rule
   strings; measure the RSS delta and put it in the receipt. Expect a few MB for about 60k rules,
   paid only when the shield is on. Get the list from a `HashMap<rule, list name>` filled while
   concatenating (`FILTER_LISTS[].name`). `should_block` becomes `check -> Option<BlockReason>`,
   and the worker replies with it.
C. **Shield in parity-capture.** Add `--shield` (default off, so the board stays byte-flat). It
   needs `hiwave-shield` and the adapter moved out of `hiwave-app`, or a thin copy behind a
   feature: decide which in the PR, preferring a move to a small crate `hiwave-shield-intercept`.
   It must wait for the worker to be ready (`--shield-wait-ms`), or the run measures the floor,
   and the record says `domain-floor` either way.
D. **Initiator kinds:** add `inserted_script`, `fetch`, `xhr`, `font` and `image` to the initiator
   string, from destination plus the T1 inserter. Appended values only.
E. **Cap overflow:** a distinct reason `"in-flight cap"` / `"queue cap"` with stage OverBudget.

## Acceptance tests (red before)
A fixture server with three routes:
- `/ads/x.js`, matched by a one-rule test list `||127.0.0.1^$script,domain=…`, or a host the floor lists
- a route that never answers, for the timeout
- N+1 parallel images beyond the cap

Assert `failure.blocked_by == {list, rule}`, `stage == timeout` and the cap reason, each on the
right `id`. Then yahoo headless live with `--shield --live-ms 25000`: list every `blocked_by`
record against the static-asset origin, as origin+path only.

## Cost
Off means no interceptor and no extra allocation. On means one `Option<BlockReason>` per blocked
request plus the debug engine's rule strings.
