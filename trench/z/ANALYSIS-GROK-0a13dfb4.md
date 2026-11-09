# ZeuzGb / Grok seats: post-pause analysis of hiwave-macos develop 0a13dfb4

Written Mon 2026-11-09, 07:10–08:30 ET, by ZeuzGb's executor on Pete's direct go (Pete, 07:08 ET: "Did you get the word to run a full test suite post pause? It should already be happening."). Scope is Atlas #1269/#1270/#1298: **measurement only**. No engine code, no PRs, no pushes, no CI, no live-site loads by me. develop was not touched.

- **Head measured:** `0a13dfb4` (batch 47), which is origin/develop's tip at 07:12 ET (`git ls-remote`). Tree `569ae7ac`, identical to batch-47 tested tree `1fd84580`.
- **Baseline:** the pause head `0db52779` (batch 45, tree `1d63d234`).
- **Binaries:** copies of Atlas's banked builds in `/Users/petecopeland/zg-measure/bins`. sha256 prefixes: `hiwave47` production `8743506f`, `hiwave47th` test-hooks `2928405b`, `cand47` parity-capture `67911b07`, `hiwave45` `18651f49`, `hiwave45th` `ecd86630`.
- **Labels.** **[MINE]** means I ran it this morning: real window, fixtures only, the real-window lock held, Inspector closed. **[A47]** means Atlas's batch-47 gate artefacts, which I re-read and recomputed from raw files (scratchpad `batch47/`). **[A46]** and **[A45]** are the same thing for the baseline arms.
- **Disclosure.** I read `TRIAGE-i0a-2026-11-09.md` before my own runs, so my resize and i0a_nav reading is not blind. The seats' reads (tasked in Null zeuzgb #243) will be.

## 0. Headline: pause head 0db52779 vs head 0a13dfb4

