Dev-tools lane follow-ups from the reviews of #791, #797, #799 and #802 (Atlas 10-26 14:35 (3) and 20:50 (2)). One small branch with six commits; develop e587d94a is merged in.

## What changes
- **#799 nit, parity-capture `--run-inline-scripts`** (f86f7126). The run now fails on any `Skipped` inline script except the engine's `HTML_LOAD_RUNS_INLINE_CLASSIC_ONLY` (that covers too large and an earlier engine panic). Tested with an inline script over 4 MB.
- **#797 review, Inspector** (7d28e854):
  - A navigation with nobody listening clears `held_load` and its count. **Red before:** doc 2's `load` named doc 1's `inline#1`.
  - The inserted path's unparseable label got its own name, apart from the load path's `unparseable#<index>`. This PR then removes that branch (below).
- **#802 nits, `diagnose.py`** (9ca47ce2). It uses a `TemporaryDirectory`, which is removed even on failure, and prints the stderr tail when no report is written. `site_of`: `file://` has no site, and an IPv4 host is kept whole. Unit test added.
- **#791 review pins** (dfeb141a). Stack frames from `/app.js?token=SECRET` reach the Inspector as `/app.js`. New shape tests for `console.assert` and `timeLog`. These pin behaviour that was already correct, so they were never red.
- **20:50 (2): the `unparseable-inserted#<node>` branch is removed as unreachable** (f5bd7a63).
  - `web_scripts.js` resolves an inserted script's `src` with the `URL` it captured at install, which is `web_url.rs`, the `url` crate's parser. When that throws it fires `error` and queues nothing, so the engine only ever receives an `href` that `Url::parse` accepts. A page that replaces `window.URL` doesn't change this.
  - The `Err` arm is now a `let`-`else` with a `debug_assert!`.
  - New bindings test `an_unparseable_inserted_src_never_reaches_the_engine_queue`: a bad-port `src` set both as a property and through `setAttribute`, with `window.URL` replaced, is never queued; a good `src` is queued and parses.
  - `INSPECTOR_EVENT_LOG.md` now says that such a script fires `error` and gets no `script` record.

- **20:50 (3): #791 Error subclass name, a pin** (693bc3ac). Test `a_page_defined_error_subclass_name_reaches_no_record`, run with the mirror off and on. The page uses `class SecretLeak extends Error`, and subclasses that set `this.name = 'SecretName'`. They are passed to `console.error`, rejected in a promise, and thrown uncaught from a named function. No record carries any of the page's names. The test was green the first time, so the 09:40 trace holds (`ScriptError.name` is `&'static str` from `standard_name`): no breach, no fix.

## Red before
- `held_load` reset: red before (doc 2's `load` named doc 1's script).
- `--run-inline-scripts` over-4 MB: not run red separately, because the old filter has no `Skipped` arm.
- The new unparseable pin and the #791 pins hold behaviour that was already right, so they are pins rather than red tests: the branch they cover could never run.

## Suite
`rustkit-engine --features headless --lib` at 0d2fedb6: **1098 passed / 0 failed** (6 ignored). The pin (693bc3ac) was added after that run and passes 1/1 on its own. `rustkit-bindings` `web_scripts_tests` 5/5.

## Campaign (26 cases, binary built at 693bc3ac, `--profile parity`)
**26/26, mean 1.1078%**, unchanged. Worst three: article-typography 4.79%, about 3.70%, form-controls 3.24%.

## Receipt (`scripts/receipt.py`)
candidate 693bc3ac, base e587d94a, profile parity, features headless, binary sha256 a45a202e091b0ce5805fa521a4a1dccb1f20a23922a4aa3ee6c3d6127a94818a, campaign sha256 7fd47df71b606b4a0f1e701c5fe08a4a3fc9707845c1803e625e1cd87a49c2b8, dirty_state false, rustc 1.91.0.

Not in this PR yet (20:50 (4)): Prometheus's #799 Chart.js-style report-page test, and callback errors (timers, rAF, event listeners) reaching the Inspector, with a test each. They come next on this branch.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
