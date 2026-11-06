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
- Crate suites and headless suite: SUITE_RESULT

RECEIPT

🤖 Generated with [Claude Code](https://claude.com/claude-code)
