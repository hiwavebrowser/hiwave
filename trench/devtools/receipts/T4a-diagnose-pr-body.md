Dev-tools lane, package T4: **`diagnose`**. `parity-capture --report` / `--report-text` (page state, then ranked causes from the layout and the event log) and `scripts/diagnose.py <url>`. Branch `atlas/dt-diagnose` @ c7ee3505 (11 commits on develop ff6ad36a: T4a 88d786fe..add3cc85, T4b 18576572, T4c e271b032, T4d 14b125f8..c7ee3505). Design note: `trench/devtools/T4-design.md` on `atlas/z`.

## T4d: R4 and R8 read the timeline, not single records (14b125f8, 9c2a2e80, 8c84cf16)
A `script` record is written when its script ends, so it ran over `[t - ran_ms, t]` and waited `waited_ms` before that. The rules now use those spans:
- **R4, queued is not starved (14b125f8).** Other scripts' runs during a wait are subtracted. R4 fires only on 3 s or more of idle wait, and says how much was spent behind running scripts.
- **R4, the load's script phase (9c2a2e80).** The yahoo read with LW + T3 showed that no page script ran until 5.8 s, parser ones included. The async chunks' bodies were in by 1.7 s, and scripts started after first layout (4.5 s) and the last image response (5.8 s). The old rule printed 30 "starved" async lines for this. Now it prints one line: `no page script ran until t=5.8 s: N script body(ies) had arrived 3.0 s or more before (first at t=1.6 s); first layout at t=4.9 s; last answer before it: image at t=5.7 s`. Only the wait after the first script ran is checked for a missed turn. This replaces the earlier note that the async lines were "behind the parser scripts": the parser scripts waited too.
- **R8 (14b125f8, 8c84cf16).**
  - Times are sorted, so out-of-order records no longer give overlapping duplicate gaps.
  - A running script's span is not silence. The wording is now "no script ran", not "no script ended".
  - Silence after load counts when a script body is in and waiting to run across the gap (the design note's "or requests are open"). In one yahoo run, nine inserted chunks were in at 11.3 s and no record of any kind came until 15.4 s.
- Red before (run: the three new tests put onto e271b032's `report.rs`): 3 of 3 fail, 6 old tests pass.
  - queued-not-starved: the old code also names `queued.js` (waited 3.9 s, all of it behind p1) and prints two overlapping R8 gaps, 6.1 s each, from 4.9 s and from 5.0 s.
  - script phase: the old code prints `async script a.js … waited 4.2 s for a turn`, where no script had run yet.
  - silence after load: the old code has no R8 line.
- **R5, the page's own site first (5ff0d770, 21f0cab3).** This is the design note's rule, which the code had not followed. An error whose script shares the navigation's site (the last two host labels) reads `the page's own script: …` and ranks after R1/R2/R10/R9, before R4. The line also counts the fetch/XHR to the page's exact host after the error: `; then 0 fetch/XHR to www.yahoo.com`. It counts by host, not site, because yahoo's ad and analytics hosts share the site.
  - Pinned Chromium, same User-Agent, 25 s: document 5436 px; 22 fetches to `www.yahoo.com` (Next route prefetches) and 12 to `nexus-gateway-prod.media.yahoo.com`.
  - RustKit: 2366 px, and none to either host.
- **R5, caught and logged errors (c7ee3505).** A `console.error` record with an `error_stack` is grouped by the frame that threw: `logged TypeError thrown in <url:line:col>`.
- **R10, new (c7ee3505).** The first viewport has no text and no image. R9 needs content above the empty band, so a page blank from the top fired nothing.
- Tests: parity-capture 34/34 (6 new; the benji test gained a parser script so its wait falls after scripts began).
- Campaign 26/26, mean 1.1078%. `binary_sha256` d81581e81ab5cd8fde2f157d6439096ff31909e196182328f900184a3b9cde25, campaign sha256 a3b34376cf9b2ee3c77c2dd01f4fac576c5875ceab2e689e234bd0da81237b7c, candidate c7ee3505, dirty_state false, utc 2026-10-24T11:07:27Z. Same as at 8c84cf16 (1.1078%).
- cnn at c7ee3505 (develop engine): unchanged at the top, `[R1] scroll locked (body overflow-y:hidden) by overlay: fixed body:nth-child(2) > div:nth-child(7) (z 999999) covers 100% of the viewport`. Nothing new fires. The fave bundle is on `cnn.io`, so it is correctly not ranked as cnn.com's own script.

### yahoo, LW + T3 + T4d merged locally (not pushed), 33-36 s wall clock per run
```
  1. [R4] no page script ran until t=5.7 s: 7 script body(ies) had arrived 3.0 s or more before (first at t=1.6 s); first layout at t=4.9 s; last answer before it: image at t=5.7 s
  2. [R4] inserted script …/chunks/67222-….js arrived in 1853 ms and waited 5.4 s for a turn (1.2 s of it behind other scripts running)
  …
  5. [R5] uncaught SyntaxError in https://www.yahoo.com/_nca/_next/static/chunks/7730-4e3ddf231f766d70.js:1:6278 (x2)
```
- With LW merged, benji's 24.5 s wait and the 21 open script requests are gone.
- Line 1 is stable over three runs: the first script ran at 5.8, 5.7 and 4.8 s.
- Inserted-script waits of 4 to 5 s showed in two of the three runs and not in the other. They were taken at load average 14 to 16 (eight unrelated python processes at 100% CPU). Do not read them as an engine fact until a quiet run repeats them.
- Document 2366 to 2390 px tall in all three runs: the page never grows a feed below the skeleton. With 21f0cab3, R5 ranks first: `the page's own script: uncaught SyntaxError in …/7730-….js:1:6278 (x2); then 0 fetch/XHR to www.yahoo.com`.

### What chunk 7730's SyntaxError is (#777)
Found by reading the report's own lines, then a local check (the error text is kept locally only):
- 7730:1:6278 is `document.head.appendChild(u)` in Next's `self.__next_s` loader (`beforeInteractive` scripts). Inline entries get `u.innerHTML = r.children`.
- The messages: `expected token ';', got ':' in for statement at line 1, col 808` and `… got ')' … col 395`.
- Repro (lane tool `tools/nexts_bisect.py`): each of the page's four inline `__next_s` scripts runs clean as a parser script. Inserted through `innerHTML`, as Next does, two fail with exactly these messages: `cmpstub` col 808 and `ad-shield-container` col 395. Col 395 is `…o<r.length;…`, so the text is parsed as HTML.
- With #777 (`atlas/innerhtml-rawtext` @ 32f2c2f1) merged into the stack, both pass.

### yahoo, LW + T3 + T4d + #777 merged locally (32 s wall clock)
```
diagnose https://www.yahoo.com/  viewport 1280x800  document 800px tall  77 elements
  1. [R10] the first viewport has no text and no image (77 elements, document 800px tall)
  2. [R5] the page's own script: logged TypeError thrown in …/chunks/7730-….js:1:6198; then 0 fetch/XHR to www.yahoo.com
  3. [R5] the page's own script: logged TypeError thrown in …/chunks/webpack-….js:1:13395; then 0 fetch/XHR to www.yahoo.com
  4. [R4] no page script ran until t=5.0 s: …
```
- #777 removes the SyntaxErrors, and the page then goes blank. No inserted script runs after load (no benji, no taboola). Two TypeErrors, `cannot convert 'null' or 'undefined' to object`, are caught and logged, and React's error boundary takes the page.
- Before c7ee3505 the report's only line here was R4.
- Both throw sites assign `onerror` on a freshly made `<script>`:
  - 7730:1:6198 `u.onerror=n`, just after `u.onload=()=>e()`;
  - webpack:1:13395 `b.onerror=i.bind(null,b.onerror)`.
- A top-level `createElement('script'); s.onload=…; s.onerror=…` does not throw. The trigger is in the context (a timer turn, inside a promise executor, or page state). Not chased further: this is #777's next step, not the lane's.

## T4b: event-log rules (18576572)
`--report` now collects the load's Inspector records and adds, after the layout causes:
- **R4**: an `inserted` or `async` script that waited 3 s or more between its body arriving and running; script requests still open when the capture ended.
- **R3**: scripts that never finished (`nomodule` excluded).
- **R6**: shield blocks first (T2's `blocked_by`), then other failures. Scripts and stylesheets come first; cancels are left out.
- **R5**: uncaught errors, grouped by name and place.
- **R7**: `load` 5 s or more after `DOMContentLoaded`, with T3's `held_by`.
- **R8**: a stretch of 3 s or more with no record before the load finished (T4d: or while a script body waits to run).

Fields are read by name from the JSON records. A build without T2's or T3's records runs the rest and lists the skipped rules under "Not checked" (on develop: R3, R4, R6's attribution, R7). Tests are synthetic records taken from the yahoo and cnn runs.

## T4c: `scripts/diagnose.py <url> [--keep DIR] [--shield] [--live-ms N]` (e271b032)
Runs parity-capture headless live with `--event-log --report --report-text` and prints the report. It does not build.

## cnn with T4b (develop engine, so no T3 records)
```
  1. [R1] scroll locked (body overflow-y:hidden) by overlay: fixed body:nth-child(2) > div:nth-child(7) (z 999999) covers 100% of the viewport
  2. [R5] uncaught TypeError in https://registry.api.cnn.io/bundles/fave/latest-4.x/js:1:75470
  3. [R5] uncaught TypeError (unhandled rejection) in event:load
  4. [R8] event log silent 6.0 s from t=12.2 s before the load finished: no script ended, no request moved
Not checked: R3, R4 (T3); R6 shield list/rule (T2); R7 (T3)
```

## yahoo with T3 merged locally (not pushed; what the exit metric will read once T3 lands)
```
  1. [R4] inserted script https://s.yimg.com/du/benji/benji-2.3.489.js arrived in 192 ms and waited 24.5 s for a turn
  2. [R4] async script …/chunks/23772-….js arrived in 182 ms and waited 3.2 s for a turn
  3. [R4] async script …/chunks/app/global-error-….js arrived in 222 ms and waited 3.2 s for a turn
  4. [R4] 21 script request(s) still open when the capture ended, first https://securepubads.g.doubleclick.net/tag/js/gpt.js at t=31.5 s
  5. [R5] uncaught SyntaxError in https://www.yahoo.com/_nca/_next/static/chunks/7730-4e3ddf231f766d70.js:1:6278 (x2)
```
- Line 1 and line 4 are the missing live wake that `atlas/dt-live-wake` (LW) fixes. Inserted scripts run only on the last turn.
- Line 5 is #777's chunk 7730, now a SyntaxError where #777 saw a TypeError.
- The `async` lines name scripts that waited behind the parser scripts (the engine runs async scripts in document order after the deferred ones). That is not turn starvation. A threshold or wording tweak may be wanted.

## T4b receipt (binary at 18576572; e271b032 adds only the Python script)
Campaign 26/26, mean 1.1078%. `binary_sha256` fa59637b928648c7f298fbea569f9d6c95d001ab6102fbccae67807d34f43b3f, campaign sha256 523f51261fad4eb2df18e8ba467badd7a4fc1b817f3b387d11a04adf635aa70f, dirty_state false, utc 2026-10-24T05:43:48Z. parity-capture tests 28/28.

---
The T4a sections below are kept as they were written.

## What it does
At the end of a capture, after any actions and the final render, from the element diagnostics of the final layout (`all_element_diagnostics`, read-only, up to 20 000 elements) and the element hit at the viewport's centre:
- **Facts:**
  - `html`/`body` `overflow-y` and `position`;
  - positioned boxes covering 30% or more of the viewport (outermost only, largest first, z-index, and whether they take the centre);
  - text-holding elements and images per band of one viewport height.
- **Ranked causes:**
  - **R1** scroll locked: html/body `overflow-y:hidden` or `position:fixed` while the document is taller than the viewport. It names the overlay that takes the centre, else the largest covering box, else the largest fixed box on screen.
  - **R2** an overlay of 50% or more over the centre.
  - **R9** an empty band wholly inside the document, below content.
- **Not checked:** the event-log rules (R3 to R8: scripts, errors, requests, load holds, silent gaps) are T4b. The report says so instead of leaving them out.
- `html`/`body` are never covering or fixed boxes. A consent script often makes the body `position:fixed`: that is the lock, and the body's content is still the page's. An element with no id or class is named by its structural selector's last two steps; selectors are capped at 64 characters.
- The text and JSON have no page text and no query strings. Selectors do carry page id and class names (question 2 in the design note).

## Red before
The four report tests fail on develop at argument parsing (`--report` does not exist). This was not run as a separate red build: the flag is new.

## Tests
parity-capture 22/22, 4 new:
- `a_fixed_dialog_over_a_locked_body_is_the_first_cause`
- `a_fixed_body_is_the_lock_and_the_largest_fixed_box_is_named` (the cnn pattern)
- `an_empty_viewport_band_below_content_is_r9`
- `a_short_plain_page_fires_no_rule_and_says_what_it_did_not_check`

The engine is untouched.

## Acceptance: cnn (headless live, 25 s)
```
diagnose https://www.cnn.com/  viewport 1280x800  document 27242px tall  4419 elements
Most likely:
  1. [R1] scroll locked (body overflow-y:hidden) by overlay: fixed body:nth-child(2) > div:nth-child(7) (z 999999) covers 100% of the viewport
Facts:
  body: overflow-y hidden, position fixed
  covering: fixed body:nth-child(2) > div:nth-child(7) z 999999 covers 100%, takes the centre
  covering: sticky header.header__wrapper-outer z 9998 covers 39.5%
```
The first live run named the body itself as the overlay and counted no content. That is fixed in c974d724, and the test pins it.

## Yahoo (exit metric): no rule fires, as expected for T4a
The document is 2378 px tall. The bands at 800 and 1600 hold text and images, so the grey feed skeleton is not an empty band, and nothing covers the page. Layout facts alone do not explain the blank feed. The lead is in the event log: T3 shows the ad loader `benji` waiting 24.5 s for a turn (the LW live-wake bug). That is T4b's R4.

## Cost
Nothing unless `--report`/`--report-text` is given. With it, one whole-page diagnostics dump at the end of the run. Its time was not measured separately: the cnn run took 44.3 s with the report and 44.5 s without it (T3's run), which is within run-to-run noise.

## Campaign (26 cases, binary built at add3cc85, `--profile parity`)
Passed 26/26, mean 1.1078%, the same as develop.

## Receipt (`scripts/receipt.py`)
```json
{"base_sha": "ff6ad36a", "binary_sha256": "0d15872f4a8bdec27be047b7e983f2b01458d524ea9498c380ddcf07222406e4",
 "campaign": {"cases": 26, "failed": 0, "passed": 26, "mean_diff_pct": 1.1078,
              "file": "scratch/camp-t4a-add3cc85.json",
              "sha256": "9b97f2c810287a33e2c184b1d1927595b6200999eb1438bdbb885e9c0c3acabf"},
 "candidate_sha": "add3cc8517f55a39be578fee0bd2ed82ea151da6",
 "cargo_lock_sha256": "d43bf3f40c046d3d625a2876c81a524fcaac59b37460f330942147537a4c8cb7",
 "dirty_state": false, "profile": "parity", "os": "macOS-26.5.2-arm64-arm-64bit",
 "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)", "utc": "2026-10-24T05:35:33Z",
 "work_package": "T4a-page-report"}
```

Overlap: `crates/parity-capture/src/main.rs` (new Args fields, a call at the end of `write_diagnostics`, tests). #792 adds `--shield` to the same Args struct: adjacent hunks.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
