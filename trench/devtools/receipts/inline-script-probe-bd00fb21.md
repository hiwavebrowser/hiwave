# Inline `<script>` under `load_html`: a real engine gap. Red test only, no fix.

Branch `atlas/dt-inline-script` @ bd00fb21 (on develop ff6ad36a). No PR.

Finding: `ContentThread::load_html` -> `PageCmd::LoadHtml` -> `Engine::load_html_as`
(rustkit-engine/src/lib.rs, ~7164) parses, builds the JS bindings, lays out and fires
PageLoaded, but never executes the document's `<script>` elements. Only the Inspector page
path (parity-capture `render_inspector`) runs them, by calling `Engine::run_inline_scripts`
(inspector_page.rs:197) after `load_html`.

So this is not the test page's setup: `EngineBuilder::new()` has `javascript_enabled: true`
by default, and the bindings exist (an `eval` afterwards works).

Shipped paths affected (hiwave-app, RustKit content mode, content thread):
- `load_new_tab` / `load_about_page` -> `content.load_html(ABOUT_HTML)`: about.html's one
  inline script (asks the shell for the version over `window.ipc`) never runs.
- `load_report_page` -> `content.load_html(REPORT_HTML + inline Chart.js)`: the report's
  inline scripts, Chart.js included, never run.
- Not affected today: `webview_rustkit_chrome.rs` also uses `Engine::load_html`, but it builds
  its engine with `.javascript_enabled(false)` ("No JS for now"). Once Phase X turns on script
  for the RustKit chrome, it will hit this gap.

Red test: `content_thread::tests::load_html_runs_the_documents_inline_scripts`

    python3 z-cargo.py <wt> test -p rustkit-engine --features headless --lib load_html_runs_the_documents_inline_scripts
    test content_thread::tests::load_html_runs_the_documents_inline_scripts ... FAILED
    the inline script did not run: String("before")
    test result: FAILED. 0 passed; 1 failed; 0 ignored; 0 measured; 1074 filtered out

Fix options, for whoever takes it (not done here):
(a) Run inline scripts in document order inside `load_html_as`, as the URL load path does.
(b) Call `run_inline_scripts` from `PageCmd::LoadHtml` only.
The parity-capture Inspector page would then run its script twice under (a) unless its explicit
call is dropped.
