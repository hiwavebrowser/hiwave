Dev-tools lane, package T3: **script lifecycle per tab**. Branch `atlas/dt-script-life` @ e1aceaa0, one commit on develop ff6ad36a.

## What the event log says now
- **`script`**: one record per page script, written when its life is over: after it ran (and after its console lines and errors), or when the engine gave up on it.
  - `kind`: `parser`, `defer`, `async`, `module`, `inserted`.
  - `outcome`: `ran`, `threw`, `skipped`, `fetch_failed`, `over_budget` (not started: budget already spent), `stopped` (started, then stopped by the budget's deadline), `engine_failed`.
  - `reason`: in the engine's words (`nomodule`, `too large to run inside the script budget`, `HTTP 404`, `network`, `script budget`, ...). A transport error's own text is not copied (it can name hosts); the request's `failure` has the stage.
  - Stage times:
    - `queued_ms` (inserted only): from the page inserting the script to the engine draining the insertion queue, which starts its request.
    - `fetch_ms`
    - `waited_ms`: from the body arriving to the script starting.
    - `ran_ms`: parse, compile and run, with microtasks; Boa does not separate them.
  - `event`: the `load` or `error` its element heard.
  - `held`: the lifecycle event that waited for it.
- **`lifecycle`**: written as `DOMContentLoaded` and `load` fire. `load`'s `held_by` names the scripts that ended between the two (first 16) and `held_by_count` gives how many there were. On the yielding load (the app) that list is exactly the inserted chain that held `load`.
- `rustkit-bindings`: `InsertedScript` carries `inserted_at`.
- Docs: `docs/INSPECTOR_EVENT_LOG.md`, new "Scripts" section.

## Red before
`script_lifecycle_tests` reads the records as JSON, so it compiles on develop. Run on develop's engine code (test file only, everything else at ff6ad36a), 3 of 4 fail:
- `every_load_path_script_has_one_record_with_its_kind_outcome_and_hold`: `left: []`
- `a_script_the_budget_stops_is_stopped_and_the_next_is_over_budget`: `range end index 2 out of range for slice of length 0`
- `stage_times_say_where_a_script_spent_its_time`: `no script record for inline#1`
- The 4th, `with_nobody_listening_no_script_record_is_built`, is the cost guard and is green on both.

The fixture covers parser, defer, async, module, a 404, `nomodule`, the size cap, a throw, an inserted script (`held=load`, `event=load`, named in `load`'s `held_by`), a script the budget stopped and the next one over budget. A 300 ms route checks `fetch_ms` for a parser and an inserted script.

## Tests
- `script_lifecycle` 4/4
- engine `inspector` 97/97. Two pinned-order tests gain the three new records: the script after its console lines, then `lifecycle DOMContentLoaded`, `lifecycle load`.
- engine `script devtools console` 214/214
- parity-capture 18/18
- Full engine lib suite at e1aceaa0 (1040 s): 1067 passed, 5 failed. All five are the Mac localhost tests that fail on develop and are fixed on `atlas/dt-mac-gates` (T5): `referrer_tests` x3, `image_loader_routing_tests::an_img_is_fetched_…`, `remote_font_tests::remote_web_fonts_are_fetched_concurrently`.

## Cost
- Off (nobody listening, the board): one atomic load per script, plus the clock reads the stage times need: two per external page script, one when page script inserts a script, one when its body arrives. No record is built and no string is formatted.
- On: one record per script.

## Acceptance: cnn (headless live, 25 s, `--event-log`)
`parity-capture --url https://www.cnn.com/ --live-ms 25000 --timeout-ms 120000 --event-log …`. Summary from `trench/devtools/tools/scriptsum.py`:
- 13 parser scripts end by 9.3 s. `inline#13` alone ran 2598 ms. `DOMContentLoaded` fires at 9.75 s.
- **The consent chain is an inserted chain that held window load:** OneTrust's `wbdotp/scripttemplates/otSDKStub.js` (inserted, q=22 f=206 run=13, `held=load`, `event=load`), then `…/202608.1.0/otBannerSdk.js` (inserted, f=203 run=141, `held=load`). Both are in `load`'s `held_by` (10 scripts), with no bisect.
- New fact: five of the ten inserted scripts that held `load` show `queued_ms` 2186 to 3179 ms (two more about 470 ms). The page inserted them while `inline#13` and the other parser scripts ran, and the engine drained the queue only after `DOMContentLoaded`. Their requests all start there, at 9777 ms.
- **Lead for T4, not explained here:** the last script ends at 11.73 s and `load` fires at 18.40 s. In between, the log has nothing for 5.9 s (11.85 to 17.76 s), and no script request was open. Then four OneTrust fetches are recorded at once. So for those 6 s `load` waited on something that is neither a script ending nor a request: a callback, a timer or the turn cadence. This record cannot tell which. T4 or a callback record should.

## Yahoo, same binary (headless live, 25 s)
- 22 parser scripts, then 34 Next.js chunks as `async`: fetch 0.2 to 1.4 s, then `waited_ms` 1.2 to 4.0 s behind the parser scripts. The webpack runtime arrived first (f=209) and ran last, in document order (the engine runs async scripts in document order after the deferred ones).
- `DOMContentLoaded` and `load` both fire at 5.77 s, and nothing held `load`.
- **One inserted script, `s.yimg.com/du/benji/benji-2.3.489.js` (the ad loader): f=196 ms, then `waited_ms` 24519 ms, run on the capture's last turn at 32.2 s.** That is the missing live wake that `atlas/dt-live-wake` (LW, PR body ready, cap) fixes, read off one record with no hand digging.

## Campaign (26 cases, binary built at e1aceaa0, `--profile parity`)
Passed 26/26, mean 1.1078%, the same as develop. Worst: article-typography 4.79%, about 3.70%, form-controls 3.24%.

## Receipt (`scripts/receipt.py`)
```json
{"base_sha": "ff6ad36a", "binary_sha256": "3fc4a1d591701b3ada6fcce5f730bc2370d3a067d486dc790725c913527f57f7",
 "campaign": {"cases": 26, "failed": 0, "passed": 26, "mean_diff_pct": 1.1078,
              "file": "scratch/camp-t3-e1aceaa0.json",
              "sha256": "4978ed82376cd14fc6887b92d203bbc3964cdcfd50dfe5bc8e2a5089e4a919b2"},
 "candidate_sha": "e1aceaa0af8da83050d1fe2f18f5332761d2f2ec",
 "cargo_lock_sha256": "d43bf3f40c046d3d625a2876c81a524fcaac59b37460f330942147537a4c8cb7",
 "dirty_state": false, "profile": "parity", "features": "headless",
 "os": "macOS-26.5.2-arm64-arm-64bit", "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)",
 "utc": "2026-10-24T05:03:00Z", "work_package": "T3-script-lifecycle"}
```

Overlap: #792 (T2) also appends to `InspectorEvent` and to `docs/INSPECTOR_EVENT_LOG.md`, and touches `script_net.rs` initiators. Whichever lands second merges develop: both append, so the conflicts should be adjacent-hunk only.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
