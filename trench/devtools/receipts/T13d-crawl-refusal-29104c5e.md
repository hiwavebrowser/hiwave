## T13d: census crawl refusal follow-ups (#860 R1 delta 2, comment 6594076568)

Tooling only, CSS week. No engine change, no recrawl, no live loads: every browser test maps every host to a local server, the way the R1 did.

**Branch** `atlas/dt-t13d-crawl-refusal` @ 29104c5e, base develop 6ef43673.

### What changed
1. **Drops counted on every path** (R1 delta-2 nit 1). The per-site visit moved, unchanged, into `docs/census/tools/prevalence_visit.mjs` (commit d0d013c4) so it can be tested. Before the fix, two kinds of site read as `failed` and were missing from "sites dropped for a refused host": a page that redirects into a refused host (the load fails, so the catch path returned early), and a 401/403/429/5xx or challenge page that asked for one. Now `visitSite` decides `dropped` from the watch on every path.
2. **Watched for the page's whole life** (nit 2). The `touched` check used to run once, right after the CSS read. Now the page stays open 500 ms past the read, the context closes, and the check runs only after that, so every request event the page raised before the crawl left is counted. A request the page would make after the close never happens.
3. **Known list pinned to Chromium** (delta-1 finding 3). `css_known_properties.test.mjs` reads the property list of the Playwright Chromium in `tools/parity_oracle` on a blank page (no network), using the same `KNOWN_PROPERTIES` expression the crawl writes the list with (now exported from `css_property_names.mjs`). The test fails on any committed name that Chromium does not know. It also checks the list is sorted with no duplicates, and that the read is not empty.
4. **One command** (nit 4). `cargo test -p css-census` now also runs `node --test docs/census/tools/*.test.mjs` (`tests/node_tools.rs`), and the README documents it. The test fails if any of the four node test files is missing.

### Red first
- **cdb02900** (tests on the refactor, before the fix): `node --test` 2 pass / 4 fail. These failed: *a page that redirects into a refused host is dropped, not failed* (old: `failed`), *a blocked-status page that asked for a refused host is dropped* (old: `failed`), *a refused request made while the crawl reads the page drops the site* (old: `loaded`, red on 3 of 3 runs), and the known-list file (no `KNOWN_PROPERTIES` yet). Green on the pre-fix code: the clean control page, and the stylesheet redirect, which was already caught and is kept as a pin.
- **Known-list mutation:** `xmadeup-card` added to both `css_known_properties.json` and the prevalence file. The old guard (`css_property_names.test.mjs`, 13 tests) passes, which is the gap. The new test fails: `actual: [ 'xmadeup-card' ]`. Files restored afterwards.
- **Cargo wrapper mutation:** with the pre-fix `prevalence_visit.mjs` checked out, `cargo test -p css-census --test node_tools` gives FAILED (node 22 pass / 3 fail). Restored afterwards.

### Green at 29104c5e
- `node --test docs/census/tools/*.test.mjs`: 25 pass / 0 fail. The local server saw no refused host.
- `cargo test -p css-census` (z-cargo): generator 64/0, node_tools 1/0.
- Campaign 26/26, mean 1.1095%, identical to T13c (no engine change).

### Limits
- The during-read case fires its request 100 ms after the crawl's own `querySelectorAll`. A request issued later than 500 ms after the read is not made at all, because the page is closed first. That counts as "before the crawl leaves it", not as a check of the page's later life.
- The known-list check uses the installed Playwright Chromium. If that Chromium is upgraded and drops a property, the test fails until the list is regenerated. That is the intended direction: it fails closed.
- The 11-03 crawl in the repo was not rerun (the row says do not recrawl). Its "sites dropped" figure is still the old count.

### Receipt (`scripts/receipt.py`)
```json
{
 "base_sha": "6ef43673",
 "binary_sha256": "edac7893471a0a6b3ba03dff80b95b311b1ad63b1ba083019ce8e5e258f9345d",
 "branch": "atlas/dt-t13d-crawl-refusal",
 "campaign": {"cases": 26, "failed": 0, "passed": 26, "mean_diff_pct": 1.1095,
  "sha256": "05494e04dadde89e513b6b6518e966ab4422213dbdb272344906323693ecd9a9"},
 "candidate_sha": "29104c5ef9080d05cbf51640bbb93e38ce91cdfc",
 "dirty_state": false,
 "profile": "parity",
 "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)",
 "repo": "https://github.com/hiwavebrowser/hiwave-macos.git"
}
```
The binary was built by z-cargo `--profile parity` at 539c1b80; 29104c5e changes only docs and one comment. For the campaign, `parity_test.py` ran with a no-op `cargo` first on PATH and `target/release/parity-capture` linked to the parity build (the 10-29 recipe). The shim was on PATH only for that run.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
