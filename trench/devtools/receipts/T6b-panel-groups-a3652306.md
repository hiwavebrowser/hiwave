# T6b panel grouping by document: `atlas/dt-service` @ a3652306 (on eb8bcc65)

Change: `crates/hiwave-app/src/ui/inspector.html` only. `consoleRows(entries)` (pure) puts a
divider row wherever `doc` changes and marks lines from documents before the newest one
`stale-doc` (opacity 0.55). With one document in view there are no dividers. The console's own
input and results take the `doc` of the line before them, stamped when they are added.

Test: `python3 scripts/tests/test_inspector_console_groups.py` (cuts `consoleRows` out of the
page and runs it in node; skips without node).
- after (a3652306): 4 passed
- before (eb8bcc65 panel): 0 passed / 4 failed ("consoleRows is not in inspector.html")

WebKit check (Playwright WebKit, panel HTML loaded with a stub `window.ipc`; scratch script, not
committed): two documents (4 lines) plus one `addConsoleResult` render as

    console-doc-divider          | Document 1 (earlier page) | opacity=1
    console-entry info stale-doc | Navigated to https://a.test/ | opacity=0.55
    console-entry log stale-doc  | first page says hi | opacity=0.55
    console-doc-divider          | Document 2 | opacity=1
    console-entry info           | Navigated to https://b.test/ | opacity=1
    console-entry error          | second page error | opacity=1
    console-entry result         | 42 | opacity=1

Not run: no Rust tests and no campaign. The change is panel HTML only (`include_str!`), and
parity-capture never loads this panel.
