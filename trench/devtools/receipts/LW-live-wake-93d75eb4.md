Branch `atlas/dt-live-wake` @ 93d75eb4 (on develop 64c8d382). No PR yet: 11 PRs are open and the cap is 8. Below is the ready PR body.

## fix(parity-capture): the live loop wakes when an inserted script's fetch arrives

**Bug.** An inserted script's fetch runs on the engine's fetch thread, and `LivePump::in_flight` doesn't count it (`rustkit-engine/src/lib.rs`: "The arrival woke the loop… the fetch is not part of `in_flight`"). The app is woken by `poke_live_turn` through `set_live_wake`. parity-capture installed no waker, so after a page inserted scripts with no timer set, `run_live` slept through the rest of `--live-ms`, and those scripts ran only on the last turn.

**Fix.** `run_live` installs a `LiveWake` (Mutex<bool> + Condvar) through `rustkit_engine::set_live_wake` and sleeps on it. A wake that arrives during a turn ends the next sleep at once. parity-capture only; the board runs no live loop.

**Red before.** `an_inserted_script_runs_when_its_fetch_arrives_not_at_the_end_of_the_window`: "late.js ran 6086 ms after load (the window is 6000 ms)". Green after; parity-capture 19/19.

**Yahoo, headless live, `--live-ms 25000`, same command, no shield:**

| | develop-based b28497c1 | 93d75eb4 (fix) |
|---|---|---|
| live turns | 4 | 16 |
| timer callbacks | 3 | 69 |
| page requests in the live loop | 1 | 42 |
| busy ms | 2701 | 23247 |
| requests: answered / open at end | 119 / 21 | 162 / 0 (2 cancelled) |

Before the fix, all 21 open requests were inserted scripts: every Next.js page chunk, plus gpt.js, prebid, taboola and opus. After it, all of them load, and the feed's third-party calls go out (taboola widgets, pubmatic, pbs).

**Not the feed.** A 1280×4000 frame after `--live-ms 25000` is the same before and after the fix: the "For You" feed is still skeleton cards. This fixes the instrument, not yahoo.

**Consequence.** Before this fix, a headless diagnosis of yahoo's blank below-fold feed measured our tool's sleep, not the browser. The T1 #777 acceptance run (live 25 s) had the same blind spot.

**Campaign** (26 cases, `--profile parity`): 26/26, mean 1.11% (1.1078), unchanged. Campaign sha256 99f95e87c7ee72de82677d202d7f7ecf72fc77fa4c524cd364cd39e62051febf.
**Receipt:** candidate 93d75eb4e4bf61402f9c53d8233bfa5663a764df, binary sha256 a578de736ef17f14f5fcf88bf709490a6a54b56e71e40644a6248e2f52a9f672, dirty_state false, profile parity.

**Cost.** Off: none, since `--live-ms` is opt-in. On: one Condvar wait instead of a sleep.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
