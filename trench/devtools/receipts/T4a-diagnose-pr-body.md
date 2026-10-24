Dev-tools lane, package T4 (part a): **`parity-capture --report` / `--report-text`**, page state and a ranked "most likely cause" list. Branch `atlas/dt-diagnose` @ add3cc85 (3 commits on develop ff6ad36a). Design note: `trench/devtools/T4-design.md` on `atlas/z`.

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
