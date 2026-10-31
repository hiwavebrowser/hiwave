## T13: CSS property census

One command, from a fresh checkout to the report:

    cargo run --profile parity -p css-census

It writes `docs/census/CSS_PROPERTY_CENSUS_<date>.md` and `.json`. The first report is in this PR, at develop `1de44430` against Chromium 143.0.7499.4. No engine change: the diff is the tool, one oracle script, one workspace member and the report.

### Result

344 properties, 415 values, 759 fixtures.

| class | properties |
|---|---:|
| effect | 130 |
| computed | 9 |
| parse | 51 |
| unsupported | 154 |

The red list has 213 rows: 164 with a visual miss and 49 non-visual rows that the page reads wrong. It is sorted by top-100 prevalence.

### Engine findings to route to the Z C rows (no fixes here)

1. **`position: relative` offsets do nothing.** 61 of 67 sites use relative positioning. `positioning_of` maps `Relative` to `Static` (`crates/rustkit-engine/src/lib.rs:8556`), and the box stays where it was in every form I tried: nested, top level, with text, inline span, with `z-index`. `getBoundingClientRect` reads the unmoved box too. Relative boxes with no offset are unaffected, so only sites that set an offset show it. Top of the red list.
2. **A leading `;` in a rule body drops the next declaration.** `#p{;width:200px}` reads 120px from the earlier rule; Chrome reads 200px. Seen once in a fixture, not reduced further.
3. **`getBoundingClientRect` ignores `transform`, `translate`, `rotate` and `scale`.** Each of these values has 0 off probes and a geometry miss, so the paint is right and the rect is wrong.
4. **`object-fit: cover` on an SVG image paints past the box** (seen in the frame, 456 off probes). A raster image was not tried.
5. **The background context's control is off by 916 probes.** With padding, a dashed border and a tiled gradient, the engine paints the background about 20 px below the border box. Not reduced.

### Decisions in this PR

- **Size:** 344 properties, not ~250. The row's three sources and the logical, SVG and animation longhands add up to that, and nothing was gained by cutting them.
- **Parse:** an arm in `apply_style_property` or `logical_to_physical`, or the engine's page moved when the declaration was added. The arm reader is the same rule as `scripts/declaration_census.py` and refuses an implausible arm set.
- **Effect needs a change in Chrome.** A value that changes nothing there reads `unexercised` and cannot pass (28 values). `nonvisual` properties stop at computed (50 values).
- **A probe forgives 1 px and 16 per channel, so a pixel count backs it:** the engine must change at least half as many pixels as Chrome did, or an underline it never drew would pass.
- **A property is its worst measured value.** An `unexercised` value does not cap a sibling that was measured.

### Known limits (also stated in the report)

- **Prevalence covers only 18 of the 344 properties.** The technique census asked about only those. The rest show `?` and sort by declarations in the 26-case corpus, so the order below those 18 is not top-100 prevalence. A per-property crawl of the top 100 would fix this; it is not in this row.
- **Background rows are weak.** The control's disagreement is credited as noise, and at 916 probes it can excuse a real miss (`background-size: 30px 30px` reads `match` with 915 off). Treat `bg` rows as unproven until finding 5 is fixed.
- **`transform` reads red on geometry alone.** Read the "why" column before making a C row from it.
- **One fixture per value, in one context.** A class says what happened there.

### Evidence

- **Red first:** `ee3e7158` is red against stubs, 32 of 38; 6 passed against the stubs (for example the refusal tests, which a stub's `Err` satisfies). `d74e28c6` is red for 3 more, seen before the code. Now 41/0 (`cargo test -p css-census`).
- **Sentinel:** the run stops if `background-color`, `width` or `color` cannot be told from its control. It stopped the run twice, and that is how findings 1 and 2 surfaced; both times the fixture was relying on the broken behaviour and was changed.
- **End to end:** ran in a fresh `new-task.sh` checkout with `tools/parity_oracle/node_modules` moved away, so the `npm ci` path ran too. A second run gave a byte-identical JSON. **This was not a bare `git clone`:** that needs approval on this seat, and the checkout's `target` is seeded.
- **Campaign:** 26/26, mean 1.1095%, on the same engine as develop.

## Receipt (`scripts/receipt.py`)

```json
{
 "base_sha": "1de44430",
 "binary": "target/parity/parity-capture",
 "binary_mtime_utc": "2026-10-31T04:47:10.176934Z",
 "binary_sha256": "8da93be5d8368304ecafb612c5a77d902d2e8cc3a17e475feb8a7b0be85d52f3",
 "branch": "atlas/dt-t13-css-census",
 "campaign": {
  "cases": 26,
  "failed": 0,
  "file": "parity-baseline/parity_test_results.json",
  "mean_diff_pct": 1.1095,
  "passed": 26,
  "sha256": "028b49b657d3df32d1ac161a16ec5901419789b20ed0ef9c2933d7c82de7d453",
  "timestamp": "2026-10-31T01:01:51.377424"
 },
 "candidate_sha": "cb0188c9e2f1855349572697caf9ed0f2550005c",
 "cargo": "cargo 1.91.0 (ea2d97820 2025-10-10)",
 "cargo_lock_sha256": "241df6e8a50e5a0d93f45d52e91b46ed3f39286897f689b06e8e39e7b7a1e97a",
 "chrome_version": null,
 "cpu": "arm",
 "dirty_state": false,
 "effective_engine_flags": {},
 "features": null,
 "host": null,
 "note": "tooling only: engine crates unchanged from develop 1de44430",
 "os": "macOS-26.5.2-arm64-arm-64bit",
 "profile": "parity",
 "raw_runs": [],
 "repo": "https://github.com/hiwavebrowser/hiwave-macos.git",
 "rustflags": null,
 "sccache": true,
 "target": "aarch64-apple-darwin",
 "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)",
 "utc": "2026-10-31T05:02:49.765907Z",
 "work_package": "T13"
}
```


🤖 Generated with [Claude Code](https://claude.com/claude-code)
