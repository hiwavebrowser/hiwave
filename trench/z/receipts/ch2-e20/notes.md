# CH2.E20: script-inserted `<link rel=stylesheet>` (branch `atlas/z-ch2-e20-inserted-link`)

- base: develop b9fa9836. red: efdf6045. fix: 6567bb68.
- No PR yet: 11 hiwave-macos PRs were open at 21:45 ET against the plan's cap of 8 (max_open_prs).

## Before → after
- Before: the engine looked for stylesheet links once, in `load_subresources`, before the page's scripts ran. A link a script inserted (during the load or after it) was never requested and its rules never applied.
- After: on its first turn and after every layout (the trigger images already use), the live loop (`pump_live`) looks for stylesheet links the document has not requested. Each new one is fetched through `live_sheets`, the S6 late-sheet path, which inserts the sheet and restyles. Load-time URLs are recorded so nothing is requested twice.
- Known limit, written in the code: an inserted sheet cascades after every sheet the load found, in the order the live loop found them. That is right for appended links (what lazy CSS does). A link inserted before a markup link still cascades after it.

## Pins (`inserted_link_tests.rs`)
- a parser-run script appends a link → requested once, rule applies (red: 0 requests).
- a link appended after the load → fetched on a live turn, rule applies (red: 0 requests).
- a markup link plus an added one → the added one applies, the markup sheet is not requested again (red: the added rule never applied).
- 3/3 red on develop's code, 3/3 green with the fix.
- Expected values come from the HTML spec (a connected stylesheet link obtains its resource). No Chromium probe was run.

## Gates at 6567bb68
- Campaign: 26/26, 0 moved (base b9fa9836 vs candidate).
- A/B (ab5.py, 20 sites, capture at the end of the load): no cross-arm mover. google 1.53% and bing 25.38% flip INSIDE the arms (google 3 reruns: both arms flip; bing: one candidate frame in 2 of 3 runs). ab5.py never runs a live turn, so this A/B cannot exercise the change: those rows are page variance by construction. bing loads no external sheet at all (`external_count=0`).
- Live-window A/B (new `tools/ab5_live.py`, `--live-ms 10000`; `ab-e20live.txt`, rerun `ab-e20live2.txt`):
  - **One mover, microsoft: 0.00% inside each arm, 5.99% on all four cross pairs, and the same on the rerun.** The candidate draws the Store Assistant card ('Can we help you? / Chat now / No thanks') at the bottom right. That is the script-inserted storeassistant sheet that S12 found Chrome loads and we never did. This mover is toward Chrome.
  - linkedin 52.64% / 76.80% cross: a short page (5–6 script records against 18) turns up in either arm (base load in run 1, candidate load in run 2). This is a served variant.
  - yahoo varies 35–59% inside both arms. google flips its 1.53% variant inside both arms.
  - The 10 s live window pushes x, cnn, shopify, squarespace and some facebook/netflix/walmart/bing loads past the 30 s capture limit, in both arms.
- Candidate parity binary sha256 b9f337a3b67c4098ecff98c8293068deb368da7b57be0c6afd685330835d5aeb (base 32c315ae…, in `gates.log`).
- Crate suites (`crates-summary.txt`): layout 906/0, bindings 479/0, engine lib 772/0.
- Headless engine suite: **partial**. It ran under the live A/B, and I stopped it at the session cap after 676 ok + 33 FAILED. All 33 had printed 'running for over 60 s' (117 such lines), and all 33 pass on one thread (`suite-failed-1thread.log`, 58 s). The rest of the 2079 tests are owed.
