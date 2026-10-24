Dev-tools lane, package T2: **network facts**. A to E done, plus the combined acceptance fixture. Head 22813653 (develop ff6ad36a merged in at e17e54e7). Design note: `trench/devtools/T2-design.md` on `atlas/z`.

## What a request record says now
- **Block reason** (A, a13c5864 + b45337cf). `InterceptAction::BlockedBy(BlockReason { list, rule })`; `NetError::Blocked` and `Denial::Shield` carry `Option<BlockReason>`. `failure.blocked_by: {list, rule} | null` is appended (null by default) on images, parser scripts, inserted scripts, fetch and modules. Rule text is public filter-list text, capped at 256 chars.
- **Which list and rule** (B, 3792a2e1). `AdBlocker::check -> Option<BlockMatch>` comes from `Engine::from_rules_debug` plus a rule→list map (EasyList and EasyPrivacy kept apart). The pending floor answers `list = "domain-floor", rule = <domain>`.
- **Shield in a headless run** (C, 39f1cf9e). The app's adapter moves unchanged out of `hiwave-app` into a small crate, `hiwave-shield-intercept`. `hiwave-app` aliases it as `shield_adapter`, so the app code is untouched. It adds `wait_until_ready`. `parity-capture --shield [--shield-wait-ms 30000]` installs it after waiting for the lists, and prints `shield: on, filter lists ready|not ready (domain floor only)`. **Off by default**: the board path has no interceptor.
- **Initiator kinds** (D, b28497c1). `fetch`, `xhr` and `inserted_script` instead of `script`. Imports and script-added images stay `script`. Fonts were already `css`, and image/font are `resource_type`. Docs: `docs/INSPECTOR_EVENT_LOG.md`.
- **Cap overflow** (E, 22813653, as Atlas decided 10-24: no new failure kind). The caps queue and never refuse: a script request (fetch, XHR, module) waits for one of 6 per origin and 24 per page, and an inserted `<script src>` waits for one of the process's 8. `rustkit-net` gains `policy::SlotWait`, which the policy stamps when a request starts waiting for its slots and again when it has both (`execute_waited`, `fetch_module_waited`; `execute`/`fetch_module` unchanged). The inserted-script thread stamps its permit the same way.
  - `response` and `failure` now carry `queued_ms`: how much of `duration_ms` was spent waiting for a slot. It is `null` for requests no cap queues.
  - A `timeout`/`over_budget` failure whose deadline passed while the request was still queued gets the reason **`in-flight cap`**.
  - That check is made **at the deadline, not when the failure is recorded**. Requests started together share a deadline: when the blockers time out, the freed slot reaches the queued request a moment before its own timeout fires. Judged at recording time, it read `timed out` (shown red below).
  - Built only when the Inspector listens, so nothing is allocated when it is off.

