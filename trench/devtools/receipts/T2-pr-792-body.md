Dev-tools lane, package T2: **network facts**. Draft: (E) and the combined acceptance fixture are still to do; see the end. Design note: `trench/devtools/T2-design.md` on `atlas/z`.

## What a request record says now
- **Block reason** (A, a13c5864 + b45337cf). `InterceptAction::BlockedBy(BlockReason { list, rule })`; `NetError::Blocked` and `Denial::Shield` carry `Option<BlockReason>`. `failure.blocked_by: {list, rule} | null` is appended (null by default) on images, parser scripts, inserted scripts, fetch and modules. Rule text is public filter-list text, capped at 256 chars.
- **Which list and rule** (B, 3792a2e1). `AdBlocker::check -> Option<BlockMatch>` comes from `Engine::from_rules_debug` plus a rule→list map (EasyList and EasyPrivacy kept apart). The pending floor answers `list = "domain-floor", rule = <domain>`.
- **Shield in a headless run** (C, 39f1cf9e). The app's adapter moves unchanged out of `hiwave-app` into a small crate, `hiwave-shield-intercept`. `hiwave-app` aliases it as `shield_adapter`, so the app code is untouched. It adds `wait_until_ready`. `parity-capture --shield [--shield-wait-ms 30000]` installs it after waiting for the lists, and prints `shield: on, filter lists ready|not ready (domain floor only)`. **Off by default**: the board path has no interceptor.
- **Initiator kinds** (D, b28497c1). `fetch`, `xhr` and `inserted_script` instead of `script`. Imports and script-added images stay `script`. Fonts were already `css`, and image/font are `resource_type`. Docs: `docs/INSPECTOR_EVENT_LOG.md`.

## Red before
- A/B: `a_shield_block_records_its_list_and_rule` (four request kinds); `blocked_by` was absent.
- C: `the_shield_filters_requests_only_with_the_flag` (parity-capture). Before, there was no flag and no interceptor.
- D: `script_made_requests_name_the_api_that_made_them`. Before: `["GET fetch /f by=script", "GET script /ins.js by=script", "GET script /parsed.js by=parser", "GET xhr /x by=script"]`. Three older tests that pinned fetch/xhr as `by=script` were updated.

## Tests
rustkit-net 99/99, hiwave-shield 13/13, hiwave-shield-intercept 7/7 (the moved app tests), parity-capture 19/19, engine `inspector console_log error_text script_net script_loading` 120/120 (GPU inspector page tests included). Full engine lib suite: see the comment below once it finishes.

## Cost
- Off (default, and the board): no interceptor, nothing allocated.
- On: one `Option<BlockReason>` per blocked request. The debug engine keeps rule strings. Max RSS of `parity-capture --html-file websuite/micro/bg-pure/index.html` (3 runs each): no shield 86.4 MB; shield with `from_rules` 168.5 MB; shield with `from_rules_debug` 177.4 MB. So **the list/rule naming costs about +9 MB**, paid wherever the shield runs (the app too). The other ~82 MB is EasyList itself, which the app already paid.

## Acceptance: yahoo and the #832 question
`parity-capture --url https://www.yahoo.com/ --live-ms 25000 --timeout-ms 120000 --shield --event-log …`, filter lists ready:
- 141 requests: 120 answered 200, **0 failures, 0 `blocked_by`**, 21 still open at the end. The same run without `--shield`: 140 requests, 119 answered 200, 0 failures, the same 21 open.
- Origins: www.yahoo.com 67, s.yimg.com 71, plus securepubads.g.doubleclick.net, cdn.taboola.com and opus.analytics.yahoo.com, 1 each.
- **Answer: in this run our shield blocks no yahoo static asset**, and nothing on s.yimg.com fails with or without it. The ad hosts are not blocked either: they are among the 21 open requests, so the run ends before their verdict.
- **The lead this shows instead:** all 21 open requests are `inserted_script`s recorded at t=35.8 s. They include every Next.js page chunk (`/_nca/_next/static/chunks/…`, `app/homepage/page-….js`). The event timeline: `load_finished` at 7.9 s, the last relayout at 8.9 s, then nothing until 35.9 s. `live_stats.turns = 4` over 27 s. The engine records an inserted script's request when a turn drains the insertion queue. These 21 were drained on the last turn, so they never load. Either they were inserted that late, or they had waited since about 8 s; this log cannot tell which, and T3's script lifecycle will. This is T3/T4 material (script lifecycle, live-loop turns), not the network.

## Campaign (26 cases, binary built at b28497c1, `--profile parity`)
Passed 26/26, mean 1.11% (1.1078, the same as develop). Worst: article-typography 4.79%, about 3.70%, form-controls 3.24%.

## Receipt (`scripts/receipt.py`)
```json
{"binary_sha256": "3dbf3e2aa9bb1a6264514cae9537ecb0603f0d8cca369ba796f61bf51d2e03e7",
 "campaign": {"cases": 26, "failed": 0, "passed": 26, "mean_diff_pct": 1.1078,
              "file": "scratch/camp-t2-b28497c1.json",
              "sha256": "7544be70a94887d90fe9bb2a6adbf31873ab9bad17ddea32c926b09188a6760e"},
 "candidate_sha": "b28497c158c9f3d4f554e5aa2533545c6fe6850e",
 "cargo_lock_sha256": "45b66585b4e1b9edd2288f242beb611d830a021f02fb81a571f534cfbe131294",
 "dirty_state": false, "profile": "parity", "os": "macOS-26.5.2-arm64-arm-64bit",
 "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)", "utc": "2026-10-23T23:20:22Z",
 "work_package": "T2-net-facts"}
```

## Still to do on this PR
- **(E) cap overflow.** The per-origin (6) and per-page (24) in-flight caps *queue* on a semaphore and never refuse. A capped request shows up only as a wait that may end in `timed out`. The refusals that exist are the page request budget (`over_budget "page request budget spent"`), the module limit, and the inserted-script fetch queue (`policy "too many script requests"`, which should be `over_budget "queue cap"`). Proposal: `queued_ms` on `response`/`failure` (time spent waiting for a slot), plus `"in-flight cap"` as the reason when the deadline passes while still queued.
- The combined fixture (shield host + never-answering route + cap overflow) once (E) is in.

Overlap: `hiwave-app/src/main.rs` (one line) and `Cargo.toml`. #784/#791 touch `inspector_glue.rs`, not these files.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
