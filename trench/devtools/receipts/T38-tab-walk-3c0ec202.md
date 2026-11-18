# T38: m1_cmd_w_after_clicks clicks tabs from the chrome's own report

Draft PR body (not opened: PR cap, 28 open at 12:50 11-18). Branch
`atlas/dt-t38-tab-walk` @ 3c0ec202, red d7e845ef, base develop 1901c6c8.
Tooling only (`tools/real_window/`): no Rust or app change.

## Problem (Trace #243)

`m1_cmd_w_after_clicks` step 2 swept the tab strip's row from x=232 in
4 px steps until a click closed a tab. In chrome.html every tab's
`.tab-block` ("block this domain and close tab") sits just left of its
`.tab-close` and takes clicks even while transparent (`opacity: 0`, no
`pointer-events: none`). So a left-to-right sweep always meets a block
button first, and the step was NOT RUN on every run. Step 1 used the
same kind of sweep, and only passed because a tab's title comes before
its buttons.

## Fix

- `M1_TABS_JS` runs in the RustKit chrome through the existing
  `HIWAVE_RUSTKIT_CHROME_EVAL` hook (on with `HIWAVE_TEST_HOOKS=1`, which
  the driver already sets; the `test-hooks` cargo feature is not needed).
  Every 250 ms it posts, only when something changed:
  `{"cmd":"m1_tabs","strip":[x,y,w,h],"tabs":[{"id","box","active","block","close"}]}`.
  The strip is `#tabs`, the `overflow-x: auto` scroller that clips tabs.
  It reports ids and boxes only: no titles and no URLs. The app logs the
  body whole under test hooks and answers it with one `Failed to parse
  IPC` line, which is harmless.
- `m1_strip_report` reads the last report. `m1_background_tab_point`
  picks the background tab that shows the most title inside the strip
  and left of its buttons, and clicks the middle of that span.
  `m1_close_point` returns the active tab's close button when it lies
  wholly inside the strip.
- The check waits 0.8 s, then waits up to 10 s for a report. It clicks
  once per step and requires the IPC for that exact tab id
  (`activate_tab`; then `close_tab` plus `Closed tab`). If there is no
  report, the check is NOT RUN and clicks nothing.
- The README says how the check finds the tabs.
- The row asked for "AX/known geometry". There is no AX tree in the
  RustKit chrome (T39/A8), so the geometry comes from the chrome's own
  layout.

## Tests (`python3 -m pytest tools/real_window/tests/`)

- `tests/test_tab_walk.py`, 14 tests. The fake strip is laid out the way
  chrome.html lays it out: the active tab is centred and tabs are clipped
  at the strip's left edge. A fake hw answers clicks and keys in the log
  format the app uses.
- **Red first:** 12/12 red at d7e845ef on develop's driver. The strip
  model reproduces Trace #243 exactly: `NOT RUN — the walk met the tab's
  block button first (x=360)`.
- **Green:** 14/14. Two pins were added after the fix: a tab that shows
  mostly buttons is clicked left of them, and a tab wholly outside the
  strip is never picked.
- **Mutations**, each turning tests red: dropping the button limit (1
  red), dropping the strip clip (5), allowing a close button outside the
  strip (1), and not passing the reporter env (1).
- The full driver suite is 53/53.
- The reporter JS ran under node against a fake DOM. It posts once, stays
  quiet when nothing changes, and posts again on a change. The driver
  parses its output to `('7', (229, 28))` and `('8', (446, 28))`.

## Owed

- A real-window `--checks m1_cmd_w_after_clicks` run on a granted seat.
  This seat has no Accessibility grant. The run would also be the first
  time `M1_TABS_JS` executes in RustKit's Boa chrome (it uses
  NodeList.forEach, dataset, classList and getBoundingClientRect, all of
  which chrome.html already uses).

## Campaign and receipt

The campaign ran on parity-capture built at the candidate
(`z-cargo build --profile parity`, 1m46s), with a no-op cargo shim.
Result: **26/26, mean 0.4052 %**. Worst cases: article-typography
3.49 %, form-controls 2.67 %, backgrounds 1.01 %.

```
base_sha 1901c6c8  candidate_sha 3c0ec202cb446c03fc7a999b474192aa8610dec8  branch atlas/dt-t38-tab-walk
binary target/parity/parity-capture sha256 ef1cf287a79a81ba781bc74da1321ee28c611092ecb975f5e5c2c1fb420f193a
profile parity  dirty_state false  toolchain rustc 1.91.0 (f8297e351 2025-10-28)  cpu arm  os macOS-26.5.2-arm64
campaign: cases 26 passed 26 failed 0 mean_diff_pct 0.4052 (sha256 a3cda28b4a8cf6ea…)
```

Merge note: T37 (`atlas/dt-t37-key-ack`) also edits `driver.py`, in
different hunks (key timing near `resize_request_epoch` and `Driver`
~L1100). This branch's hunks are after `set_tab_urls` and in the m1
check.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
