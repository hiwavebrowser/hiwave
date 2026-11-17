# T33 receipt: the quiet board, the headed oracle, and shopify (dev-tools lane, 2026-11-17 12:36–13:00 ET)

Read-only investigation of the live job, plus one tested tool and a patch to the live hook. I did not apply the patch: the hook is live config and goes through /config-receipts.

## Why a headed Chrome took the screen (row question answered)
- `com.alephnull.quiet-board` runs `~/.claude/hooks/quiet-board-daily.sh` (04:30 and 13:00). It builds parity-capture from develop, but it runs **`scripts/realsite_board.py` from the `atlas/trench-realsite` hub** (`~/Repos/.worktrees/trench-realsite`), not from develop.
- That copy was last changed 10-12 (15cbdc23 on origin; the hub's local branch has its own copy). Its oracle is **headed off-screen (A1) by default**: `--oracle-headless` exists only to opt out. It takes no lock.
- Develop's copy is newer (T19 #960, b5b462c8/06ffa528, 11-06). It defaults to headless, makes headed opt-in and idle-gated, and holds `~/.claude/realwindow.lock`. **The quiet board never picked this up.**
- Develop's script is not a drop-in replacement. It has no `--board top25`, does not write trend.csv or trend-top25.csv, and has no `top20` key in summary.json. Switching the hook to it would change the board, so that is Atlas's call.

## Second finding: the hub cannot sync, so the board's results are not reaching origin
- `atlas/trench-realsite` in the hub has diverged from origin, **171 ahead / 150 behind**, with merge base 1aacbd18 (09-26). Every run logs `fatal: Not possible to fast-forward` and `! [rejected] … (non-fast-forward)`. This happened on every run from 11-14 through 11-17 04:47, the last ones I checked.
- origin's newest quiet-board commit is 7618c1a4 (11-05 13:21). **Since then, digest-realsite.md and trend*.csv exist only in the hub's local commits.** The frames still reach renders-private, which is a separate repo.
- The fix needs someone to decide which side wins: merge origin into the hub branch, or push the local commits to a new branch. I did not touch it.

## shopify is loaded live twice a day
- `websuite/realsite-top25.json` and `realsite-top20.json` list shopify on develop and on the realsite branch. ebay is not in top20/25; it is in top80, top100 and holdout20.
- The 11-17 04:30 run (20261117T0931Z) captured shopify: `shopify PASS PASS 84.4% unst`. This breaks the 10-20 "never load live" rule on every run.

## What I built (hub only; no hiwave-macos change, so no PR)
- `trench/devtools/tools/realwindow_lock.py`: `realwindow_lock.py [--wait S] -- CMD…` runs CMD while it holds `~/.claude/realwindow.lock`. It uses the same lock protocol as develop's `RealWindowLock`, which I copied unchanged from 46ea55e3: mkdir plus a pid file, and a dead holder is recovered by rename-then-mkdir. A bare dir (the batch recipe's `mkdir`) is never treated as stale. It exits 75 without running CMD if the lock stays busy for the whole wait. It forwards SIGTERM, SIGINT and SIGHUP to the child and releases the lock on every exit path.
- `trench/devtools/tools/test_realwindow_lock.py`: **8/8 lock tests pass.** They cover: a free lock, the command's exit status passing through, a live holder blocking the run, a bare dir never stale, dead-holder recovery leaving no stale dir, a holder that leaves mid-wait, release never removing a foreign lock, and SIGTERM. Mutant check: with the signal forward removed, the SIGTERM test fails (10.2 s against a 5 s bound).
- **Red first:** `HookTests` fails on the live hook (the board line has no lock). It passes with `T33-quiet-board-hook.patch` applied (9/9, run with `QUIET_BOARD_HOOK=<patched copy>`).

## For Atlas to apply (live config: /config-receipts first)
1. `install -m 755 trench/devtools/tools/realwindow_lock.py ~/.claude/bin/realwindow-lock.py`
2. `patch ~/.claude/hooks/quiet-board-daily.sh trench/devtools/receipts/T33-quiet-board-hook.patch`. The board then holds the real-window lock. It waits up to 1 h for a driver or batch holder, otherwise it logs "board skipped" and exits. A real-window runner that starts during the board waits for it.
3. Check: `python3 trench/devtools/tools/test_realwindow_lock.py` should report 9/9.

## Decisions for Pete (row says "decide with Pete")
- **(a) shopify on the daily board.** Option 1: drop shopify from top20 and top25. This changes the /60 denominator, so re-baseline once. Option 2: run shopify through HAR replay; T18's `--replay-proxy` branch is waiting on the PR cap. Lane recommendation: option 1 now, option 2 once T18 lands, because the board loads it live twice a day.
- **(b) Board identity.** Either keep the headed A1 oracle under the lock (this patch), or move the quiet board to develop's headless-default script. Moving it is a separate re-baseline: different flags, and develop's script writes no trend files.
- **(c) The hub divergence (171/150 since 09-26).** Decide which history wins. Until then, daily results do not reach origin.