## Red before
- E: `a_shield_block_a_timeout_and_a_cap_overflow_each_record_their_result` (the combined fixture: one shield-listed path, six requests that never answer, and a seventh to the same origin). With the wiring removed (the base's behaviour), `/hang/6` reads `timeout timed out`, the same as the six blockers. With the slot wired but judged at recording time it still reads `timed out`, which is the race above. At head it reads `timeout in-flight cap` with `queued_ms` ≥ 25 000 (the whole 30 s wait), while the six blockers queue for < 1 s. Unit test: `policy::a_request_queued_behind_the_cap_reports_its_wait`.
- A/B: `a_shield_block_records_its_list_and_rule` (four request kinds); `blocked_by` was absent.
- C: `the_shield_filters_requests_only_with_the_flag` (parity-capture). Before, there was no flag and no interceptor.
- D: `script_made_requests_name_the_api_that_made_them`. Before: `["GET fetch /f by=script", "GET script /ins.js by=script", "GET script /parsed.js by=parser", "GET xhr /x by=script"]`. Three older tests that pinned fetch/xhr as `by=script` were updated.

## Tests
At 22813653: rustkit-net `policy::` 50/50; engine `inspector` 100/100 (the fixture and the GPU inspector page tests included), engine `script` 178/178. Load 11-13 from foreign processes.
At b28497c1: rustkit-net 99/99, hiwave-shield 13/13, hiwave-shield-intercept 7/7 (the moved app tests), parity-capture 19/19, engine `inspector console_log error_text script_net script_loading` 120/120 (GPU inspector page tests included). Full engine lib suite: see the comment below once it finishes.

## Cost
- Off (default, and the board): no interceptor, nothing allocated.
- On: one `Option<BlockReason>` per blocked request. The debug engine keeps rule strings. Max RSS of `parity-capture --html-file websuite/micro/bg-pure/index.html` (3 runs each): no shield 86.4 MB; shield with `from_rules` 168.5 MB; shield with `from_rules_debug` 177.4 MB. So **the list/rule naming costs about +9 MB**, paid wherever the shield runs (the app too). The other ~82 MB is EasyList itself, which the app already paid.

## Acceptance: yahoo and the #832 question
`parity-capture --url https://www.yahoo.com/ --live-ms 25000 --timeout-ms 120000 --shield --event-log …`, filter lists ready:
- 141 requests: 120 answered 200, **0 failures, 0 `blocked_by`**, 21 still open at the end. The same run without `--shield`: 140 requests, 119 answered 200, 0 failures, the same 21 open.
- Origins: www.yahoo.com 67, s.yimg.com 71, plus securepubads.g.doubleclick.net, cdn.taboola.com and opus.analytics.yahoo.com, 1 each.
- **Answer: in this run our shield blocks no yahoo static asset**, and nothing on s.yimg.com fails with or without it. The ad hosts are not blocked either: they are among the 21 open requests, so the run ends before their verdict.
- **Correction 10-24 (with `atlas/dt-live-wake` merged in locally, not pushed).** The run above ran under parity-capture's live-wake bug, and inserted scripts never loaded. With LW: 175 requests, all answered, and **11 blocked**. Each one names its list and rule. Four are on s.yimg.com: `/aaq/prebid/prebid-current.js` three times (EasyList, prebid rules) and `/ss/analytics-3.90.0.js` once (EasyPrivacy `||s.yimg.com/ss/analytics-$script,domain=yahoo.com`). The other seven are ad and analytics hosts (doubleclick, taboola, opus.analytics, ay.delivery, clean.gg). **No feed or app chunk is blocked.** Revised answer: the shield blocks yahoo's ad and analytics scripts on s.yimg.com, and nothing else there.
- `queued_ms` on the same run: 44 inserted scripts have it, 14 of them queued > 100 ms, max 1.12 s. The 9 fetches and 1 XHR queued 0 ms. No `in-flight cap` failures. **The caps are not yahoo's multi-second script waits.**
- Wart: with adblock's optimizer, `rule` can be several rules joined with ` <+> ` (prebid above). It is public list text and capped. Naming the single rule needs the optimizer off when the debug engine is built: a follow-up if wanted.
- **The lead this shows instead (pre-LW):** all 21 open requests are `inserted_script`s recorded at t=35.8 s. They include every Next.js page chunk (`/_nca/_next/static/chunks/…`, `app/homepage/page-….js`). The event timeline: `load_finished` at 7.9 s, the last relayout at 8.9 s, then nothing until 35.9 s. `live_stats.turns = 4` over 27 s. The engine records an inserted script's request when a turn drains the insertion queue. These 21 were drained on the last turn, so they never load. Either they were inserted that late, or they had waited since about 8 s; this log cannot tell which, and T3's script lifecycle will. This is T3/T4 material (script lifecycle, live-loop turns), not the network.

## Campaign (26 cases, binary built at 22813653, `--profile parity`)
Passed 26/26, mean 1.11% (1.1078, the same as develop). Worst: article-typography 4.79%, about 3.70%, form-controls 3.24%.

## Receipt (`scripts/receipt.py`)
```json
{"binary_sha256": "05518bed572e5478b075cbb53d21a722fe567cac4d213a75780620e48a735766",
 "campaign": {"cases": 26, "failed": 0, "passed": 26, "mean_diff_pct": 1.1078,
              "file": "scratch/camp-t2e-22813653.json",
              "sha256": "42981f89adee026ef97fa098c22621faea253912aa3b7b8cb64c91013961a182"},
 "candidate_sha": "228136538410fe5f206ca15fe4e3754d6dd0fa65",
 "cargo_lock_sha256": "45b66585b4e1b9edd2288f242beb611d830a021f02fb81a571f534cfbe131294",
 "dirty_state": false, "profile": "parity", "os": "macOS-26.5.2-arm64-arm-64bit",
 "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)", "utc": "2026-10-24T17:17:27Z",
 "work_package": "T2"}
```

## Left out on purpose
- The inserted-script queue-full refusal stays `policy "too many script requests"`. Atlas's (E) decision covered only the in-flight reason. Renaming it to `over_budget "queue cap"` would be its own small change.
- Full engine lib suite at 22813653 (`--features headless --lib`): 1066 passed, 5 failed. The five are the known Mac localhost failures that T5 (`atlas/dt-mac-gates`) fixes: three referrer tests, `image_loader_routing`, `remote_web_fonts`. They fail on develop too.

Overlap: `hiwave-app/src/main.rs` (one line) and `Cargo.toml`. #784/#791 touch `inspector_glue.rs`, not these files.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
