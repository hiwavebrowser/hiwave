## #788 follow-ups: observable adoptedStyleSheets, disabled/media republish, O(n) adopters

Atlas 10-26 10:50 note, branch `atlas/z-adopted-followups`, off develop `e1093aad`.

- **`adoptedStyleSheets` is an ObservableArray** (CSSOM §6.3).
  - One Proxy-backed list per document/shadow root, made on the first read. A Lit root that only assigns gets no proxy.
  - `push`, `splice` and `length = 0` re-link and republish. Index writes are validated (`TypeError` for a non-sheet, `NotAllowedError` for a non-constructed one).
  - Assignment replaces the contents and keeps the same object, as in Chrome.
- **`disabled`** is an accessor that republishes on change.
- **`media`**: a constructed sheet's `media.mediaText` setter republishes. A sheet with media publishes its rules inside `@media <list> { … }`, so `{ media: 'print' }` no longer applies on screen.
- **Adopters**: per sheet they are a `Set` (O(1) add/remove; was `indexOf` on an array, O(n²) over n roots). Roots are still held strongly while they adopt a sheet: there is no WeakRef path. This is follow-up item (1) only in part.

Commits:
- `eb695ea4` red: push/splice/length and disabled/media never republish. The many-roots case (50 shadow roots; insertRule/replaceSync/push) already passed and stays as a guard.
- `723856d2` the fix.
- `c4117b38` lazy proxy + array links.

Gates (base develop `e1093aad`, candidate `c4117b38`, `--profile parity`, macOS seat, load 11-13):
- rustkit-bindings 386/386; rustkit-engine adopted 3/3, shadow 39/39.
- Campaign 26/26, **0 cases moved** vs develop (candidate binary sha256 `e032d558…`, develop `9262790c…`).
- 20-site A/B (A,B,A,B): **no mover**. google, linkedin and bing vary as much within an arm as across arms (served variants). lyft: the second capture of each A,B,A,B pass fails in 0.3 s on whichever binary is in that slot. With the arms swapped it hit develop, so it is the site refusing a quick repeat. Every lyft frame that loaded is identical across arms (0.00%).
- 10,000 shadow roots adopting one sheet, then one `replaceSync` (local page, 2-3 runs each):

| | adopt loop | republish to 10k | max RSS |
|---|---|---|---|
| develop | 2025-2035 ms | 62 ms | 139-140 MB |
| candidate | 373-374 ms | 73-76 ms | 145-148 MB |

Asking Prometheus for R1.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
