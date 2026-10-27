## What

yahoo.com went blank after React's hydration error recovery. Two missing script APIs did it, and this PR adds both:

1. **`Element.removeAttributeNode`** (plus `NamedNodeMap.removeNamedItemNS`). React 19 resets a host singleton (`<html>`/`<head>`/`<body>`) on a client render after a hydration error with `for (l = n.attributes; l.length;) n.removeAttributeNode(l[0])`. The method was missing, so it threw `TypeError: not a callable function`, React left the body empty, and the page painted white. A removed `Attr` keeps its value, has no `ownerElement`, and the name gets a fresh `Attr` if it is set again (DOM §4.9.2). `removeNamedItem` now detaches the same way.
2. **`Intl.Locale`**, over the en-US Intl shim. With (1) in, the client render got further and threw `not a constructor` at yahoo's locale helper (`new Intl.Locale(lang)`, reading `language`/`region`). Supported: subtags (`language`, `script`, `region`, `baseName`), the `-u-` keywords as `calendar`/`caseFirst`/`collation`/`hourCycle`/`numberingSystem`/`numeric`, options overriding them, and the canonical `toString`. There's no likely-subtags data, so `maximize()`/`minimize()` are left out on purpose.

D0 (content reveal). Found while doing the #804 yahoo proof (PLAN-z 23:10 note): #804 does not change yahoo, but this does.

## Red first

- `d74290c6` test (red): `node_apis_tests::remove_attribute_node_takes_the_attr_out_and_keeps_its_value`. It fails with `TypeError: not a callable function`, the same message yahoo logs.
- `c05bf97b` fix.
- `c52928af` test (red): `web_intl_tests::intl_locale_parses_a_tag_its_keywords_and_options`. It fails with `TypeError: not a constructor`, the same as yahoo. Expected strings are Chrome's.
- `7240b217` fix.
- rustkit-bindings: 382/382.

## yahoo (live, 40 s live loop, parity profile)

Each arm is a fresh build from develop `0af43eab`, captured A,B,A,B with `--live-ms 40000`.

| arm | run | body after the load | boxes | document | viewport ink |
|---|---|---|---|---|---|
| develop | 1 | replaced, no classes | 2 | 800 px | 0.000 (white) |
| candidate | 1 | `#news-content-app`, 6 classes | 819 | 2422 px | 0.346 |
| develop | 2 | replaced, no classes | 2 | 800 px | 0.000 |
| candidate | 2 | `#news-content-app`, 6 classes | 818 | 2422 px | 0.345 |

- Develop: React error #418 (hydration mismatch) fires 20 to 50 s into the load, and at the same instant `TypeError: not a callable function` at `iB` (React's singleton reset). After that the page is white. Over this session develop was white in every run where #418 fired inside the window, both before #804 (`68f4c8e1`, 3/3) and after it (`e587d94a`, `0af43eab`, 5/5). One `e587d94a` run painted only because it ended before #418. **#804 does not change yahoo.**
- Candidate: #418 still fires, but React recovers and renders. No TypeError follows it.
- Still open, not in this PR: why yahoo's hydration mismatches (#418), and the two 7730 SyntaxErrors (#777's area).
- The 20-site A/B below runs with no live loop, so yahoo reads 0.00% there: #418 comes later than the board's capture.

## Gates

- Campaign 26/26 at `7240b217` vs develop `0af43eab`: 26 cases, the same diff count on both arms, **0 movers**.
- 20-site all-site A/B (A = develop `0af43eab`, B = `7240b217`), A,B,A,B: **no mover.**
  - Every site has a 0.00% cross-arm pair.
  - linkedin and walmart differ only within one arm (served variants). On the re-run walmart is 0.00% everywhere, and linkedin's within-arm spread (2.96%) is larger than its cross-arm spread (1.55 to 2.64%).
  - lyft: one capture fails after 0.3 s on either arm (B in the first pass, A in the re-run). Every lyft capture that finishes is 0.00%.
- rustkit-bindings 382/382. Bindings only; no engine, layout or paint code is touched.

## Receipt (`scripts/receipt.py`)

```json
{
 "base_sha": "0af43eab",
 "binary": "scratch/pc-ran2",
 "binary_mtime_utc": "2026-10-27T07:26:05.469659Z",
 "binary_sha256": "3cfc943cdca9b9f1ea6fbd61fce7f02a6b59777fb604e6d7e4ac45d69ae6590a",
 "branch": "atlas/z-remove-attribute-node",
 "campaign": {
  "cases": 26,
  "failed": 0,
  "file": "scratch/camp-cand.json",
  "mean_diff_pct": 1.1078,
  "passed": 26,
  "sha256": "81adfad934652d0692a6c9653ee9545609843891e8778796107b9735d91b9ede",
  "timestamp": "2026-10-27T03:27:44.046693"
 },
 "candidate_sha": "7240b217a3e96021ba2cbae613053cf219cf8238",
 "cargo": "cargo 1.91.0 (ea2d97820 2025-10-10)",
 "cargo_lock_sha256": "d43bf3f40c046d3d625a2876c81a524fcaac59b37460f330942147537a4c8cb7",
 "chrome_version": null,
 "cpu": "arm",
 "dirty_state": false,
 "effective_engine_flags": {},
 "features": null,
 "host": null,
 "note": "yahoo 40 s live A,B,A,B in the PR body",
 "os": "macOS-26.5.2-arm64-arm-64bit",
 "profile": "parity",
 "raw_runs": [
  {
   "bytes": 3078,
   "file": "scratch/ab-ran.txt",
   "sha256": "a9dd84d74193fe37fb2593c4c97fa212383e6bfea403302565075269132435ae"
  },
  {
   "bytes": 458,
   "file": "scratch/ab-ran-rr.txt",
   "sha256": "9fc758c41919a2ce54c9f5810e7bfc1867a346f8f51887ccf68709e1aabbd278"
  },
  {
   "bytes": 596225,
   "file": "scratch/camp-base.json",
   "sha256": "568632e6bf6fc0c38dbd0aa6f569c354ff14d9654cceafd4023761c6f6fd1dab"
  }
 ],
 "repo": "https://github.com/hiwavebrowser/hiwave-macos.git",
 "rustflags": null,
 "sccache": true,
 "target": "aarch64-apple-darwin",
 "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)",
 "utc": "2026-10-27T07:45:46.382362Z",
 "work_package": "D0-remove-attribute-node"
}
```


🤖 Generated with [Claude Code](https://claude.com/claude-code)
