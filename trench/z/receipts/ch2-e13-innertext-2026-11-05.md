fix(bindings): innerText reads computed display and visibility (CH2.E13)

PR body, ready to open. Branch `atlas/z-ch2-e13-innertext` @ 2de87d19, base develop c959570f. Held, not opened: 16 hiwave-macos PRs were open at 13:14 ET (cap 16).

## What was wrong

`HTMLElement.innerText` (rustkit-bindings `inner_text.rs`) decided what is rendered from two things only: the UA defaults for each tag and the `hidden` attribute. It never read computed style, so it could not see author CSS. #910's check hit this: its text reader read out hidden panels. Pinned against Chromium 143.0.7499.4, develop gets 1 of 12 pages right:
- `display:none` from a class, from a `style` attribute, or from a class that script sets before the read: the hidden text is read out (`ahiddenb`, Chromium `ab`). A hidden block also adds line breaks (`a\nx\nb`).
- `visibility:hidden` and `visibility:collapse` text is read out. A `visibility:visible` child inside a hidden span should still be kept (`avb`).
- A `display:block` span does not break the line, and a `display:inline` div does.
- An element that is itself hidden, or is under a hidden ancestor, is collected as rendered text (white space collapsed) instead of returning its textContent.

## Fix
- `__rustkit_dom_info(…, 'innerText')` now forces a fresh layout first, as the other geometry reads do (Chromium flushes style for innerText too). It passes the getter a lookup into the published computed styles (`display`, `visibility` lines).
- `display: none` skips the subtree. `is_rendered` checks for it up the ancestor chain.
- A `visibility` other than `visible` drops the element's own text, line breaks, `<br>` and cell tab, but its children are still walked (the collection steps' order).
- Block-level comes from the computed `display`: block, list-item, flex, grid, table, flow-root and table-caption.
- An element with no published style falls back to the tag rules. That covers no layout yet and nodes outside the layout. With no layout at all (the bindings unit tests), the getter behaves as before.

## Commits
- b0151ab2 test (red): `inner_text_style_tests` with 12 pages from `tools/parity_oracle/inner_text_style_cases.json`. The oracle script `grid_flexible_row_log.mjs` takes an optional `"expr"` per case file; here it is `encodeURIComponent(t.innerText)`, which keeps the comparison free of escapes. develop matches 1 of 12.
- 2de87d19 fix: `inner_text.rs` and `dom.rs`.

## Receipt
- base c959570f, candidate 2de87d19
- binaries (`--profile parity`): develop sha256 fed34ea8…2929, branch sha256 7897e393…828a
- rustc 1.91.0 (f8297e351 2025-10-28); macOS 26.5.2 arm64; Petes-MacBook-Pro; load 8–14 during the runs
- oracle: Chromium 143.0.7499.4 (Playwright pin); case file sha256 e5628dec…818a
- `inner_text_style_tests`: develop 1/12, branch 12/12
- rustkit-bindings: 467/0 (the existing innerText unit tests run on the fallback)
- rustkit-engine `--lib restyle_invalidation`: 22/0. `inner_text`: 2/0, which includes the existing `inner_text_writes_are_painted_when_the_script_settles`.
- 26-case campaign: 26/26 on both arms, average 1.1%, 0 cases moved
- chrome board: 42/42 rows identical on both arms (6/42 green on each)
- Not run: the all-site A/B. Live-site work is frozen (11-04 22:20), and the batch A/B is Atlas's. This does touch scripts. Possible costs: a page that reads `innerText` after a write now pays a forced layout, capped by the per-task budget (`FORCED_LAYOUTS_PER_TASK`), as `offsetHeight` already does. A page that scrapes its own DOM now gets Chromium's text.

## Not done
- `white-space` is still read from the tag (`PRESERVE`: pre, textarea, …), not from computed style.
- Table cell tabs and row newlines are still decided by tag (`td`/`th`/`tr`), not by `display: table-cell/row`.
- `display: contents` is not pinned. If the layout publishes a style for such an element, it reads as rendered and not block-level, which is right. If it does not, the tag fallback applies (a `div` would add a line break).

R1 asked of Prometheus.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
