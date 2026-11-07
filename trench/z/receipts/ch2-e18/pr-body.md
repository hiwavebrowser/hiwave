## CH2.E18: attribute selector case flag `[a="v" i]`

**Bug.** The attribute matcher kept the case flag as part of the value. `[data-a="Foo" i]` compared the element's value against `"Foo" i`, so no flagged selector ever matched, and `:not([a="v" i])` matched every element. Chromium 143 matches.

**Fix** (`SelectorMatcher::attr_selector_test`, `rustkit-engine/src/lib.rs`):
- A quoted value ends at its closing quote, and an unquoted one at whitespace. What follows is the flag.
- `i` or `I` gives the operator's ASCII case-insensitive form (`"=i"`, `"~=i"`, …). `attr_test_passes` lowercases both sides with `to_ascii_lowercase`, so `é` still does not match `É`, as in Chromium.
- Any other flag, `s` included, makes the selector invalid. Chromium 143 does not take `s`. `selector_list_is_valid` now rejects it, so the rule is dropped and `querySelector`, `matches` and `closest` throw `SyntaxError`. Inside `:is()`/`:where()` only that member is dropped.
- The operator is now the first `=` plus the character before it. Before, the first operator found anywhere in the text was used, so an operator inside a quoted value (`[a="x~=y"]`) split the selector in the wrong place.
- The rule index, the match-sharing key and the invalidation index all go through these same two functions, so they pick up the flag too.

**Red first.** b13f4a74 adds the pins, then 983e4084 is the fix.
- `attribute_flag_tests.rs` uses the page `tools/parity_oracle/attribute_flag_page.html`. The expected answers come from `tools/parity_oracle/attribute_flag_log.mjs` on Chromium 143.0.7499.4.
- Cascade: on develop, 3 of the page's 27 navs are shown (`l1 o0 o1`). With the fix, the 16 that Chromium shows are shown (`a1 b1 c1 d1 e1 f1 g1 k1 l1 m1 n1 o1 p1 q1 u1 v1`).
- Matcher unit pins cover all six operators with `i`, both quote styles, the unquoted form, no space before the flag, extra whitespace, ASCII-only folding, `s` and an unknown flag, and an operator inside a quoted value.
- Script pins check `querySelectorAll` with `i`, `s` (throws), the unquoted form and a bad flag (throws), plus `matches` and `closest`.
- Result: 3 failed on develop, 3 passed with the fix.

**Gap found, not fixed here (row CH2.E27).** A script query with an attribute on an ancestor compound ignores that ancestor's attributes. `querySelectorAll('[data-m] nav')` returns all 27 navs, where Chromium returns 2. The query path gives attributes only to the root element in its ancestor chain. The `closest()` pin therefore starts from a node it can reach directly.

**Gates** (all on the candidate 983e4084; base = develop 0da5827a; both arms built `--profile parity` in this worktree):
- New pins: 3/3 pass (they failed 3/3 on develop at b13f4a74).
- 26-case campaign: 26/26, 0 cases moved against the base binary (`campdiff`).
- All-site A/B (20 sites, A,B,A,B): no cross-arm mover from this change.
  - google 1.53%, facebook 45.83% and squarespace 2.21% (rerun) differ only inside the base arm. These are page variants.
  - walmart and microsoft lost loads to timeouts in the first pass. In the rerun they read 0.00% on every pair.
  - cnn timed out on all four loads, as on develop.
- Headless engine suite (`rustkit-engine --lib --features headless`): **partial, still owed.** Three other seats ran engine suites at the same time, at load 17–25.
  - The default-thread run was cut at the 50-min limit after 1089 of 2078 tests: 1044 passed, 45 failed.
  - All 45 failures had printed 'running for over 60 s' (GPU guard / wall clock). On one thread, 43 of them pass.
  - The other 2 are content_thread load deadlines on pages with no attribute selector: `a_navigation_mid_flight_records_one_cancel_in_the_old_document` (8 s load) and `shutdown_does_not_wait_for_a_spinning_script` (10 s load).
  - Every selector and attribute test that ran passes, including `ancestor_attribute_tests`, `is_complex_argument_tests`, `id_compound_selector_tests` and `diagnostics_tests::every_invalid_selector_is_an_error`.
  - The 989 tests the cut run never reached are being run by exact name. Results so far are in the next comment.

## Receipt (`scripts/receipt.py`)

```json
{
 "base_sha": "0da5827a",
 "binary": "scratch/bins/cand",
 "binary_mtime_utc": "2026-11-06T23:21:58.941801Z",
 "binary_sha256": "f4fc39d834989834d5bb828f3a3bf99c79061ffcf55dc5c6f09f7e92124a6e5a",
 "branch": "atlas/z-ch2-e18-attr-i",
 "campaign": {
  "cases": 26,
  "failed": 0,
  "file": "scratch/camp-cand.json",
  "mean_diff_pct": 1.073,
  "passed": 26,
  "sha256": "c2728fed32d42b29fbabee2c9df3f88567ffa9176119a80515b0ec9a03906ad4",
  "timestamp": "2026-11-06T18:22:41.892584"
 },
 "candidate_sha": "983e4084c4892265d5f7d9718ba39409e2a034aa",
 "cargo": "cargo 1.91.0 (ea2d97820 2025-10-10)",
 "cargo_lock_sha256": "36360f8f04d56d938a5d58455c21b1feb791b309cc1dc7eddd356856f9a28e0d",
 "chrome_version": null,
 "cpu": "arm",
 "dirty_state": false,
 "effective_engine_flags": {},
 "features": null,
 "host": null,
 "note": null,
 "os": "macOS-26.5.2-arm64-arm-64bit",
 "profile": "parity",
 "raw_runs": [
  {
   "bytes": 3066,
   "file": "scratch/ab-e18.txt",
   "sha256": "0c555cb97dc5c3639ec8eb527f84b012ed344329c341bbe011b2dcad7c796c4a"
  },
  {
   "bytes": 476,
   "file": "scratch/ab-e18re.txt",
   "sha256": "17d1508b7b663fd92cf7d9ef69fe65df17bd3ad99909e92bb70b2048a758b7f9"
  },
  {
   "bytes": 596201,
   "file": "scratch/camp-base.json",
   "sha256": "7ceee181e0b86d019c7d6068a5c74a035a59b8136e99953f9eed4738a9d08a0e"
  }
 ],
 "repo": "https://github.com/hiwavebrowser/hiwave-macos.git",
 "rustflags": null,
 "sccache": true,
 "target": "aarch64-apple-darwin",
 "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)",
 "utc": "2026-11-07T00:05:28.494326Z",
 "work_package": "CH2.E18"
}
```

R1: Prometheus. R2: any non-author.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
