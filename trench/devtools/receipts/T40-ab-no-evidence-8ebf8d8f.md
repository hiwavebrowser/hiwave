# T40: the batch A/B says NO EVIDENCE for cnn, and why cnn times out

Branch `atlas/dt-t40-ab-no-evidence` @ `8ebf8d8f` (red `d97597d4`, base develop `29bd706e`). Tooling only: `tools/site_ab/` + one `.gitignore` line. No Rust change.

## Cause: engine cost, not the site, not a hang

cnn timed out at 30 s on all 8 loads of batches 51 and 52, both arms, and on every batch A/B since at least batch 45. At develop `29bd706e` (parity profile, load 2.5–6.5):

| limit | result | per capture |
|---|---|---|
| 30 s | 4/4 timeout (`status: timeout`, exit 3, nothing on stderr without `RUST_LOG`) | 30.1–30.2 s |
| 90 s | 4/4 frames, within A 0.00 %, within B 0.00 %, across 0.00 % ×4 | 69.3–83.4 s |

So the page itself is stable and the capture finishes; 30 s is just too short for what the engine spends on it. Where the time goes (one 90 s run, `--verbose`):

- `script_stats.elapsed_ms` 49 177 of 69 447. **One script holds 48 454 ms of it:** cnn's 3.27 MB inline module bundle (`inline#10`, a webpack-style `self.modules.push(...)` registry plus `mountComponentModules()`). The other 16 scripts total 723 ms.
- Its time is not parse: the same script alone in an `--html-file` page (no network) parses, starts and throws early in 0.5 s.
- It is **forced layouts**: `Forced layouts in the script task forced_layouts=225 ms=45185.0 cause=attribute:inner_text`, with 174 of the 225 caused by `innerText` reads after an attribute write. Each one rebuilds the whole tree (`build_ms` 23.8 s + `layout_ms` 26.7 s in the load's wgate hold line of 62.7 s). Then 3 later tasks add 21 + 12 + 12 more at about 200 ms each.
- 225 is under the per-task count cap of 256 (#812, `FORCED_LAYOUTS_PER_TASK`), so nothing stops it. That cap is a count on purpose: a time leg made cnn's frame depend on machine load (#812 A/B).

**For the Z lane (proposed row, not filed: this lane edits only trench/devtools):** "cnn's module bundle forces 225 full-tree layouts in one script task (174 from `innerText` after an attribute write), about 200 ms each = 45 s; Chromium does the same reads incrementally. Reduce: one element, N × (set attribute; read innerText), time per read against N." It is a perf row, not a hang.

## Tool change

The batch ran `$P/batch<N>/ab.py`, a scratch copy (batch71 lineage), which printed `n/a` in every diff column and `failed: 4`. That row read like a quiet one. `tools/site_ab/ab.py` is that script moved into the repo with the same arguments and outputs (frames, layouts, stdout JSON, stderr under `x-<tag>/`, so `abinputs.py` still works). The output dir and the limit are now flags (`--out`, `--timeout-ms`, default 30000). On top of that:

- A site with **no cross pair that has both frames** reads `NO EVIDENCE (0 of 4 cross pairs: …)` in place of the diff columns. This covers both arms failing, and also one arm failing entirely, which also certifies nothing.
- Some pairs missing reads `PARTIAL k of 4 cross pairs (…)`. A missing diff prints `—`, never `n/a`.
- The note gives each arm's reasons with counts, taken from the capture's own JSON status (`timeout`, `error`, `no frame` when it said ok, `crash` when it printed no JSON), and the limit.
- It also gives **where the capture was when it stopped**: the last script the engine started and how many forced layouts it had run, from the `RUST_LOG=rustkit_engine=info` log the batch already collects. Runs stalled in one place collapse to a count range. URLs are shown as `host/…/file` with no query.
- The run ends with `no evidence (k of n sites): …`, so a reader of the tail sees it.
- Full rows are unchanged, character for character (a test pins the old prefix). Only rows with a missing frame change, plus the new footer line.

Live, develop on both arms, at 30 s:

```
wikipedia    within A 0.00%  within B 0.00%  across 0.00% 0.00% 0.00% 0.00%  failed: 0  secs A,B,A,B 13.3,9.5,10.6,7.8  …
cnn          NO EVIDENCE (0 of 4 cross pairs: A timeout 2/2, B timeout 2/2, limit 30 s; stalled in inline#10 after 92–104 forced layouts)  failed: 4  secs A,B,A,B 30.2,30.1,30.2,30.1  …
no evidence (1 of 1 sites): cnn (A timeout 2/2, B timeout 2/2, limit 30 s; stalled in inline#10 after 92–104 forced layouts)
```

(the wikipedia line is from the first live run, before the range commit; the cnn and footer lines are at `8ebf8d8f`.)

## Tests

- `python3 -m pytest -q tools/site_ab/tests/test_ab.py`: **10/10**. Fake parity-capture binaries (frame / hard-timeout JSON with cnn-like stderr / external-URL stall with a query / crash / cnn-only timeout / fail once). No network, no engine.
- Red first: the red commit's `ab.py` fails **9 of 10** of the final tests. The one pass is the full-row guard. The range test is red on `9486b96b`.
- Six mutants of the fix each turn tests red: no NO EVIDENCE branch (5), query kept (1), no forced count (1), no footer (2), PARTIAL unmarked (1), `n/a` for a missing pair (1).
- One test fixture changed after the red commit: the footer test's fake timed out on every site, so it could not tell 1 of 2 from 2 of 2. Its replacement times out on cnn only. Stated in the fix commit.

## Gates

- Campaign **26/26, mean 0.4052 %** (= T38/T39). It ran on parity-capture built at base `29bd706e` with `--profile parity`; the candidate changes no Rust. The no-op cargo shim was on PATH and `target/release/parity-capture` was symlinked to the parity build. The seed binary was renamed aside.
- Receipt: `T40-receipt-8ebf8d8f.json` (candidate `8ebf8d8f04ef`, base `29bd706e`, branch `atlas/dt-t40-ab-no-evidence`, dirty false, campaign sha256 `16f746e7…`, binary sha256 `877d497f…`).
- Raw runs: `T40-ab-live.txt`, `T40-ab-final.txt`, `T40-ab-l90.txt`.

## For Atlas

1. Open the PR when under the cap; this file is the body.
2. **Batch switch:** in `run.sh`, replace `python3 $S/ab.py $B batch<N> …` with `python3 $B/tools/site_ab/ab.py $B batch<N> … --out $S`. Frames, layouts and the table land where they do today (`$S/x-batch<N>/`, `$S/ab-batch<N>.txt`), so `abinputs.py` needs no change. Full rows are identical to the batch's ab.py; rows with a missing frame and the last line differ, so a script that parses the table should expect `NO EVIDENCE` / `PARTIAL` rows and the `no evidence (…)` footer.
3. **cnn evidence now:** until the Z row lands, a cnn-only pass at `--timeout-ms 90000` gives real evidence (4/4, 0.00 % at develop, ~5 min per batch). Your call whether that is worth the batch time; the tool supports it with one flag.
4. The Z row above, if you agree it is one.
