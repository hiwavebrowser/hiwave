T6c of the devtools service plan (`T6-design.md` §4). T6a and T6b landed in #803.

**1. A console read during a same-thread load is answered** (Prometheus, #803 R1, non-blocking). On the `HIWAVE_CONTENT_THREAD=0` path, a load holds the endpoint. The read couldn't borrow it to reach the Inspector, so it fell through to a page command, and the load drops page commands. The panel's console went quiet for the whole load. The view now takes its Inspector and devtools counters once, when it is built; both live as long as the view. `devtools_ask(Console)` and `devtools_inspector()` use that copy and no longer borrow the endpoint. Attach keeps its #803 path: it must reach the page, so a load still defers it to `pending_attach`.
- Red before: `a_console_read_during_a_same_thread_load_is_answered` fails on develop (the receiver closes and no answer comes) and passes at e9ae1c37.

**2. Deadlines and a busy state for live snapshots.** This covers tree, subtree, element, hover, pick and highlight; highlight is now its own kind, no longer `Ack`.
- Only one question of each kind is out at a time. A question asked while one of its kind is out replaces whatever was waiting, and goes out when the first is answered. Before this, a page stuck in a long script came back to a backlog and the panel showed every stale answer, oldest first.
- Each question gets a 2 s deadline. Once it passes, the panel shows `page busy (no answer for N s)` above the tree and greys the tree it already has, which stays visible (`setPageBusy` in `inspector.html`).
- A late answer is discarded (R1 condition 5), and its kind is asked again with the newest question wanted. For hover, that's the pointer's newest position. The busy line clears when nothing late is still out.
- No deadline for console reads (the devtools thread answers them) or for the recording switch (it must reach the page).
- The console input's Eval deadline is unchanged from T6c part 1 (#803): past its deadline it is cancelled on the page and never runs late.
- Tests: `a_busy_page_gets_one_live_question_per_kind_and_late_answers_are_dropped`, `a_question_answered_in_time_asks_what_was_wanted_meanwhile`, `console_reads_and_the_recording_switch_have_no_deadline`. These test new panel state, and develop has none of these functions to fail against. The behaviour they replace is "every question is sent and every answer is shown".

**Deviation from the design (for Atlas).** §4 says the busy line reads `in script N s`, taken "from the last `script` record". A `script` record is written when the script ends, so a hung script doesn't have one yet. Reading the last record would name the previous script. N is therefore how long the oldest late question has waited. That's a lower bound on how long the page has been busy, and it's never wrong. Naming the running script needs a "script began" mark that the window thread can read (an atomic on the Inspector, set in `with_script_js`). That's a small follow-up if wanted; T6d may need it anyway.

**Cost.** Panel-side only; no new page commands and no engine change. With the panel closed, nothing runs.

**Tests.** hiwave-app `--bin hiwave` passed 60 with 0 failures. The campaign is 26/26 with mean 1.1078%, identical to develop: parity-capture doesn't link hiwave-app, so this branch doesn't touch it.

## Receipt (`scripts/receipt.py`)

```json
{
 "base_sha": "origin/develop",
 "binary": "target/parity/parity-capture",
 "binary_mtime_utc": "2026-10-27T11:04:44.387080Z",
 "binary_sha256": "1fb0bac16827642e186887fc5a163852bc51f0006be7610146da87335d7ddec7",
 "branch": "atlas/dt-t6c",
 "campaign": {
  "cases": 26,
  "failed": 0,
  "file": "scratch/camp-t6c-33a04a80.json",
  "mean_diff_pct": 1.1078,
  "passed": 26,
  "sha256": "f52ee261110da4d20d9884f47d9b9e3d782365c9fdb72acd4ae69343c06dd205",
  "timestamp": "2026-10-27T07:05:00.399174"
 },
 "candidate_sha": "33a04a805434ca076f914987379816351789200f",
 "cargo": "cargo 1.91.0 (ea2d97820 2025-10-10)",
 "cargo_lock_sha256": "45b66585b4e1b9edd2288f242beb611d830a021f02fb81a571f534cfbe131294",
 "chrome_version": null,
 "cpu": "arm",
 "dirty_state": false,
 "effective_engine_flags": {},
 "features": null,
 "host": null,
 "note": null,
 "os": "macOS-26.5.2-arm64-arm-64bit",
 "profile": "parity",
 "raw_runs": [],
 "repo": "https://github.com/hiwavebrowser/hiwave-macos.git",
 "rustflags": null,
 "sccache": true,
 "target": "aarch64-apple-darwin",
 "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)",
 "utc": "2026-10-27T11:05:03.714528Z",
 "work_package": "T6c"
}
```

🤖 Generated with [Claude Code](https://claude.com/claude-code)
