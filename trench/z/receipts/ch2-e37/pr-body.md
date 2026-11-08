<!-- gh pr create -R hiwavebrowser/hiwave-macos --base develop --head atlas/z-ch2-e37-enter-modifiers --draft --title "fix(engine): Enter keydown carries its modifiers; a cancelled Enter types nothing; Enter in a textarea is a newline (CH2.E37)" --body-file trench/z/receipts/ch2-e37/pr-body.md -->
## CH2.E37: Enter and its modifiers (closes #990)

**Before (develop c7209173):** you could not tell Shift+Enter from Enter. `submit_focused_form` fired Enter's keydown with ctrl, shift and alt hardcoded to false. Two more faults sat on the same path, and between them the usual chat box (Enter sends with `preventDefault`, Shift+Enter is a newline) could not work:
1. **A cancelled Enter keydown still edited.** The key step that runs after the submit step skipped Enter's keydown entirely and never learned that it had been cancelled. When the key step ran alone, no keydown fired at all.
2. **Enter in a `<textarea>` never typed a line break.** The engine passes the edit model a bare `TextEditState`, with `area = None`, so `keyboard::handle_key` read Enter as Submit in every text control. The probe on develop gave `a` Shift+Enter `b` → `"ab"`.

**After:**
- `submit_focused_form_with(id, ctrl, shift, alt)` fires the keydown with the key's own modifiers. `submit_focused_form(id)` stays and passes no modifiers.
- When the submit step submits nothing, it records whether the page let its keydown through. The key step that follows uses that result and does not fire a second keydown. If the keydown was cancelled, nothing is typed. When the key step runs alone, it fires Enter's keydown the same way it does for any other key.
- `PageInput::FormSubmit` now carries the modifiers, and so does the app's `form_submit_url(ctrl, shift, alt)` (both macOS key paths). On the synchronous path, a `FormSubmit` was followed by a `TextKey` whose Enter arm ran the submit step again, so the keydown fired twice. The arm now skips that second run when a keydown is already pending.
- In `rustkit-dom` `handle_key`, Enter in an edit state marked multi-line is a line break. `sync_attributes` already marks every textarea this way.

**Oracle:** Chrome for Testing 148.0.7778.216, `tools/parity_oracle/enter_modifiers_log.mjs` (new). Every pinned value matches Chromium:
| step | Chromium 148 | develop | this branch |
|---|---|---|---|
| Shift+Enter in chat textarea | `Enter:t:S`, value `"\n"` | `Enter:t:`, cancelled, `""` | `Enter:t:S`, `"\n"` |
| Enter (page cancels) | `Enter:t:`, value unchanged | (same keydown), unchanged | same |
| Ctrl+Alt+Enter | `Enter:t:CA`, types nothing | `Enter:t:` | `Enter:t:CA`, nothing |
| Shift+Enter in a form field | `Enter:q:S submit` | `Enter:q: submit` | `Enter:q:S submit` |
| `a` Shift+Enter `b` in a textarea | `"a\nb"`, one Enter keydown | `"ab"`, no Enter keydown | `"a\nb"`, one |
| Enter Enter in a textarea | `"a\nb\n\n"` | no change | `"a\nb\n\n"` |
(Chromium also fires keydowns for the Shift, Control and Alt keys themselves. The shells send those separately, so the pins do not cover them.)

**Commits:** red `7c8f1841` (two engine tests, with stubs that keep develop's behaviour; both FAIL on develop), then fix `0dfc9b07`, then `655b554a` (the oracle script, plus a pin that Ctrl+Alt+Enter types nothing).

**Gates**
- Red-first: `enter_keydown_carries_its_modifiers_and_a_cancel_types_nothing` and `enter_in_a_textarea_types_a_newline_and_fires_one_keydown` FAIL at 7c8f1841 and pass at the fix.
- rustkit-dom lib: 110/0, including the new `test_keyboard_enter_in_a_bare_multiline_state_is_a_line_break`.
- rustkit-engine lib (default features): 797 passed, 3 failed under load 15. The 3 `content_thread` tests are wall-clock tests and pass 3/3 alone on one thread.
- hiwave-app: 109 passed, 2 failed (wall-clock asserts; one chrome round trip took 104 ms under load). Both pass 2/2 on one thread, so 111/111.
- Headless engine suite (`--features headless --lib`) at 0dfc9b07, load 12 to 15: the run was **partial**. The 1 h limit stopped it after 1415 of 2113 tests. Of those, 1353 passed, 3 were ignored and 59 failed. The failures came in GPU-guard-shaped bursts (`computed_read_*`, `grid_*`, `float_*`, `forced_layout_cause_*`) plus four `page_script_tests` wall-clock asserts. **All 59 pass on one thread.** The E37 pins pass 7/7 at 655b554a. The roughly 700 tests the run never reached are still owed, and the batch suite covers them.
- **Campaign and all-site A/B: not run.** The change only runs when Enter is pressed. Neither the campaign nor the A/B captures send key input, so neither can see it. Ask if you want them run anyway.

**Receipt fields:** base develop c7209173; candidate 655b554a (merges cleanly with develop 8ebc1b79; `merge-tree` shows no conflicts); toolchain 1.91.0 (rust-toolchain.toml); profile debug (tests); host macOS arm64 (Z lane seat); Chrome for Testing 148.0.7778.216; no fixtures; raw logs in the hub at `trench/z/receipts/ch2-e37/`.

**Not done:** Ctrl+Enter / Cmd+Enter commands in the edit model, which are unchanged and match Chromium on the pinned chord. `metaKey` on Enter, because `handle_text_key` has no meta and the app folds Cmd into ctrl, as it does for every key.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
