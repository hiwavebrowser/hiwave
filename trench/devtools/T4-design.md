# T4 design: `diagnose <url>` (dev-tools lane, 2026-10-24)

Goal (plan row T4, exit metric): one headless run prints one page of text,
ranked "most likely cause" first and facts below, plus the same as JSON. Someone
who has never seen yahoo should learn why its below-fold feed is blank in under
5 minutes. cnn should read "scroll locked by fixed overlay <selector>" at the top.

## What already exists (develop ff6ad36a + lane branches)
- Event log (`--event-log`, `docs/INSPECTOR_EVENT_LOG.md`):
  - T1 errors with stacks (landed, #784).
  - T2 `blocked_by` and initiator kinds (#792, blocked on (E)).
  - T3 `script` and `lifecycle` records (`atlas/dt-script-life`, cap).
- Element diagnostics (`diagnostics.rs`; `parity-capture --diagnose <sel>` and `--diagnose-at x,y`): per element, read-only, from the committed layout. No page-level view.
- `--live-ms` and `--shield`. The live wake is on `atlas/dt-live-wake` (LW, cap). Without it, inserted scripts run only on the last turn, and T3 shows that as yahoo's benji `waited_ms` 24519.

## Shape
1. **Engine: `Engine::page_state(view) -> PageState`** (`diagnostics.rs`, read-only like `element_diagnostics`, runs no script):
   - element count, document height, viewport, scroll offset and max;
   - `html`/`body` computed `overflow-x/y` and `position`;
   - **covering boxes**: fixed/sticky/absolute boxes that cover at least 30% of the viewport. For each: a short selector (`tag#id.class`, first 2 classes), z-index, area %, and whether a hit test at the viewport centre lands in it;
   - **below-fold content**: in bands of one viewport height down to 3 viewports, the counts of text runs, images and boxes with painted backgrounds;
   - open requests and queued inserted scripts at the moment it is taken.
2. **parity-capture `--report <file.json>`**: at the end of the run it writes `{ page_state, event_summary, ranked: [...] }`, and `--report-text` prints the text page. No new binary: it shares the capture path, and `--live-ms`, `--shield` and the event-log flags all apply.
3. **`scripts/diagnose.py <url>`**: the one command. It runs `parity-capture --url <url> --live-ms 25000 --timeout-ms 120000 --shield --event-log <tmp> --report <tmp> --report-text` and prints the page.

## Ranking (deterministic rules over facts; each line cites its records)
Each rule names the facts it read (seq numbers or a page_state path). A rule whose records are absent (no T2 or T3 on this build) is skipped and says so in a footer, so nothing is silently omitted.

| rule | fires when | line |
|---|---|---|
| R1 scroll lock | html/body `overflow:hidden` or `position:fixed`, document taller than the viewport | `scroll locked (body overflow:hidden) by fixed overlay <sel> (z N, covers N%)` |
| R2 covering overlay | a covering box takes the centre hit and covers 50% or more | `overlay <sel> covers N% of the viewport` |
| R3 script never finished | a T3 `script` with outcome `skipped`, `over_budget`, `stopped` or `fetch_failed` | `<kind> script <url> <outcome> (<reason>)` |
| R4 starved script | an `inserted` or `async` script with `waited_ms` over 3 s, or one still queued at the end | `inserted script <url> arrived in N ms and waited N s for a turn` |
| R5 uncaught error | a T1 `script_error`, ranked first when its script is the page's own chunk (same site) | `TypeError in <url>:line:col (stack N frames)` |
| R6 blocked or failed request | a T2 `blocked_by` record or a `failure`, script and stylesheet first | `shield blocked <url> (EasyList ||rule^)` |
| R7 late or held load | `load` more than 5 s after `DOMContentLoaded` | `load waited N s for: <held_by top 3>` |
| R8 silent gap | no record for 3 s or more while `load` is pending or requests are open (cnn: 11.85 to 17.76 s) | `engine silent N s at t=…: not a script or request (callback/timer/turn)` |
| R9 blank below the fold | band 2 or 3 has no text and no images while the top band has some | `below the fold is empty from y=N: <R3/R4/R6 facts about scripts still open>` |

Order: R1, R2, then R9 joined to its causes (R4, R3, R6), then R5, R7, R8. Score = rule weight × (fact present on the page's own origin ? 2 : 1). Ties keep the table order.

## Privacy
The text and JSON follow the event log's rules: no query strings, no page text. The overlay selector does carry page-chosen names (id and classes), unlike the event log. The report is for local use and the lane's PR bodies, so they are kept but capped at 64 characters. **Decision for Atlas:** is a selector with page class names acceptable in a report that may be pasted into a PR? The alternative is tag plus position only (`div fixed z=9999 covers 100%`).

## Packages
- **T4a** (develop, independent): `PageState` plus `--report` with R1, R2 and R9 and the footer. Red-before: a fixture with a body `overflow:hidden` and a fixed full-viewport dialog, and a fixture with an empty band 2. Acceptance: cnn top line R1/R2.
- **T4b**: the rules over event-log records (R3 to R8), read by field name from the JSON, so they light up when T2 and T3 land. Tests use synthetic records.
- **T4c**: `scripts/diagnose.py`, the yahoo and cnn runs, the 5-minute read. Needs T3, LW and T2 landed (or a local merge) for the yahoo answer.

## Open questions for Atlas
1. Stack T4b/T4c on `atlas/dt-script-life` (+ `dt-live-wake`, `dt-net-facts`) locally, or wait for them to land? Proposal: T4a on develop now; T4b reads JSON fields by name, so it does not need the branches to compile.
2. The selector privacy question above.
3. R8 points at something the log cannot name yet (cnn's 6 s). A small `callback` record (network callbacks and timer slices: count and ms per turn) would let R8 say which. Add it as T3b, or fold it into T6?