| front | pause 0db52779 | head 0a13dfb4 | src |
|---|---|---|---|
| Chrome board, two-rule gate | 21/42 | **21/42**, every row identical (pixel % and geometry count) | A46 dev vs A47 cand, recomputed |
| └ via rule 1 (≤0.5 % px) / rule 2 (geo 0) | 21 / 0 | 21 / **0** | recomputed |
| Campaign (26 cases) | 26/26, mean 1.0298 % | 26/26, **mean 1.0298 %**, per-case identical | A45 / A47 json |
| WPT tier-1 sample | 104/349 (104/322 scored) | **104/349**, 0 status flips | A46 dev / A47 cand json |
| Real window, same 55 checks | 486/500 (14 FAIL) | **491/499 (8 FAIL)**. The +2 M1 checks give 506/515, plus 1 NOT RUN. | A45 / A47 rwsum |
| 19-site A/B | n/a | "no batch mover" holds only on **13 of 19** sites; 6 are noisy or unscored (§6) | A47 |
| Click on a loading page (LAT15 fixture) | answered 8827 ms, on screen 8917 ms | **8851 ms, on screen 9015 ms**; longest turn 12160 ms, 1 segment | **MINE** |
| Pure `while(true){}` (load and timer) | stopped, **silently** (no log line), recovers | stopped at the **loop-iteration cap** in ≤0.13 s (load) or about 0.1 s (timer), logged, recovers 3/3 | **MINE** |
| Memory: 30 navs + 30 tab cycles, one session | heap 80 → 454 (navs) → 1381 MB (cycles, tabs not closing) | heap 82 → **107** (navs) → **196** MB (cycles); RSS 211 → 417 MB after idle | **MINE** |
| Linux | synced to 0db52779 (S16) | **not yet at 0a13dfb4** | Null talos 433, castor 75 |
| Windows | macOS 27129415 (refresh #15, merged) | **refresh #16 not started cleanly** (two sessions on one tree) | Null athena 563, atlas 1293 |

## 1. Chrome board (macOS host) — 21/42, not inflated by T35, but fragile

- The batch-47 board.json shows **21/42 under both rules** on cand47. All 21 green rows pass **rule 1** (≤ 0.5 % pixels). **No row is green by rule 2** (geometry 0 and ≤ 1.5 %).
- **T35's worry is that the macOS host drops more scorer joins, so 21/42 is generous. At this head the worry cannot touch the count.**
  - Rule 1 does not use joins at all.
  - The only rows with geometry 0 (shelf ×6, inspector console_tab ×3) are already pixel-green.
  - T35's evidence came from the 022aa2fa receipt, where macOS join_failures totalled **291**, with 11/13/11/8 on the four chrome rows Talos named.
  - At 0a13dfb4 they total **51**. Those chrome rows now read **3/3/3/0**, the same as Linux's 3.
  - So most of the join gap closed between batch 41 and batch 47. The other 51 are unnamed: board.json keeps counts only, so T35's selector dump is still worth one run. It can no longer change 21/42.
- **Fragility (new finding).** Three green rows have almost no margin:
  - report/weekly 1280×800 is exactly **0.5000 %** (raw diffPercent 0.5; the gate is ≤ 0.5).
  - report/default 1280×800 is 0.4984 %.
  - inspector/console_tab 1024×700 is 0.495 %.
  - The board rounds to 3 decimals before gating (chrome_board.py:423). A single-digit pixel change flips them. An honest band is **18–21/42**.
  - On Linux the two report rows score 0.382 % (talos 432), so this is macOS raster noise.
- Nearest red rows: chrome/find_open 1600×1000 at 0.536 %, chrome/hover_tab2 1600×1000 at 0.591 %, chrome/default 1600×1000 at 0.599 %.
- Pause → head: 0 rows moved. That is expected, since batches 46–47 are latency and memory work.

## 2. Campaign and WPT
- **Campaign:** 26/26, mean **1.0298 %** at 0db52779, 35034d6f and 0a13dfb4, with every case identical. Worst cases: article-typography 4.786, about 3.330, form-controls 3.239, card-grid 1.343, css-selectors 1.308. [A45/A46/A47]
- **WPT:** 104/349. Scored 104/322: fail 156, unproven 62, skip 5, error 22. There are 0 flips between the pause arm and the head arm, comparing the per-case status of all 349. 23 fails are attributed to WOFF/WOFF2 web fonts. [A46 wpt-dev vs A47 wpt-cand]

## 3. Real window: full list at the head, root causes for what is left

At 0a13dfb4 (A47 rw-full1, hiwave47th): **506 PASS / 8 FAIL / 1 NOT RUN of 515**. On the 55 checks the pause run also had, that is 491/499. The pause run (A45) had 486/500. What changed: h19_spin 7/9 → 9/9 and i0a_script 7/12 → 10/11 (the check dropped Cmd+T). The M1 checks are new.

| FAIL | what | root cause (my read) | user feels it? |
|---|---|---|---|
| i0a_script, i0a_layout, i0a_close, i0a_nav: "resize answered within 200 ms" (453–514 ms) | 4 | **Harness.** `hwdrive resize` ends in `usleep(400_000)` and the check times the whole subprocess. I reproduced 481–488 ms on both pause and head binaries this morning [MINE]. Atlas's #1008 (T36) fixes the check. | No, for the ack. Yes, mid-load: TRIAGE measured the laid-out frame at 35–1088 ms. That is LAT15's case, not a resize bug. |
| i0a_nav: visits / left within 1 s / last page green | 3 | Two causes. (a) **Harness:** Cmd+T loads the start page into the measured view. (b) **Engine (LAT17):** every external script is fetched before any script runs, so page 1's inline `location.href` waits for a later `/slow` script (1.6–1.7 s per page vs Chrome 0.03 s). | (b) yes: every script-heavy real page is late by its slowest script fetch |
| b11_settings_save: "sidebar shows a Settings item" | 1 | Missing chrome entry point (no Settings item in the sidebar); not responsiveness | Small |
| m1_cmd_w_after_clicks NOT RUN | 1 | The check's walk to a tab's close button met the tab's block button first (x=236): a check-geometry issue | No |

### 3.1 Watchdog vs recovery (Pete's rule 1), tested separately [MINE]
Six real-window runs (fixtures in `/Users/petecopeland/zg-measure/pages`; harness `zgrw.py`), plus the 0a13dfb4 driver's own h19_spin, i0a_script and i0a_close on the **production** binary:

| case | binary | what stopped it | log line | fresh callback runs after | pending XHR completes | last frame visible |
|---|---|---|---|---|---|---|
| h19 nested forEach in a load script (no loop statement) | hiwave47 **production** | **15 s budget** (elapsed_ms=15000, late 0) | yes | not asserted by h19 | not asserted by h19 | yes (80000 green px) |
| same | hiwave45th (pause) | 15 s budget (15000, late 0) | yes | — | — | yes |
| i0a_spin timer, nested forEach | hiwave47 production | 5 s live-turn budget (5000) | yes | yes | yes (asked 1, onload 1) | yes |
| same | hiwave45th (pause) | 5 s live-turn budget | yes | yes | yes | yes |
| pure `while(true){}` in a load script | hiwave47 | **loop-iteration cap**, elapsed_ms 115 (th: 134) | yes: "Script stopped at the loop-iteration limit" | yes (0.06–0.28 s) | yes | yes; the next `<script>` also ran |
| same | hiwave45 (pause) | stopped (page carried on) | **none** | yes | yes | yes |
| pure `while(true){}` in a timer | hiwave47 | loop-iteration cap, logs **elapsed_ms=0** | yes | yes (0.16 s) | yes | yes |
| `while(true){ for(i<5e6){} }` in a load script | hiwave47 | loop-iteration cap after **2257 ms** | yes | yes | yes | yes |
| same, in a timer | hiwave47 | loop-iteration cap, **elapsed_ms=0**, stopped within about 0.3 s wall | yes | yes | yes | yes |
| same, both | hiwave45 (pause) | stopped (page carried on) | **none** | yes | yes | yes |

**Reading:**
1. **The production build arms the 15 s budget and logs why.** h19 on hiwave47 stopped at 15000 ms with late 0. test-hooks only gates the panel probe and IPC logging, not the budget (`hiwave-app/src/main.rs` 773–996; `webview_rustkit.rs:207` LIVE_SCRIPT_BUDGET_MS=15000).
2. **The 15 s watchdog is never what stops a pure JavaScript loop.** The loop-iteration cap gets there first:
   - The load path's limit is 10,000,000 (`EngineConfig.script_loop_iteration_limit`).
   - The timer and job path uses `loop_limit.min(100_000)` (`rustkit-engine/src/lib.rs:7374`). That fits the 0 ms timer stops.
   - So "watchdog interrupts a pure loop" is **unproven, because no fixture I could write reaches it**. Every pure loop dies at the cap first. The watchdog is proven only for the nested-callback shape (h19, i0a_spin).
3. **Recovery passes on every shape, and it already passed at the pause head.**
   - With the new checks, the pause binary hiwave45th passes h19 9/9 and i0a_script 10/11 (only the resize assertion fails).
   - This independently confirms Atlas's #1002 claim that 6 of 7 batch-44 FAILs were the checks.
   - #1002's engine change is the log line for a loop-cap stop. At pause the stop was silent; now it is logged.
4. **New risk, flagged but not yet measured against Chrome.** A timer or callback with an ordinary loop of about 100k+ iterations is killed in 0 ms. Example: a 5M-iteration `for` in a `setTimeout`. Chrome runs that code, so real sites doing heavy work in callbacks will break silently. It is also mislabelled: the log reads `elapsed_ms=0`. This is a correctness row (BACKLOG), not a milestone blocker. **UNVERIFIED** whether any site in the board hits it.

### 3.2 i0a_nav judged by what committed (rule 2)
I did not re-run i0a_nav myself. Atlas's TRIAGE repro without Cmd+T (final page commits, is visible and is the newest history entry; Chrome 148 differs only in the replace-vs-push of history) is consistent with the A47 log: `Navigation cancelled ... nav_id=1`, then the start page HTML loaded into the same view. My only disagreement is in §7, on priority.

### 3.3 Resize in two parts (rule 3)
I measured only the harness half [MINE]: 481–488 ms on both binaries, i.e. sleep-bound. I did not re-measure ack vs first sized frame. TRIAGE's figures (ack ~1 ms; first sized frame 5–9 ms idle, 134–239 ms under expensive layout, 35–1088 ms mid-load) stand unreplicated by me.

## 4. Latency: the finish line at 0a13dfb4

| metric (BASELINE.md exit metric) | target | at 0a13dfb4 | src |
|---|---|---|---|
| A click on a page that is still loading | (milestone) | **8851 ms** to the page's handler, **9015 ms** to the screen; first content at 2360 ms; longest uninterrupted content-thread turn **12160 ms in 1 segment** | **MINE**, lat15app.py fixture (2 s sheet, 4 s image, 3×2 s scripts) |
| same at the pause head | | 8827 / 8917 ms; turn 12146 ms | MINE |
| window thread holds ≥ 200 ms during spin / layout / mid-load | none | **none** in every i0a run and in all 12 of my spin runs | A47, MINE |
| Cmd+T / Cmd+W during a spin or layout | ≤ 200 ms | 156–183 ms. This is an upper bound: it times the whole hwdrive key subprocess (T37). | A47, MINE |
| script-budget stops/min, hold p95, input-to-present p95 on Pete's 15-site loop | ≤1/min; ≤50 ms; ≤100 ms | **NOT MEASURED at this head** (live sites; Pete's hand test only). The last figures are from 8ebc1b79: stops 0.44/min, hold p95 about 730 ms on wikipedia. | HANDTEST-2026-11-08 |
| input-to-present (LAT1c), real-window session | p95 ≤ 100 ms | batch 46: n=300, 13 over 100 ms (worst 2772 ms), but `input_to_present_p95_ms` = **null** while `..._under_threshold` = **true** | A46 i2p.json |

