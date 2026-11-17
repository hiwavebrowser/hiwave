# T34: one oracle for the chrome board (CfT 148). Receipt and ready PR body

Branch `atlas/dt-t34-one-oracle` @ **1c77e461** (red 4c606193, fix c2d6af92, board 1c77e461), base develop 6d3cbda7.
**No PR yet: PR cap** (33 open at 18:55 11-17, cap 8). When under the cap:
`gh pr create --draft --base develop --head atlas/dt-t34-one-oracle --title "tooling: chrome board scores against the pinned CfT 148 (T34)"`
and use the body below.

---

## What

The chrome board's Chromium arm launched whatever Chromium the installed Playwright bundles. That is **143.0.7499.4** with playwright 1.57 (`chromium-1200`). The batch method never sets `PARITY_CHROME_PATH`, so the batch board gate scored against 143, while pins, probes, the real-site board and `docs/GATES.md`'s other rows use Chrome for Testing **148.0.7778.216**. This PR gives the board one oracle:

- `scripts/chrome_board.py --oracle pinned` (the default) uses `PARITY_CHROME_PATH`, or else the default pin path (the same path as `realsite_board.py`). If the pin is missing, the run is **refused before any capture**, with exit 2 and a message naming 148 and `--oracle bundled`.
- `--oracle bundled` is opt-in for local iteration. It removes `PARITY_CHROME_PATH` for the Chromium arm, and `BOARD.md` says in bold that the run is NOT the pinned oracle and does not gate.
- `board.json` `run` gains `oracle`, `oracle_pin` and `oracle_mismatch`. If a pinned run's Chromium reports any other version, the board is still written, is flagged, and the run **exits 3**.
- The pin goes only to the Chromium arm (`chromium_env`). The pixel and geometry diff steps keep the plain node environment.
- `docs/GATES.md`: the chrome board row names CfT 148.0.7778.216 and says it was 143 until T34.
- `trench/chrome/BOARD.md` and `board.json` are re-baselined once on 148 (see below).

## Red before

Seven new tests are in `scripts/tests/test_chrome_board.py` (`OracleTests`). At 4c606193 (tests only) **7 of 7 were red** (6 errors, 1 failure) and the 20 existing tests passed. At c2d6af92 the file runs **27/27**. The existing fake-capture tests now point `PARITY_CHROME_PATH` at `sys.executable`, so they do not depend on the pin existing on the host.

## Re-baseline (same binary, both oracles)

One parity build of c2d6af92 (sha256 6f417c41…) ran the full 42-row board twice: `--oracle bundled` (143) and the default (148). Each run took about 2 min at load about 7.

| | Chromium | green | rows identical (pixel %, geometry diffs, join failures) |
|---|---|---:|---:|
| bundled | 143.0.7499.4 | 39/42 | — |
| pinned | 148.0.7778.216 | 39/42 | **42 of 42** |

- **Chromium frames:** all 42 `chrome.png` decode equal within 8/channel. The PNG bytes differ in 37 of them, from encoding and sub-threshold values.
- **Chromium rects:** 12 of 42 `layout-rects.json` differ. The `settings` selects and button move by 1/64 px (`#browserSelect` width 281.734 → 281.719). `#modeSelector` scroll width is 24 → 54; that is its scroll box, not its rect. No geometry diff count moves.
- **So the switch moves no board row today.** It removes a hidden variable before a Chromium update does move one.
- **Committed board:** the 11-05 board (5/42 on develop 209f6a64, 143) becomes the 148 board (39/42 at c2d6af92 on develop 6d3cbda7). That jump is develop's progress since 11-05, not the oracle; the same-binary A/B above is the oracle's share (0 rows).

## Gates

- `python3 scripts/tests/test_chrome_board.py`: 27/27.
- Campaign: **26/26, mean 0.405 %**, on this branch's parity build. The no-op cargo shim was first on PATH and `target/release/parity-capture` was symlinked to the parity build, because the seed's release binary had been moved aside. No engine or render code changed.
- Receipt (`scripts/receipt.py`, at c2d6af92; 1c77e461 adds only `trench/chrome/` data):

```json
{"base_sha": "6d3cbda7", "binary": "target/parity/parity-capture",
 "binary_sha256": "6f417c418b9c3a89afcd2fdc2b0b03daf8cae67fa0205ccb5c605ec57d016d66",
 "branch": "atlas/dt-t34-one-oracle", "candidate_sha": "c2d6af927be66deb13c732ed4b0157b364aa7428",
 "campaign": {"cases": 26, "failed": 0, "passed": 26, "mean_diff_pct": 0.4051,
              "sha256": "e322a932f3c49f272c81934d91a8ddf8669bf4db370a3c2a6a4f41d142e399dc",
              "timestamp": "2026-11-17T18:49:36.868905"},
 "dirty_state": false, "profile": "parity", "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)",
 "utc": "2026-11-17T23:49:37.147284Z", "work_package": "T34",
 "note": "tooling only (scripts/chrome_board.py, docs/GATES.md); no engine change"}
```

## Disclosures

1. **Linux and Windows board hosts now refuse unless `PARITY_CHROME_PATH` is set.** The default pin path is macOS-only, as in `realsite_board.py`. That is intended (one oracle, no silent fallback). Any host that runs the board needs the variable set, or `--oracle bundled` for a local look.
2. **Batch method:** on this Mac the batch `run.sh` needs no change, because the default pin path exists. But a `cbcmp` of a pre-T34 batch board against a post-T34 one compares 143 with 148. Today that moves 0 rows (above). If one ever moves, re-run the older arm.
3. **Quiet board:** no change needed for the oracle. The hook's `realsite_board.py` (the trench-realsite hub copy) already defaults to CfT 148 and sets `PARITY_CHROME_PATH`. Its other problems are T33's.
4. **Not touched (outside this repo/lane):** `agent-briefs/common.md` line 5 still says "Oracle is Chromium (Chrome 143.0.7499.4 / …)", while line 38 names the 148 pin. Atlas should change line 5 to CfT 148.
5. Other callers of `deterministic.mjs` and the census tools are unchanged: they still fall back to bundled Chromium when `PARITY_CHROME_PATH` is unset. `capture_all_baselines.mjs` already refuses to run unpinned. Only the board gate was in scope.
