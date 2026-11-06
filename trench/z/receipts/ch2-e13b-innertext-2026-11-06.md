## CH2.E13b: innerText takes `white-space`, the table breaks and a boxless `<p>` from computed style

Branch `atlas/z-ch2-e13b-innertext` @ `07e6bb8e` (red `a1aa3711`), off develop `5e87a184`. Row CH2.E13b (from #923's review). Full gates run in the batch.

**Before** (develop 5e87a184, which has CH2.E13):
- `white-space` came from the tag. The getter checked whether a `pre`/`textarea`/`listing`/`plaintext`/`xmp` was an ancestor, so:
  - a `white-space: pre` div collapsed its spaces;
  - `pre-wrap` from a class collapsed too;
  - `pre-line` dropped its line feeds;
  - a `<pre style="white-space:normal">` kept its spaces.
- The table breaks came from the tag. Only `td`/`th` got the tab and only `tr` got the line feed, so:
  - `display: table-cell` spans or divs read `ab` (Chromium `a\tb`);
  - `display: table-row` divs gave no line feed;
  - a `<td style=display:block>` still got a tab.
- A `<p>` always got its two breaks, even under `display: contents` (no box). Chromium gives that `<p>` none, but still gives a `display: inline` `<p>` two.

**After** (`crates/rustkit-bindings/src/inner_text.rs`):
- **White space.** A text node is processed by its parent's computed `white-space`. The property inherits and a text node has no style of its own. The engine already publishes `white-space` in the computed lines.
  - `pre`, `pre-wrap` and `break-spaces` keep everything.
  - `pre-line` collapses spaces and tabs and keeps each line feed. The spaces either side of a line feed go.
  - `normal` and `nowrap` collapse.
- **Table breaks.** A cell is computed `display: table-cell` and a row is `table-row`. Row groups are `table-row-group`, `table-header-group` and `table-footer-group`.
  - The tab goes after a cell that has a later cell sibling.
  - The line feed goes after a row that has a later row in its table, counting rows in later row groups.
- **`display: contents`.** Any element with it, a `<p>` included, adds no required breaks.
- **Fallback.** When the layout has no style for a node, the old tag rules still apply, as before.

**Red → green:**
- `inner_text_style_tests::inner_text_takes_white_space_and_table_breaks_from_computed_style_as_in_chrome`.
- It checks 17 pages in `tools/parity_oracle/inner_text_style2_cases.json` (sha256 `4dc056c3…d422d`). Chromium 143.0.7499.4 produced each page's `encodeURIComponent(t.innerText)` with `grid_flexible_row_log.mjs --file inner_text_style2_cases.json --write`.
- Develop gets **7/17** right; this branch gets **17/17**.
- The pages cover:
  - `white-space`: pre on a child and on the target, pre-wrap by class, pre-line, normal on a `<pre>`, nowrap, pre inherited into spans;
  - tables: table-cell spans, table-row divs, `<td>`/`<tr>` set to block;
  - `display: contents`: a div, a span holding a block, the target itself, a `<p>`, a `visibility: hidden` child inside contents;
  - a `display: inline` `<p>`.

**Narrow runs:**
- engine `inner_text` filter 3/3, which includes E13's 12 pins unchanged;
- engine `restyle_invalidation` 22/0;
- `rustkit-bindings` 478/0.

**Campaign** (`--profile parity`, base `5e87a184` parity-capture sha256 `484e7904…c734`, candidate `07e6bb8e` sha256 `07d35a44…f1fa`): 26/26, **0 moved**.

**20-site A/B** (`ab5.py`, A = develop, B = candidate, A,B,A,B at 1280×800): **no mover from this PR.** 15 sites 0.00% on every pair. **walmart** 62.95% on all four cross pairs with 0 inside each arm: arm A drew the grey skeleton page (105 script records), arm B the hydrated hero (124). Two swapped passes (A = candidate) show it's the site's variant: pass 1 had the candidate itself draw the skeleton once (105) against 124, and pass 2 was 0.00% on all pairs with 124 records everywhere. google 1.53% and yahoo 58.42% inside arm B only (noise, as in #950's run); netflix 4.26% inside both arms; cnn timed out (30 s) in both arms. Table: hub `trench/z/receipts/ch2-e13b-ab.txt`.

**Not in this PR:**
- A line feed at the very start of a `pre-line` text is handled like any other, not checked against Chromium.
- `innerText` of a `display: contents` target already matched Chromium on develop: it is rendered and reads `a\nb\nc`, not its textContent. That case is pinned here.

Toolchain: rustup stable (1.91.0), aarch64-apple-darwin. Builds go through z-cargo (lease + sccache). Host: the macOS seat. Chromium 143.0.7499.4 (pinned oracle).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
