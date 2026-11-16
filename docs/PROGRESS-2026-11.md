# HiWave progress, November 2026

Status as of 2026-11-16. This page covers the macOS tree, which is the
reference platform for RustKit, the project's own engine. Where a number is
compared with Chrome, the reference is Chrome for Testing 148 on the same Mac.

Every figure below names its source. Two kinds are public: the
[hiwave-macos releases](https://github.com/hiwavebrowser/hiwave-macos/releases)
and its [merged pull requests](https://github.com/hiwavebrowser/hiwave-macos/pulls?q=is%3Apr+is%3Amerged).
The third is the project's batch gate records: the results each batch's gate
run wrote down before the batch merged (cited below as "gate records", with
the date of the entry).

## Releases

| Release | Published (UTC) |
|---------|-----------------|
| [V1.5.0](https://github.com/hiwavebrowser/hiwave-macos/releases/tag/V1.5.0) | 2026-11-15 (promoted to `master` on the evening of 2026-11-14, US Eastern) |
| [V1.4.0](https://github.com/hiwavebrowser/hiwave-macos/releases/tag/V1.4.0) | 2026-10-24 |
| [V1.3.0](https://github.com/hiwavebrowser/hiwave-macos/releases/tag/V1.3.0) | 2026-10-12 |
| [V1.2.0](https://github.com/hiwavebrowser/hiwave-macos/releases/tag/V1.2.0) | 2026-10-02 |
| [V1.1.0](https://github.com/hiwavebrowser/hiwave-macos/releases/tag/V1.1.0) | 2026-09-24 |

V1.5.0 added dedicated workers with structured clone, a rasterised and
painted 2D canvas, faster layout of deeply nested pages, and fixes that make
several previously failing sites usable. The release notes list what changed,
the evidence, and the known issues.

Fixed on `develop` since V1.5.0 and not yet released: a crash in the
JavaScript engine's inline caches
([#1177](https://github.com/hiwavebrowser/hiwave-macos/pull/1177)). The fix
ships with the next release.

## How changes land

Since 2026-11-02, changes to hiwave-macos land in batches. A batch is a set of
pull requests that have each had an independent review. The batch is merged
only after one combined gate on a Mac:

- the unit and integration suites;
- a 26-page capture campaign: each page is compared with Chrome, and its
  capture must be byte-identical to the previous build's unless the batch
  explains the change;
- a 42-state board of the browser's own interface, drawn by RustKit and
  compared with Chrome's;
- a 19-site A/B run against the previous build;
- a subset of the Web Platform Tests;
- two passes of the real-window interaction checks (572 checks per pass).

The merged tree must equal the tested tree.

Batch numbering reached 95 on 2026-11-16. Not every number landed: some
batches were re-cut or retired. From batch 74 onward each batch is its own
pull request; 21 batch pull requests (batch 74 to batch 95b) merged between
2026-11-13 and 2026-11-16. Earlier batches were merged as their member pull
requests and are listed in the gate records.

Sources: V1.5.0 release notes ("Every PR in this release landed through a Mac
batch gate..."); gate records, entries of 11-02 23:40 and 11-16 11:35; merged pull
requests titled "batch N".

## Test counts

Passing tests recorded by the batch gate, with no failures in either column.

| Suite | Batch 1, 2026-11-02 | `develop` `d4455b45`, 2026-11-16 |
|-------|--------------------:|---------------------------------:|
| Engine, headless | 1,496 | 2,588 |
| Engine library | 618 | 905 |
| Layout | 881 | 978 |
| Script bindings | 428 | 732 |
| JavaScript engine crate | not recorded | 211 |
| App | not recorded | 250 |

Sources: gate records, entries of 11-02 23:40 and 11-16 11:35.

## Measurements at `develop` `d4455b45` (2026-11-16)

- **Real-window interaction pass:** 570 of 572 checks pass. One check fails
  (saving a setting) and one is not run. Opening and closing a tab from the
  keyboard (Cmd+T, Cmd+W) takes 157 to 164 ms.
- **Capture campaign:** 26 of 26 pages pass, with a mean pixel difference of
  0.405% from the Chrome reference. At V1.4.0 the mean was 1.1%.
- **Browser-interface board:** 39 of 42 states match. On 2026-11-09 the same
  board stood at 21 of 42.
- **Web Platform Tests subset:** 99 pass, 151 fail.
- **Frame pacing:** the real window drew about 52 frames per second at the
  start of the pacing work on 2026-11-15, then 56, then 60. A 3-second probe
  now counts 179 to 181 frames, the same count as Chrome on the same Mac.

Sources: gate records, entry of 11-16 11:35 (all five); V1.4.0 and V1.5.0 release notes
(campaign means); gate records, entry of 11-09 (board at 21 of 42); gate records, entry of 11-15
10:28 (about 52 frames per second before the pacing work).

## Landed behind a flag, or planned

- **Same-origin iframes** are on `develop` behind a flag that is off by
  default (batch 87, 2026-11-15). They are not in V1.5.0.
- **WebAssembly** has an approved plan, using the `wasmi` interpreter. It has
  not shipped.
- **A baseline JIT** for JavaScript is at the plan stage. No decision has been
  made to build it.
- **Media playback** is not implemented.

Sources: gate records, entries of 11-14 11:30 and 11-16 11:35; V1.5.0 release notes
("Not in this release").

## Stress suites: where the engine is behind

The current priority is the standard browser stress suites: Speedometer,
MotionMark and JetStream. The project's bar is Chrome's result on the same
Mac. RustKit is not at that level.

- At V1.5.0 no stress suite produced a score.
- MotionMark now completes end to end in the real window. That is the
  milestone. One run, with a raised time budget for the stress test, scored
  52.16 overall. Two of its eight subtests (Multiply and Images) still score
  at the floor of the scale. This is a single run, not a median, and it is
  not a result to compare with other browsers.
- Speedometer needs iframes and JetStream needs WebAssembly, which are in the
  states listed above.

Sources: V1.5.0 release notes ("No stress suite ... produces a score yet");
gate records, entries of 11-12 09:30 (priority) and 11-16 11:35 (MotionMark subtests).

## Process

Every pull request gets an independent review before it joins a batch.
Details of security hardening work are not published.

## Development activity

![Weekly non-merge commits and merged pull requests on hiwave-macos, hiwave-windows and hiwave-linux from 29 December 2025 to 16 November 2026, with cumulative commits. The two full weeks starting 2 and 9 November have 665 and 928 commits and 171 and 219 merged pull requests.](../charts/commit-history.svg)

What the chart counts:

- **Commits:** non-merge commits reachable from the `develop` branch of
  hiwave-macos, hiwave-windows and hiwave-linux, placed in the week of their
  author date. Merge commits are excluded.
- **Merged pull requests:** every merged pull request in the three repos,
  placed in the week of its merge date.
- Weeks start on Monday, UTC. The last bar is an unfinished week. This
  umbrella repo, including its automated metrics commits, is not counted.
- Data fetched 2026-11-16 and stored in
  [`metrics/commit_history.json`](../metrics/commit_history.json).

| Period | Non-merge commits | Merged pull requests |
|--------|------------------:|---------------------:|
| July 2026 | 222 | 179 |
| August 2026 | 297 | 122 |
| September 2026 | 440 | 234 |
| October 2026 | 1,258 | 406 |
| Week of 2026-11-02 | 665 | 171 |
| Week of 2026-11-09 | 928 | 219 |
| All time, to 2026-11-16 | 4,139 | 1,364 |

The repos were close to idle from late January to early July 2026; the chart
shows that gap as it is. Commit and pull request counts measure activity, not
quality: the measurements above are the evidence for what works.

To regenerate the chart:

```bash
python3 scripts/commit_history_chart.py --fetch   # refresh the data (needs an authenticated gh)
python3 scripts/commit_history_chart.py           # redraw from the stored data
```
