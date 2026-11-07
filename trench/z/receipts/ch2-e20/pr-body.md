## CH2.E20: a `<link rel=stylesheet>` added by script is fetched

Row CH2.E20 in `trench/z/PLAN-z.md` (hub `atlas/z`). Base develop b9fa9836. Red: efdf6045. Fix: 6567bb68. Regression fix: fb58dc8e. The branch merges cleanly onto develop 5b4371ec (`git merge-tree`).

### Before → after
- **Before:** the engine looked for stylesheet links once, in `load_subresources`, before the page's scripts ran. A link that a script inserted, during the load or after it, was never requested, and its rules never applied.
- **After:** the live loop (`pump_live`) looks for stylesheet links the document has not requested yet. It does this on its first turn and after every layout, the same trigger images already use. Each new link is fetched through `live_sheets`, the S6 late-sheet path, which inserts the sheet and restyles. Load-time URLs are recorded, so no sheet is requested twice.
- **fb58dc8e:** a cancel during the load returned before the load-time URLs were recorded. The live loop then treated the stopped page's markup sheet as an inserted one: it fetched it, restyled the page and started its images. This broke `load_cancel_tests::a_subresource_answered_after_the_cancel_changes_nothing` (develop 3/3 pass, 6567bb68 3/3 fail). Now `load_cancelled` marks every link the stopped document holds as requested. Links inserted after the stop are still fetched.
- **Known limit (commented in the code):** an inserted sheet cascades after every sheet the load found, in the order the live loop finds them. That is right for appended links, which is what lazy CSS does. A link inserted *before* a markup link still cascades after it.

### Pins (`inserted_link_tests.rs`)
- A parser-run script appends a link: requested once and the rule applies. Red: 0 requests.
- A link appended after the load: fetched on a live turn and the rule applies. Red: 0 requests.
- A markup link plus an added one: the added rule applies and the markup sheet is not requested again. Red: the added rule never applied.
- 3/3 red on develop's code, 3/3 green with the fix.
- The red for fb58dc8e is the existing load_cancel test failing at 6567bb68.
- Expected values come from the HTML spec: a connected stylesheet link obtains its resource. No Chromium probe was run.

### Receipt (hand-written fields; receipt.py is Prometheus's step)
- base b9fa9836 / candidate fb58dc8e
- toolchain: rust-toolchain.toml; host: macOS seat (Darwin 25.5.0)
- parity binaries (`--profile parity`), sha256: candidate a61fa94c45ada3e0db407193dfba0468d5ebb770c02585d3617481bbf67b4ee8, base 61c18a71e91d62c478a0c42554ae2a44ae7cd4d89712238f7d6dcccddc1ffd97
- Campaign at fb58dc8e: 26/26 pass, 0 cases moved (diff pixels identical to base b9fa9836 on all 26; `camp-fb58.log`).
- Live-window all-site A/B (`tools/ab5_live.py`, `--live-ms 10000`, base b9fa9836 vs fb58dc8e, 20 sites; `ab-fb58live.txt`): **one mover, microsoft, 0.00% within each arm, 5.99% on all four cross pairs.** It is the same as at 6567bb68: the candidate draws the Store Assistant card from the script-inserted sheet that S12 found Chrome loads. This mover is toward Chrome.
  - linkedin: a short served variant (6 script records against 18) turns up inside arm B. That is page variance.
  - cnn and squarespace hit the 30 s capture limit in both arms (4/4), and shopify in 2 of 4.
  - The other 15 sites read 0.00% everywhere.
- The load-end A/B (ab5.py) at 6567bb68 showed no cross-arm mover. It never runs a live turn, so it cannot see this change.
- Crate suites at 6567bb68: layout 906/0, bindings 479/0, engine lib 772/0.
- **Headless engine suite (`rustkit-engine --lib --features headless`) at fb58dc8e: complete, all 2079 tests, 0 failures left.**
  - Exact-name 200-test chunks at default threads (load 5-9): 2037 ok, 42 FAILED, 29 ignored.
  - 41 of the 42 failures are GPU-guard waits ('waited 120s for ...').
  - The 42nd is `vm_interrupt_tests::a_pure_spin_in_a_load_script_is_stopped_at_the_load_budget` ('the load took 3.2 s'), which also fails on develop under load.
  - **All 42 pass on one thread** (`rerun1t-fb58.log`, 42/42 in 95 s).
  - `load_cancel_tests::a_subresource_answered_after_the_cancel_changes_nothing`, which regressed at 6567bb68, passes.

Receipts: hub `trench/z/receipts/ch2-e20/`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
