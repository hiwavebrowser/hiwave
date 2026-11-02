# T13c: census follow-ups, plus the T15c R1 nits

Branch `atlas/dt-t13c-census-followups` @ 900237ad, base develop afa159da. Scripts, census tool and docs only; no engine change.

## Evidence
- **Red first:** d337921d (WPT) fails 4 of 9 in `ChromiumOnAreaProbes` on their asserts over stubs. efd40994 (census) fails 11 of 64 on their asserts over stubs.
- **Green:** `cargo test -p css-census` 64/0. `test_wpt_tier1.py` + `test_no_unguarded_nullable_diff.py` 135/0 after sync. `css_property_names.test.mjs` 7/0.
- **Census, same binary, unchanged tool vs this one:** effect 131, computed 8, parse 61, unsupported 144, red 212 on both. 0 of 344 properties moved in class, red, effect or off probes. Only the order, the notes and the "Paints right, reads wrong" list change.
- **`wpt_coverage.py --no-build`:** 63 pass / 176 fail / 70 unproven / 5 skip / 35 error, n=349, the same as T15c. Negative control red. New line: `area probes in Chromium: 47 asked, 13 differ, 34 match, 0 not measured`.
- **Campaign:** 26/26, mean 1.1095%.

## What changed
**T15c nits (comment 6570795260)**
- A Chromium gap now names its question: `area probe not checked in Chromium: <why> (N)` or `small FAIL ...`. Before, a timed-out area batch printed as small FAILs.
- `last-run.json` gains `area_probe_chromium` (asked / differ / match / not_measured). The console prints the same split.
- The docstring says 13, not 11.

**Per-property prevalence**
- `docs/census/tools/css_property_prevalence.mjs` loads the top-100 list, ebay refused by host, and counts sites whose main frame authors each property in a stylesheet, `<style>` or style attribute. The output is counts only: no site names, URLs or page text.
- 68 of 99 sites loaded, Chromium 143.0.7499.4. The census reads the checked-in file and needs no network.
- `?` rows go from 326 to 0, and 6 listed properties have 0 sites.
- **The red list reorders.** Old top: `z-index`, `object-fit`, `clip-path`, `-webkit-mask-image`, `mask`, `mask-image`. New top: `display`, `transition`, `cursor`, `text-align`, `box-shadow`, `font-family`, `z-index`, `outline`, `text-decoration`, `vertical-align`, all at 68 of 68.

**Off controls.** A miss on a control more than 150 probes off now says so, e.g. `mismatch (0 probes, control 1195 off)`, and the JSON gains `control_off`. 36 properties carry it. At this head `spanned` is 1195 off and `blend` 375. `persp` is no longer off.

**`cover` at the cap.** `FLOOR_CREDIT` goes from 100 to 150. It now sits clear of the highest kept row (`cover`, 100) and the lowest demoted one (`repeat-x`, 302). No row moved. 150 is a judgement from this data, as 100 was, and the bound is slightly more lenient.

**Guard reader.** The reader now takes helpers from every crate, reads guards with extra arguments, and refuses a run on a guard on the property name it cannot turn into names. The real engine has none.

**Past the row (Atlas's #848 landing nit).** "Paints right, reads wrong" now lists any value that matches but misreads, whatever its siblings did: 95 to 109 properties.

## Limits
- **Authored is not applied.** A rule that matches nothing still counts, and a longhand set only through its shorthand is not counted under the longhand.
- **The top of the order saturates.** Common properties tie near 68 of 68, so corpus count breaks those ties. It ranks the rarer properties better than the common ones.
- **The crawl is one live pass.** A rerun will differ a little. The 31 sites not loaded are bot walls, errors and timeouts. The reader's file also holds a few non-property names from nested selectors; the census only looks up listed names.
- **The `spanned` and `blend` causes are not reduced.** `column-count` reads mismatch and `mix-blend-mode` unsupported, so those fit, but that is inference from the rows.
- **The `bg` rows stay red on a broken control** until the C14 fix; re-read them then.
- **Fresh checkout, not a bare clone.** It ran in a `new-task.sh` checkout with `--parity-capture` on a parity build made just before. The tool's own build path did not change and was not re-run.
- **The crawl has no end-to-end test.** Only the name reader and the ebay and title checks are tested.

## Receipt (`scripts/receipt.py`)
```json
{
 "base_sha": "afa159da",
 "binary_sha256": "5b85a82443ca8da2496c03628e1cdb7d2db65bf7b61d79f5ccbc82841d03283a",
 "branch": "atlas/dt-t13c-census-followups",
 "campaign": {"cases": 26, "failed": 0, "passed": 26, "mean_diff_pct": 1.1095,
  "sha256": "0760e937b7d138e7ebb0768c6a936aeaf342e2c614f94ae1205e3a9232333fa9"},
 "candidate_sha": "900237adaf0ec608e1833bd0a00f15befec400d0",
 "dirty_state": false,
 "profile": "parity",
 "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)",
 "repo": "https://github.com/hiwavebrowser/hiwave-macos.git"
}
```
The campaign ran on the parity build via a no-op `cargo` on PATH and a `target/release/parity-capture` symlink, per the 10-29 recipe; the shim was only on PATH for `parity_test.py`. Builds used `CARGO_SERIAL_WAIT=0` because the build lock was wedged (see the digest).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
