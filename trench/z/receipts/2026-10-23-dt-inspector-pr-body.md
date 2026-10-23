## Summary

Re-cut of the parked #764 (Inspector wired to RustKit content: pick, details, console, copy) for develop as it is now, where page script runs on the content thread by default (#730, #780).

#764 had the app borrow the engine on the window thread to answer the Inspector. With the content thread on, the window has no engine to borrow, so the panel would stay empty in the shipped app. In this version every Inspector question goes over the page protocol and is answered on the page's own thread. The window never waits for the answer.

## What changed vs #764

- `PageCmd::Devtools { query: DevtoolsQuery, reply }` in `page_protocol.rs`, answered by `content_thread.rs` on the page thread. Queries: `Attach`, `DomTree { root, reveal }`, `Element`, `NodeAt`, `Highlight`, `Console { since }`. Answers: `DevtoolsAnswer`.
- `RustKitView::devtools_ask` / `devtools_eval` return a receiver. With the content thread off they are answered at once on the same thread (`submit` drains the inline endpoint), as before. If that endpoint is already borrowed, `submit` drops the command like any other, and the panel reads the closed channel as `DevtoolsAnswer::Unavailable` (`devtools_panel.rs:198`; an eval shows "the page is loading"). It does not retry by itself.
- `devtools_panel.rs` asks, then reads the answer from the live wake. A slow page delays the panel, not the window.
- The rest is #764 as reviewed: the engine query API in `devtools.rs` (hit test, element details + Copy text, DOM tree depth 6 / 3000 nodes, highlight overlay on the committed display list), the panel in `ui/inspector.html`, and View > Developer > Inspector (Cmd+Opt+I) plus the Tools sidebar button.

## Which thread runs it in the shipped app

| action | thread (content thread ON, shipped default) | thread (OFF) |
|---|---|---|
| tree, element, node-at, console, highlight | page thread, through `PageCmd::Devtools` | window thread, same call |
| panel draw, pick-mode input | window thread (chrome WKWebView) | same |

## Tests (the first two cannot be written against #764: there is no protocol path to ask)

- `content_thread::tests::the_inspector_is_answered_on_the_content_thread`: tree, element box 110x60, node-at, outline drawn into a new commit, console line, all on the page thread.
- `webview_rustkit::tests::content_thread_the_inspector_gets_the_dom_tree_and_an_element`: the app view, content thread on.
- #764's own `devtools_tests.rs`.

## Open decision (Pete's)

The console shows a value's shape, not the page's text. For example, `console.log('from the page')` shows as `<string len=13>`, because the Inspector log (`inspector.rs`, #676) records shapes on purpose. That is in the way of the dev-tools goal ("someone new names the yahoo cause in under 5 minutes"). Showing real text while the panel is open would stay in the app, but it is a privacy call, so this PR does not change it.

## Gates

Candidate `aafdac6a` (develop `6e25ea3a` merged in; one conflict per file, where both sides only added tests, kept both). Mac, load 70 to 125 (other seats building).

- **Campaign, 26 cases:** identical to develop `6e25ea3a`, case by case (0 moved). 26/26 pass.
- **All-site A/B, 20 sites, develop vs candidate, A B A B:** no mover. linkedin differs only inside the candidate arm (one run got a different page: 6 script records against 18), and the A1/B1 pair is 0.00%. microsoft, github, squarespace and cnn hit the 30 s capture limit in 2 to 4 of 4 runs, in **both** arms. On last night's quieter A/B (#780) they took 16 to 26 s; today they take 26 to 30 s. That is load, not this PR.
- **Engine, `devtools` + `content_thread`:** 39/39 (the new on-page-thread test included).
- **App (`-p hiwave-app`):** 59/60. The one failure is `a_new_load_replaces_the_one_in_progress`, a 5 s wall-clock bound that this PR does not touch. It passes when run by name (4.98 s at load 69), which is close to the bound and worth a quiet rerun.
- **Not run locally:** the full engine suite (the machine is shared this morning). CI `unit-suites` covers it.
- **Cost when off:** the console records nothing until the panel attaches. The display list is copied only while an outline is set.

## Receipt (`scripts/receipt.py`)

```json
{
 "base_sha": "6e25ea3a",
 "binary": "scratch/pc-cand-aafdac6",
 "binary_mtime_utc": "2026-10-23T13:49:15.135192Z",
 "binary_sha256": "497823eac62142f8cd86aef199e605ab333442741c3f72fd7e648dcaeefbd4bc",
 "branch": "atlas/z-dt-0910-local",
 "campaign": {
  "cases": 26,
  "failed": 0,
  "file": "scratch/camp-cand-aafdac6.json",
  "mean_diff_pct": 1.1078,
  "passed": 26,
  "sha256": "f0bc928a13e7926329b7b2930da14a0759e6872019dd003272c4db20e4c34bc1",
  "timestamp": "2026-10-23T09:50:53.389774"
 },
 "candidate_sha": "aafdac6a2f7f3c5b7c066f5537dfd41d992635db",
 "cargo": "cargo 1.91.0 (ea2d97820 2025-10-10)",
 "cargo_lock_sha256": "d43bf3f40c046d3d625a2876c81a524fcaac59b37460f330942147537a4c8cb7",
 "chrome_version": null,
 "cpu": "arm",
 "dirty_state": false,
 "effective_engine_flags": {},
 "features": "headless",
 "host": null,
 "note": "Inspector re-cut; campaign 26/26 identical vs develop 6e25ea3a; A/B 20 sites no mover",
 "os": "macOS-26.5.2-arm64-arm-64bit",
 "profile": "parity",
 "raw_runs": [
  {
   "bytes": 3079,
   "file": "scratch/ab-dt-aafdac6.txt",
   "sha256": "5b0ba0f788b561dc315007d8f9727ce5c53d3f17a1be86db42d9cd124df6cebd"
  },
  {
   "bytes": 596147,
   "file": "scratch/camp-dev-6e25ea3.json",
   "sha256": "34ce807b7ec7111c84228364046029846ebca3a4e7c6724b979e364084da4375"
  }
 ],
 "repo": "https://github.com/hiwavebrowser/hiwave-macos.git",
 "rustflags": null,
 "sccache": true,
 "target": "aarch64-apple-darwin",
 "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)",
 "utc": "2026-10-23T14:15:54.227361Z",
 "work_package": "DT"
}
```


🤖 Generated with [Claude Code](https://claude.com/claude-code)
