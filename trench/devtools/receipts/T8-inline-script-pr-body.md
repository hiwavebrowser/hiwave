# fix: load_html runs the document's inline scripts (T8)

Branch `atlas/dt-inline-script` @ 43169252 (fix 96f3e10d + test-only 43169252, on develop ff6ad36a; red test bd00fb21 below them). Draft PR to develop, to open when the PR cap allows (9 open of 8 at 2026-10-25 18:50).

## What was wrong
`ContentThread::load_html` -> `PageCmd::LoadHtml` -> `Engine::load_html_as` built the bindings and laid out, but never ran the document's `<script>` elements. The app loads New Tab / About (`about.html`) and the report page (inline Chart.js, drawn from a `DOMContentLoaded` listener) this way in RustKit content mode, so their scripts never ran. Only the parity-capture Inspector page ran its script, through an explicit `Engine::run_inline_scripts` call.

## Change (Atlas 10-25 13:05, option (a))
- `load_html_as` runs the document's inline classic scripts in document order after the first layout. Then it fires `DOMContentLoaded` (document, then window) and `load`, with `readyState` loading -> interactive -> complete, the same as the URL load path. All of this happens before `PageLoaded`.
- It matches the URL path in four ways:
  - The same `inline#n` names, counted as `fetch_page_scripts` counts them.
  - The same script budget and watchdog (`install_script_js` / `with_script_js`), loop limit, panic poisoning and 4 MB size skip.
  - The same script log and Inspector records.
  - The same layout refresh before each lifecycle step.
- A throwing script belongs to the page. It goes to the script log, not to the load's result.
- This path has no network. An external or module script is logged as `Skipped("an inline HTML load runs inline classic scripts only")`. The page's timers are left to the live loop.
- Nothing changes with JavaScript off. That covers the RustKit chrome (`javascript_enabled(false)`, untouched) and parity-capture `--html-file` without script, so the campaign and the board are unaffected.
- `Engine::run_inline_scripts` is removed, so nothing can run a page's scripts a second time.
  - The parity-capture Inspector page and `--run-inline-scripts` now read the script log, and still fail the capture on a script that throws.
  - The Inspector's `script_ms` is now the script log's elapsed time.

## Tests
Red before: these 4 tests, with the new call disabled on this branch, read 0 passed / 4 failed:
- `content_thread::tests::load_html_runs_the_documents_inline_scripts`: the red test from bd00fb21.
- `content_thread::tests::load_html_fires_domcontentloaded_and_load_after_its_scripts`: order `loading,second,dcl:interactive,load:complete`.
- `content_thread::tests::about_page_script_runs_and_sets_the_version_line`: `about.html` itself, with `hiwaveAbout.setVersion('v9.8.7')` updating `#versionBadge`.
- `inspector_page_tests::the_inspector_page_script_runs_exactly_once`: the script log is exactly `[inline#1: Ran]`, and `hiwaveInspector.selectNode` is a function.

After the fix:
- Targeted runs pass: `load_html_ about_page_script inspector_page consent_click` 34 passed, 1 ignored (iframes), and parity-capture 18/18.
- The full engine suite (`rustkit-engine --features headless --lib`) @ 43169252: 1067 passed, 5 failed, 6 ignored, 956 s. The five are the Mac localhost set (referrer x3, image_loader_routing, remote_web_fonts), which also fails on develop and is fixed on T5's branch. develop has 1064 tests; this branch adds 3 (the fourth new test replaces the old `inspector()` assertion). No new failures.
- The first suite run, on 96f3e10d, had 15 more failures, all in `shadow_tree_tests`: its helper ran each page's scripts a second time after `load_html`, so `attachShadow` threw. 43169252 makes the helper read the script log instead; shadow_tree + restyle_invalidation 49/49. Summary: `T8-suite-43169252.txt`; receipt: `T8-receipt-43169252.json`.

## Campaign
26/26, mean 1.1078% (the same as develop). Worst cases: article-typography 4.79%, about 3.70%, form-controls 3.24%. parity-capture binary sha256 `fc331f9d…`.

## Cost
No measurable cost when the page has no script, or when script is off: the traversal finds nothing and returns. When the page has script, its own script time is the cost.

## Notes for review
- Behaviour change: `parity-capture --html-file` with `--actions` already turned script on. Its inline scripts now run on load, as Chromium runs them.
- The URL path also runs timers up to the horizon and pumps network rounds. This sync path does neither (it has no runtime). Built-in pages need neither at load.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