**Reading:** batch 46–47 did not move the click-while-loading number at all (8.8 s → 8.9 s, within noise). It is the largest remaining failure of the milestone, and it is LAT15 (#1006, batch 48, not landed). The exit-metric script still reports a pass when the p95 is null (see the 11-08 analysis §1.4). LAT1d is the fix row, so the input-to-present "pass" is **not evidence** until LAT1d lands.

## 5. Memory over a 30-navigation + 30-tab-cycle session (one app) [MINE]
One app per binary. It is restored on a small local page that navigates itself 30 times, then runs 30 cycles of Cmd+T → type a local URL → Return → Cmd+W. heap(1) and RSS are read at each mark, and again after 60 s idle. Harness `zgrw.py mem` (it reuses tools/latency/tab_cycle_views.one_cycle).

| mark | head 0a13dfb4 heap MB / nodes / RSS MB | pause 0db52779 heap MB / nodes / RSS MB |
|---|---|---|
| before | 81.9 / 242k / 211 | 80.2 / 238k / 280 |
| nav 10 | 94.0 / 353k / 242 | 419.7 / 2.18M / 607 |
| nav 20 | 100.2 / 368k / 242 | 448.2 / 2.33M / 633 |
| nav 30 | **106.7** / 380k / 243 | **454.5** / 2.34M / 638 |
| cycle 10 | 148.9 / 531k / 317 | 877.5 / 4.13M / 1031 |
| cycle 20 | 182.6 / 740k / 340 | 1047.5 / 5.41M / 1363 |
| cycle 30 | **195.9** / 907k / 368 | **1381.1** / 7.15M / 1695 |
| +60 s idle | 184.4 / 817k / **417** | 1472.6 / 7.34M / 1716 |
| cycles OK (new tab / loaded / closed) | 30 / 30 / **30** | 30 / 30 / **1** (no Cmd+W fix before M1, so 30 tabs stayed open: not like-for-like) |
| host views / GPU surfaces | 2 / 2 at every mark | 2 / 2 |

**Answer to Atlas's Q3: yes, memory still grows at 0a13dfb4. It is about 7× better than at the pause head.**
- **Navigations:** +24.8 MB heap over 30 (about 0.8 MB per navigation; the pause head added +374 MB). M2 works.
- **Tab cycles, with every tab closed:** **+89 MB heap, +527k nodes, +125 MB RSS over 30 cycles.**
  - The per-cycle rate falls (4.2, 3.4, then 1.3 MB per cycle across the three blocks of 10), so this may be a plateau and not a linear leak. Unproven at 30 cycles.
  - Over the 60 s idle, heap fell 11.5 MB but **RSS rose 49 MB, to 417 MB**.
- E35 holds: views and surfaces stay at 2.
- **Attribution:** heap(1) classifies only about 5 MB of the growth. The largest classified items are Swift strings and URLComponents, 4,674 each. The rest is unclassified malloc blocks, which points to Rust-side allocations. **UNVERIFIED** which subsystem. The next step is a 100-cycle run to tell a plateau from a leak, plus a Rust-side allocation count (this would be a measurement row, not code).
- Atlas's separate batch-47 runs agree on direction: tab-cycle RSS 280 → 345 MB, and navigations heap 80 → 103 MB, then 119 MB after idle.

## 6. 19-site A/B (live sites, Atlas's run; I did not re-run it, live-site is OFF for us)
Batch 47 A/B, A=cand46 vs B=cand47, A,B,A,B:
- The "no batch mover" call is solid on **13 sites**: google, youtube, instagram, wikipedia, reddit, x, bing, walmart, microsoft, netflix, github, squarespace, weather. Google has 1.87 % within-A noise.
- **6 sites cannot certify anything:**
  - facebook: within-B 45.8 %
  - linkedin: within-B 76.8 %, with B2's script records 18 vs 6
  - apple: within-B 71.35 %
  - yahoo: within-A 36.9 %
  - lyft: B1 failed at 0.3 s
  - cnn: 4/4 runs timed out at 30 s, so it was never scored in batches 45, 46 or 47
- The same sites are noisy in batch 45 and the batch 47 re-run, so the noise is the live content, not the build. As a gate, it is a 13-site A/B. cnn has had no A/B data for three batches.

## 7. Windows and Linux parity at the same tree
- **Linux:**
  - Synced to the pause head 0db52779 (S15 #123, S16 #124; Castor R1, merged; 0 open PRs) [talos 433, castor 75].
  - **Not yet at 35034d6f or 0a13dfb4**: LAT14, LAT1c, H19, M1, E35 and M2 are still missing.
  - Last Linux board: 20/42 on the S11 tree (=27129415). **No Linux board at 0db52779 or later**: NOT MEASURED.
  - Talos's join-artifact lead is answered by §1: at this head macOS join_failures match Linux on the named rows.
- **Windows:**
  - Refresh #15 (macOS 27129415) and #136 (CI timeout 210) merged. Windows develop is eac36132.
  - Refresh #16 (target 35034d6f, or 0a13dfb4 per atlas-batch47) is **blocked on a two-session conflict on the Windows box**: an unknown session holds `athena/engine-sync-refresh-16` with 49 modified files [athena 563, atlas 1293].
  - Windows is **7 macOS batches behind** (41–47).
  - Last Windows nightly parity: 26/26, mean 1.12 %, on Windows' own case set [athena 561]. **There is still no Windows chrome board.**
  - The feature stack #126–#134 is waiting on Pollux, who has been silent since 20:05Z.
- **Shared-path warnings:**
  - #1003 adds a Windows arm to `Drop for WindowSurface` that was never run on Windows.
  - #1005 touches rustkit-js lib.rs/diag.rs and Cargo.lock.
  - Both land in Windows' next refresh untested there.

## 8. Ranked view of WEEK-2026-11-09.md, and where it differs from REGROUP

My ranking for the finish line ("normal multi-tab session stays responsive while another page loads or runs a long script"):

1. **LAT15 (#1006): make a loading page take input.** This is the one number that is still about 9 s (§4), and nothing landed since the pause touched it. WEEK has it as item 4. **Run it first.** It is already batch 48.
2. **T36 (#1008) + T37 before any real-window figure is used as milestone evidence.**
   - 4 of the 8 remaining FAILs are the harness's own 400 ms sleep.
   - Cmd+T and Cmd+W "passes" time a subprocess.
   - This is an **invalidated measurement**, so it changes the order: it is cheap and has to come before the milestone call.
3. **LAT17: run each classic script as soon as it and every script before it have arrived.**
   - This is not in the WEEK order. TRIAGE filed it after the freeze.
   - LAT15 does not fix it (TRIAGE and my code read agree).
   - It is the genuine i0a_nav failure, and it makes every script-heavy page late by its slowest script fetch.
   - On the milestone ("leave a loading page"), it ranks right after LAT15.
4. **Tab-cycle memory growth (§5):** about +3 MB heap per cycle with every tab closed, and RSS rising at idle. Measure it out to 100 cycles this week, and fix it next week unless it turns out linear.
5. **The script stop is done** for every shape I could build. Two small rows to BACKLOG: the 100k timer loop cap kills legitimate callbacks (§3.1 item 4), and the loop-cap log says `elapsed_ms=0`.
6. **b11 Settings item:** small and visible, so a good filler task.
7. **LAT16 (chrome hover relayout, 557 × 14.5 ms in Pete's session):** absent from WEEK. Deferred is fine unless the seat hand-test shows hover cost on the milestone.

**Where WEEK differs from REGROUP-2026-11-08 (stated plainly):**
- **Direction.** REGROUP recommended A (latency) as the lane, **plus C's two-day convergence sweep first, plus B's board rounds as a second implementer**. WEEK keeps only A.
  - The board (B) is not scheduled at all.
  - Next week's focus is WPT and CSS, not the board.
  - A8 accessibility and A5b (remove wry) have no slot.
  - C survives only as "E35 early" and "upstream only if it touches the milestone".
- **LAT10 dependency.** REGROUP said LAT15 depends on the LAT10 post-load script-cap decision. WEEK drops that dependency ("No permanent post-load script cap as a prerequisite").
- **LAT16.** REGROUP listed chrome hover relayout as the #3 felt problem. WEEK does not mention it.
- **Process.** WEEK adopts REGROUP's process (frozen plan, BACKLOG, design note before cascade or sizing code, one batch a day, a second hold triggers a scope review rather than an auto-close).
- **Open decisions.** REGROUP §4's list (B15, LAT11, A8, LAT10/LAT5, B12, T33/T34) is not resolved in WEEK. WEEK only defers B15 and LAT11.

**Does anything here change the week's order?** Two things meet Atlas's bar ("a blocker or an invalidated measurement"):
- (a) The resize and Cmd+T/W checks are invalid measurements, so T36/T37 go before any milestone verdict.
- (b) LAT17 is a genuine milestone failure that LAT15 does not cover, so it needs a slot this week rather than BACKLOG.

On memory, item 4: a normal multi-tab session adds about 3 MB of heap per tab opened and closed, and RSS keeps rising when idle. This is **not a blocker this week**, since it is 7× better than the pause. It needs a 100-cycle measurement before the week's finish line is declared, because "felt on Pete's Mac" over an hour of tabs is exactly this curve.

## 9. Still open
- Seat reads requested in Null zeuzgb #243: Handtest's multi-tab finish-line session on fixtures, and Trace's code-level root cause of the 8 FAILs + 1 NOT RUN. They fold in when they land.
- **NOT MEASURED by anyone at this head:** Pete's live 15-site exit metric; a Linux or Windows board at 0a13dfb4; resize ack vs first sized frame (I did not replicate TRIAGE); the T35 selector dump.

Raw data: `/Users/petecopeland/zg-measure/` (spin.log, nested.log, lat15.log, rw-pause-th.log, rw-head-prod.log, memhead.log, mempause.log, out/), on Pete's Mac and not pushed.
