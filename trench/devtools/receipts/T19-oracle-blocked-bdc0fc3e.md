## T19: real-site board stops scoring against Chrome's own error page (oracle_blocked + A1 headed oracle + A2 n/scorable)

Branch `atlas/dt-t19-oracle-blocked`, base develop 95691f85. Red **38f5bfc4**, fix **bdc0fc3e**. Changes are in `scripts/realsite_board.py`, `tools/parity_oracle/realsite.mjs` and the new `tools/parity_oracle/realsite_launch.mjs`. The engine and parity-capture are untouched.

### What changes (ported from `atlas/trench-realsite`)
- **`oracle_blocked(c)`**: a Chrome capture with `status: ok` is not an oracle when it ended on a `chrome-error://` URL, or when its top-level document came back HTTP ≥ 400. `score_site` marks such a capture `oracle_blocked`, leaves it out of the oracle pick, and uses the other capture if that one is good. Chrome self-noise needs two real oracles. If both captures are blocked, READABLE and LOOKS RIGHT become `oracle_failed`, and the reason given is "chrome capture failed: top-level document HTTP 403". Before this change, a 403 page was scored as the site.
- **Summary**: the summary code is now its own function, `summarize()`. It adds:
  - `oracle_blocked` {id: why}, only when both captures are blocked;
  - `scorable_sites/points/max`, which drop sites blocked by the access probe or by the oracle (A2: reported *beside* /60, never instead of it);
  - `oracle_headless`;
  - `full_run`.

  Two new output lines: `ORACLE BLOCKED …` and `SCORABLE n/m on k sites   oracle: headed|headless`. **/60 itself is computed as before.**
- **A1, headed oracle**: the board's `chrome` mode launches pinned CfT 148 headed, at `--window-position=-2400,0` and `--window-size=W,H`, with every deterministic flag kept. It does not change webdriver, spoof anything or solve challenges. `--oracle-headless` (which sets `REALSITE_ORACLE_HEADLESS=1`) restores the old identity for before/after readings. The launch options live in `realsite_launch.mjs`, so they can be tested without a browser.
- **`http_status`**: the main frame's navigation response status is recorded on the capture, even when `goto` throws.

### Tests (`scripts/tests/test_realsite_oracle_blocked.py`, no browser, no network)
- **Red at 38f5bfc4, against develop's scorer**: 8 of 9 failed. The good-oracle control passed, as expected.
- **Green at bdc0fc3e**: 9/9.
- **Red by mutation**: with `oracle_blocked` made a no-op in memory, 4 of the 5 oracle tests fail. The control passes.
- **Full `scripts/tests` discover**: 239 run, 0 failed, 3 skipped.

### Witness (loopback only, no live site)
A local server answered `/denied` with 403 and `/ok` with 200. Both URLs went through the real `realsite.mjs chrome` on pinned 148.0.7778.216:
```
headless: denied http_status 403 -> oracle_blocked: top-level document HTTP 403 | ok http_status 200 -> None
headed:   denied http_status 403 -> oracle_blocked: top-level document HTTP 403 | ok http_status 200 -> None   (oracle_headless false, PNG 1280x800, page rendered)
```
The headed run was at 12:44 ET with `z-window.lock` and `board-quiet.lock` both free. The window was off-screen.

### Campaign
**26/26, mean 1.073%**, on this session's parity build (`target/parity/parity-capture`, 12:43 ET). The release path was symlinked to it, and a no-op cargo shim was first on PATH. The campaign cannot move, because parity-capture and the engine are untouched. This matches the T18 figure on 5e87a184.

### Honest reading of the Trace #978 claim
This port does **not** by itself add a point to /60. A blocked oracle now scores 0 on READABLE and LOOKS RIGHT, with a reason. Before, it scored whatever matching a 403 page gave. Two things can give the point back, and neither is proved here:
- the headed oracle (A1) getting the real page where headless was challenged, which needs a live board run;
- reading `SCORABLE`.

### Not ported (follow-ups, scoring or board changes for Atlas)
1. trench-realsite's rule "probe-blocked site scores LOADS=0 even if RustKit painted (the challenge page)". This changes what scores, not what is reported.
2. `--board top25/wide/categories`, `--summarize`, `--viewport`, `trend.csv` (A6), and the engine stderr log. Develop's board has `--sites-file/--holdout/--v2` instead.
3. Develop's `actions`, `record-har` and `timestable` oracle modes stay headless. Only the board's `chrome` mode is headed.

### Receipt (`scripts/receipt.py`)
```json
{"base_sha": "95691f85", "binary": "target/parity/parity-capture", "binary_sha256": "5bf17cfcac5dfe067ba701f5477e7e426f55f2e95329d35e8590b47dd673c38b",
 "branch": "atlas/dt-t19-oracle-blocked", "candidate_sha": "bdc0fc3e6dbb5a1ee2cc4ae3600e6bc59f470442",
 "campaign": {"cases": 26, "failed": 0, "passed": 26, "mean_diff_pct": 1.073, "timestamp": "2026-11-06T12:44:19.637372",
              "sha256": "724d915439b4b3698962c6ef7263f137b744af01e973750a570b042880b5702d"},
 "dirty_state": false, "profile": "parity", "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)", "utc": "2026-11-06T17:44:26.921299Z",
 "work_package": "scripts"}
```

🤖 Generated with [Claude Code](https://claude.com/claude-code)
