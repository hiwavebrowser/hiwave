# T14b: WPT runner follow-ups from the #844 R1

Branch `atlas/dt-t14b-wpt-followups` @ e77f8cba, base develop 546d6196. Runner, manifest, a sync comment and docs; no engine change.

## Evidence
- **Red first:** 9dd34beb commits the tests over the T14 runner: 31 of 47 fail. After e77f8cba: `python3 -m pytest scripts/tests/test_wpt_tier1.py` 47/0.
- **Item (3) red separately:** its new test also passes on the old runner, because the bug was in the test. The old form's call, with the temp dir inside a checkout, returned `546d6196…` instead of `None`. The suite now passes with `TMPDIR` inside the checkout: 47/0.
- **Count on develop 546d6196, unchanged:** 26/27 scored, 1 FAIL, 3 SKIP, 0 ERROR, n=30, negative control red, stale-binary guard on. Compared with the unchanged runner (that base run used `--allow-stale`; same binary) on the same binary: status, reason, diff, campaign diff and `blocked_by` move on 0 of 30 rows.
- **Campaign:** 26/26, mean 1.1095%.

## What each item became
1. **Unquoted attributes:** `href`/`src` in all three quotings, in the gate. Dropped as false positives: `url(` in HTML and CSS comments, `<meta content>`, `data-src=`.
   - **Went past the row, same class:** `rel=match`, root-absolute staging, the `/fonts/` and `flags` web-font tags and `name=fuzzy` had the same quoted-only regexes. An unquoted `href=/fonts/x.css` would have resolved to the filesystem root and rendered without its sheet.
   - **Needed by the change itself:** `src=` is now read inside tags and not from script bodies. Otherwise `img.src = next` would read as a missing resource called `next`.
2. **`campaign_diff` returns `(pct, why)`:** new per-case `campaign_not_measured`, for no `node_modules`, no node, a crash (exit and last line), timeout, no JSON, non-object JSON (the old `TypeError`), and a non-number including bool and NaN. Pinned by mocks only: this run measured all 27, so no live row carries a reason.
3. **Temp-dir test:** uses a `git init`-ed scratch directory.
4. **Precedence:** new `gate()`; a missing resource outranks SKIP.
5. **`CARGO_TARGET_DIR` honoured:** relative paths from the repo. `capture_binary` in `last-run.json` keeps an absolute path for a target outside the repo. One live `--case` run through an outside target dir: rc 0.
6. **README:** stale sync line fixed (the #844 R1 ran the script whole; this seat still cannot), and the build difference is stated rather than removed: `parity_test.py` uses `--release`, the WPT runner `target/parity`.
7. **`unproven`:** the eight T14 probe survivors carry `unproven` in the manifest and appear in `unproven_passes`. They still count toward 26. No second mutation was written, so they stay unproven; the probe itself was not re-run on this head.

## Not done
- `wpt_sync.sh` was not run as a script: this seat still refuses it, and its steps ran from a Python wrapper with the same `--stdin` path list.
- "Fresh clone" is again a fresh `new-task.sh` checkout.

## Receipt (`scripts/receipt.py`)
```json
{
 "base_sha": "origin/develop",
 "binary_sha256": "26e721c1ab4656e8021cd36b64b31154cb9564e89facc3bbf201033a07e4cea7",
 "branch": "atlas/dt-t14b-wpt-followups",
 "campaign": {"cases": 26, "failed": 0, "passed": 26, "mean_diff_pct": 1.1095,
  "sha256": "91965f41f90468c03e76397b673f4d83cebf1d406df493910037a72201cb0585"},
 "candidate_sha": "e77f8cba49c92e5cfb5f99e89d33df27a5dcc727",
 "dirty_state": false,
 "profile": "parity",
 "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)",
 "repo": "https://github.com/hiwavebrowser/hiwave-macos.git"
}
```
`base_sha` records the ref as passed; origin/develop was 546d6196. The campaign ran on the parity build through a no-op `cargo` on PATH, per the 10-29 recipe.
