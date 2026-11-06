# Windows sync brief — 2026-11-06 (Atlas)

Pete 09:50 ET: Windows workers coming back online to catch the Windows baseline up.
This is what has moved on hiwave-macos since the last Windows sync and what to watch.

## The delta
- Last Windows sync: hiwave-windows PR #114 (2026-10-09) from hiwave-macos develop `f54103d9`.
- Target: hiwave-macos develop `95691f85` (tree `f77ab126`), the last batch-tested tree.
  Sync to a batch-tested develop commit (the hub header names each one), never to
  develop mid-batch.
- `f54103d9..95691f85`: 1,582 commits, 465 merges; `crates/` 342 files, +132k/-7.5k lines;
  `docs/ scripts/ tools/ tests/` 172 files, +47k lines.
- Share by crate: rustkit-engine 50%, rustkit-bindings 17%, rustkit-layout 5%,
  hiwave-app 5%, rustkit-js 4%, rustkit-css 3%, viewhost/renderer 2.4% each.
- New crate: `hiwave-shield-intercept`.

## Things that will bite
1. **History rewrite on 11-05.** A batch-24 landing merge swept 452 `scratch/` files
   onto develop; they were dropped (#933/#934) and the public history was then
   purged with git-filter-repo. `f54103d9` is still an ancestor of develop (the
   purge touched only 11-05 commits), so vendoring by commit still works. Any
   clone of hiwave-macos fetched between 11-05 ~19:00 ET and the purge must be
   re-cloned or hard-reset to the new `origin/develop`; do not merge old objects back.
2. **Cargo features.** `webview-fallback` is gone; `test-hooks` is new (release
   builds that the real-window driver probes use `--features rustkit,test-hooks`,
   run with `HIWAVE_TEST_HOOKS=1`). `headless` on rustkit-engine is the test
   feature for the engine suites.
3. **The RustKit chrome is the default** (#939, 11-06): the browser UI is a RustKit
   document on its own UI thread (`HIWAVE_RUSTKIT_CHROME`, `=0` is the escape
   hatch back to the WebKit chrome; alpha route `HIWAVE_RUSTKIT_CHROME_ALPHA`).
   This lives in hiwave-app/rustkit-viewhost and is macOS-hosted; Windows keeps
   its native shell + WebView2 chrome unless it hosts the chrome page itself.
   The chrome page (`chrome.html`, `inspector.html`, settings) is platform-neutral.
4. **Content thread + net runtime** in hiwave-app (`HIWAVE_CONTENT_THREAD`,
   `HIWAVE_NET_RUNTIME`, `HIWAVE_NET_WORKERS`, `HIWAVE_CONTENT_STACK_MB`): the
   page runs off the main thread with a typed bridge. The Windows "live page
   process" adaptation from #114 predates this; expect the four adapted files to
   need re-adapting rather than replaying.
5. **Engine behaviour changes a baseline will feel** (all Chromium-143-pinned):
   paint-only animation frames (no relayout), hover/focus short restyle path,
   scoped `:has()`, clean-tree geometry reads don't force layout, SVG `<use>`
   index, stylesheet cache (`RUSTKIT_SHEET_CACHE`), `:focus`/`:focus-visible` in
   the cascade (#954, pending), default focus ring now Chromium's, clicks focus
   buttons/links, Tab navigation. Expect parity pixel means to move; compare
   against Chromium 143 captures, not against the 10-09 Windows baseline.
6. **Log format.** Per-task `forced_layouts=N ms=X cause=…` and relayout summary
   lines are new; `tools/latency/baseline_from_logs.py` reads them.

## Gate recipe (what macOS runs before landing; mirror it on Windows)
`cargo check -p rustkit-engine --features headless` and `-p hiwave-app --features rustkit`,
then suites: engine headless `--lib`, engine `--lib`, layout, text, bindings (whole
crate), dom, css, canvas, svg, renderer, compositor, viewhost (no `--lib`), shell, app,
`cargo test --workspace --no-run`; release builds plain / `rustkit,test-hooks` /
parity-capture; `scripts/chrome_board.py` (42 rows); 26-case campaign.
Known: `computed_read_tests::r1_cases` exceeds 120 s under load and times out the other
GPU tests; run it alone. Full rules: `~/Repos/.worktrees/agent-briefs/common.md`.

## Process
- PRs against hiwave-macos follow the land law: draft, independent R1 comment, Atlas
  batch-lands. Windows-only adaptations stay in hiwave-windows.
- Bugs found in shared crates: file on hiwave-macos with a reduced page and the
  Chromium 143 pin, as #641–#644 were.
- Hand-offs ride the null exchange, not Pete's clipboard.
