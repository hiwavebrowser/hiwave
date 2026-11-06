CH2.E17 (Z lane): `<style media>` and `<style>.sheet.disabled` were no-ops. Found in #942's review. `<style media="print">` applied on screen, and `document.styleSheets[i].disabled = true` kept the sheet applying.

**Red first:** f9b44a6b adds `crates/rustkit-engine/src/style_media_disabled_tests.rs`, 7 tests and 25 pins, every value from Chromium 143.0.7499.4 on the same markup at 800×600. On develop 95691f85, 6 of the 7 tests fail. The one that passes is the `<style disabled>` control, which Chromium also applies.

**Fix (6afc63d2):**
- **`media`:** a `<style media>` element's text goes into the sheet as `@media <list> { … }`, after `media_query_list_serialize`.
  - The cascade's existing `Rule::applies_at` evaluates the list as the outermost condition, so it follows a resize.
  - `media=""` applies.
  - An invalid list (`foo bar`) or an unknown media type (`tv`) matches nothing, as in Chromium.
  - An inner `@media screen` inside `media=print` stays off.
  - The same helper covers `<style>` in shadow trees.
  - The engine has no `@import`, so wrapping the text changes nothing else. The sheet cache keys on the wrapped text.
- **`sheet.disabled`:** on a `<style>`'s sheet the flag goes to the engine through a new host function (`__rustkit_dom_set_sheet_disabled`), stored per document with the text the sheet had at that moment. The engine skips the sheet while the text is unchanged.
  - A CSSOM edit (`insertRule`) re-sends the flag for the new text, so the sheet stays disabled (Chromium: 10×0).
  - New text from `textContent` or an appended Text node makes a new, enabled sheet. This is Chromium's "update a style block": `e.sheet.disabled` reads `false`, and the new rules apply.
  - Only a disabled sheet is replaced on a text change, so an enabled sheet keeps its object identity as before.

**Pins, before → after:** 6/7 tests failing → 7/7 passing. Values:
- media: print 10, screen 20, all 20, "" 20, (min-width:700px) 20, (min-width:900px) 10, "print, screen" 20, "foo bar" 10, tv 10, SCREEN 20, "not print" 20.
- Inner rule 10. Set or removed by script: 10 / 20. Resize 800→400 with (max-width:500px): 10 → 20.
- disabled: 10 via `.sheet` and via `styleSheets[1]`; 20 after re-enable; 10 after `insertRule`; 30 after new text; 20×5 after an appended Text node.

**Known gaps (not pinned; Chromium differs):**
- (1) Removing a disabled `<style>` and inserting it again keeps it disabled. Chromium makes a new sheet.
- (2) `<link rel=stylesheet>`: neither `.sheet.disabled` nor `media` is honoured yet.
- (3) `disabled` on a `<style>` inside a shadow root is not honoured. Its `media` is.

**Gates at 6afc63d2:**
- Narrow runs, `--test-threads=1`, headless: `style_media_disabled_tests adopted_sheets_tests sheet_reuse_tests shadow_tree` 47 passed / 0 failed.
- 26-case campaign: 26/26, 0 moved.
- All-site A/B vs develop 95691f85 (20 sites, A,B,A,B): no mover from this change.
  - google read 1.53% on all four cross pairs and 0.00% within each arm. The frames differ in Google's button row: classic buttons vs the pill row ("Create images", "Brainstorm", …).
  - A swapped re-run (candidate as arm A) gave 1.53% within EACH arm and 0.01% on two cross pairs. Both binaries drew both variants, so it is Google's page variant.
  - facebook (45.83% within B) and linkedin (76.80% within both) differ inside an arm: site variants.
  - github lost one B capture to the 30 s limit. cnn hit the 30 s limit on all four captures (both arms).
  - The other 14 sites read 0.00% everywhere.
- Crate suites and headless suite: layout 897/0, bindings 478/0, engine lib 740/0.
  - Headless engine suite (`-p rustkit-engine --lib --features headless`, 1989 tests), default threads: the first run (load 3–15) was stopped at its 50-minute limit after 1190 results: 1177 passed, 13 failed. The 784 tests it never reached ran next by exact name: **768 passed, 0 failed, 16 ignored**.
  - The 13 failures are GPU-test-guard and wall-clock timeouts. Each test printed 'running for over 60 seconds' before it failed: content_string ×3, console_log ×2, container_query ×1, control_percent_height ×1, control_semantics ×3, css_animations ×1, and page_script ×2 (stalled subresource at the budget, script stopped at its next host call). Rerun by name with `--test-threads=1` on 6afc63d2, all of them pass: 18/18 for the modules that hold them. The earlier cut run's 10 failures (computed_read ×3, consent_click ×7) also pass single-threaded: 32/32 for both modules.

## Receipt (`scripts/receipt.py`)

```json
{
 "base_sha": "95691f85",
 "binary": "scratch/bins/cand",
 "binary_mtime_utc": "2026-11-06T17:47:14.742294Z",
 "binary_sha256": "ed76fc56403a6a6c2ac6031742731db33c34c0a3fb58600b30bf6005359c4258",
 "branch": "atlas/z-ch2-e17-style-media",
 "campaign": null,
 "candidate_sha": "6afc63d27ceec1fd3358a077de1277dd3aad01ee",
 "cargo": "cargo 1.91.0 (ea2d97820 2025-10-10)",
 "cargo_lock_sha256": "36360f8f04d56d938a5d58455c21b1feb791b309cc1dc7eddd356856f9a28e0d",
 "chrome_version": null,
 "cpu": "arm",
 "dirty_state": true,
 "effective_engine_flags": {},
 "features": null,
 "host": null,
 "note": null,
 "os": "macOS-26.5.2-arm64-arm-64bit",
 "profile": null,
 "raw_runs": [
  {
   "bytes": 417644,
   "file": "scratch/run-red.log",
   "sha256": "dd03b7537f899e11672178cd0feb44265bb0d4fde9fdcf365e0b3ded5544eb42"
  },
  {
   "bytes": 407224,
   "file": "scratch/run-green.log",
   "sha256": "402378e10d27b43de7c7cdef05881ef27c429209a59a6a241cf52af39d09d994"
  }
 ],
 "repo": "https://github.com/hiwavebrowser/hiwave-macos.git",
 "rustflags": null,
 "sccache": true,
 "target": "aarch64-apple-darwin",
 "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)",
 "utc": "2026-11-06T17:47:33.196600Z",
 "work_package": "CH2.E17"
}
```

🤖 Generated with [Claude Code](https://claude.com/claude-code)
