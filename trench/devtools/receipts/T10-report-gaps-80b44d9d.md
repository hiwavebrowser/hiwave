T9 found that `diagnose` on yahoo led a reader to "the feed is not blank" while the frame showed grey rows. This closes T9 gaps 1, 2, 4 and 5 in `report.rs`, with parity-capture passing in two capture facts. No engine change. Gap 3 (naming React errors) is out of scope until Pete rules.

## What changed

| gap | report now says | carrier |
|---|---|---|
| 1 placeholders | `[R11] y 1600..2400: 16 painted boxes with no text and no image (skeleton?)`, ranked after R9, above own-site R5 | `Band.empty_painted`; fires at 8 or more in a band |
| 2 R5 clause | `at t=25.4 s; 8 fetch/XHR to www.yahoo.com before, 2 after`, replacing `then N fetch` | R5 line |
| 4 settled | `still changing at capture end: last relayout 10 ms before; 0 requests open`, or `settled at capture end: ...` | `Report.settled`, `--live-ms` captures only |
| 5 shield | `R6 shield: not installed, nothing could be blocked`; an empty section prints no heading | `Report.shield` from `--shield` |

**What R11 counts:** in-flow, visible boxes with no text and no element children, a non-transparent background colour or a gradient, no `url()` image, not a form control or iframe, at least 4 px thick and 16 px long.

**How "settled" is timed:** no record marks the capture's end, so parity-capture times from just before `load_url` to the end of the live window. Records after that are teardown and are ignored. Record times restart at a navigation, so a page that navigated during the capture gets no relayout figure and reads "still changing".

**Also changed:**
- Removed the old "no `blocked_by` field on this build" line. It would be false on a shield run with no failures.
- The two live-window tests now take a lock. `set_live_wake` is one slot per process, so with two live tests in parallel `an_inserted_script_runs_...` failed in 2 of 3 full runs. It passed alone, and has passed every full run since the lock.

## Red first

Before the fix, with the tests in and the new fields stubbed: 14 tests failed, 34 passed (`an_inserted_script_runs_...` also failed, from the wake clash above). Those 14 are the 10 new tests written by then and the 4 existing tests whose expected text changed. The rank test `placeholders_rank_above_an_own_site_error` was added after the fix and has **not** been seen red.

After: `cargo test -p parity-capture` 50/0. `cargo test -p rustkit-engine --features headless --lib diagnos` 33/0 (run on 23db2c70; the later commit touches only parity-capture). The full engine suite was not run, since no engine file changed.

## Yahoo scoring run (branch 80b44d9d, not yet landed; shape-only, script path and class names trimmed)

```
document 2366px tall  1112 elements
Most likely:
  1. [R11] y 1600..2400: 16 painted boxes with no text and no image (skeleton?)
  2. [R5] the page's own script: logged Error thrown in <own-site chunk>; at t=25.4 s; 8 fetch/XHR to www.yahoo.com before, 2 after
  3. [R4] no page script ran until t=5.6 s: 8 script body(ies) had arrived 3.0 s or more before (first at t=1.7 s); first layout at t=4.8 s; last answer before it: image at t=5.6 s
Facts:
  still changing at capture end: last relayout 10 ms before; 0 requests open
  y 0..800: text 24, images 23, empty painted 0
  y 800..1600: text 60, images 39, empty painted 0
  y 1600..2400: text 4, images 1, empty painted 16
Not checked:
  R6 shield: not installed, nothing could be blocked
```

**Exit metric, read from this output alone: still not met (Atlas scores).** It no longer misleads: it says the lower feed is placeholders, nothing is waiting on the network, and the page is still relaying out. It does not say why they never fill.
- "Never" is out of its reach: it sees one 25 s window.
- The logged Error lands at 25.4 s, right at the end of the window. The line gives its timing but no link to the rows, and it does not name the error (gap 3).
- No record links a fetch to the rows (gap 8).

T9's hand check (grey rows at 70 s, in a 2400 px frame) agrees with the band. I did not repeat it.

## How far to trust R11

Calibrated on 7 pages, not a broad sample. The thresholds came from these runs.

| page (`--live-ms` 8000, yahoo 25000) | most empty painted in a band | R11 |
|---|---|---|
| yahoo | 16: grey rows 1184x16, 1184x28, 260x146, 260x130 | fires |
| github | 6 | no |
| wikipedia, bbc, apple, nytimes, hacker news | 0 | no |

The six other sites ran on 23db2c70, before the in-flow fix, which can only lower their counts. The first yahoo run on that commit ranked 12 stacked absolute gradient scrims in the first viewport as a skeleton, which is why positioned boxes no longer count.

Known limits:
- A white box on a white page counts, as does an empty in-flow ad slot.
- A skeleton built from boxes under 8 per band, or with a wrapper holding the colour and children inside it, is missed.
- A `url()` background counts as an image even if it never loaded.
- "Requests open" at capture end is pinned by a unit test only: a fetch started inside a local fixture's load holds the load, so it answers before the window opens.
- On a `--shield` run whose lists were not ready, the report does not say so.

## Campaign and receipt

Campaign 26/26 at 80b44d9d, mean 1.1095%, the same mean as the #833 receipt. T10 changes no render code.

```json
{
 "base_sha": "13f6b4ba",
 "binary_sha256": "d2781b528d26fbb11015e5666708e5b01168111855a4aebe7f3e7e7f48279bb9",
 "branch": "atlas/dt-t10-report-gaps",
 "campaign": {"cases": 26, "failed": 0, "mean_diff_pct": 1.1095, "passed": 26,
  "sha256": "984b846e2df02270ac9734a789a66109b022c5d61cb080872043220bc536d7e6"},
 "candidate_sha": "80b44d9dd6170a845389605789b6f2bca4776d8e",
 "cargo": "cargo 1.91.0 (ea2d97820 2025-10-10)",
 "dirty_state": false,
 "profile": "parity",
 "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)"
}
```

R1: Prometheus. T11 candidates stay gaps 6 and 7.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
