## CH2.B1 — the sidebar lays out 1105 px tall in an 800 px viewport

**Board row:** chrome.html's `#sidebar` and `#chromeMain` were 1105 px tall at 1280x800; Chromium 143 has 800 and 800.

**Reduced:** `html, body { height: 100% } body { display: flex }`. The body is a single-line flex **row** whose height is a percentage. The block pass resolves it (800) and hands it to the flex pass (`lib.rs` → `layout_flex_container_at_resolved_percent_height`), but only a **column** used that number, as its main size. A row reads its vertical **cross** size from style alone, finds a percentage indefinite, and sizes its line to `content.height`, which is the block pre-pass's stack of the items (800 + 18 = 818; 1100 + 18 = 1118). Every stretched or `height: 100%` item then grew past the viewport. A body with `height: 800px` was always right.

**Fix (`rustkit-layout/src/flex.rs`, +12 lines):** in a row, the resolved percentage height is the definite inner cross size (css-flexbox-1 §9.4.15). It is used at the two places that already read the grid path's `used_inner_height` for the cross axis (`has_definite_cross_size`, `definite_inner_cross`). The container's final height and the column path are unchanged.

### Red first
- `d9a14b24` test: `flex_percent_cross_tests.rs`. Four reduced shapes plus a px-height control. On develop: 4 of 4 wrong, the control passes.
- `e478871f` fix: 4 of 4 pass.

| shape (`#s` in the percentage-height body row) | develop | branch | Chromium 143 |
|---|---|---|---|
| `height:100%`, a 1100 px child | s=818 m=818 | s=800 m=800 | s=800 m=800 |
| no height (stretch) | s=1118 m=1118 | s=800 m=800 | s=800 m=800 |
| `height:100%` column, a 1100 px child | s=818, kid 818 | s=800, kid 800 | s=800, kid 800 |
| `height:100%` column, 300 px + a `flex:1; overflow:hidden` section | s=818, kids 300,518 | s=800, kids 300,500 | s=800, kids 300,500 |

**Full chrome.html** (board stub + fixture, headless 1280x800): `#sidebar` 1105 → **800**, `#chromeMain` 1105 → **800**, the resize handle 1105 → 800 (Chromium: 800/800/800). The shelf section is 132 against Chromium's 144. The 12 px comes from a separate diff: the first and last `.action-item` rows are 39 px tall in RustKit and 33 in Chromium. That is a follow-up, not this PR.

**A gap closed as a side effect:** `grid_in_flex_tests` listed `percent-height-row-is-not-touched` (a `height: 50%` item of a 400 px row: 110, Chromium 200) as a known gap. It now matches Chromium, so it is off the list.

### Targeted runs (lane: targeted crates only; the full suite is the batch's)
- `rustkit-layout`: 888 passed / 0 failed / 13 ignored
- `rustkit-engine --features headless --lib`, filters: `flex` 77/1 before the gap-list edit (the 1 was "gap now matches Chrome"), `grid_in_flex` 7/0, `height` 34/0, `percent` 39/0, `stretch` 7/0, `flex_percent_cross_tests` 2/0

### Receipt fields
- base: develop `82893eac` (merges clean onto `366fdd48`, tree `9ccbb498`); candidate: `e478871f`
- toolchain: cargo 1.91.0 (ea2d97820 2025-10-10); profile: `test` (debug), no pixel measurement in this PR, so no parity binary and no binary sha256
- host: Petes-MacBook-Pro (macOS seat); oracle: Chromium 143.0.7499.4 (`tools/parity_oracle` Playwright, deterministic launch options)
- fixtures: `flex_percent_cross_tests.rs` sha256 `0f4174d6…`; chrome.html `04057643…`; board fixture `chrome.js` `82d20d3f…` and `ipc_stub.js` `c8d0f069…` (from `atlas/ch3-a1-chrome-board`, probe only, not committed)
- not run here: the 26-case campaign and the all-site A/B. **This touches layout on every page with `html, body { height: 100% }` and a flex-row body**, so the batch's A/B should look for movers, which are expected to move toward Chromium.

R1: Prometheus. R2: any non-author.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
