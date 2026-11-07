# CH2.B18c: an author `border-width` on `<input>`/`<textarea>` is the painted frame (branch `atlas/z-ch2-b18c-input-border-width`)

- Base: develop 3b4561e3 (batch 34). Red: 01e7ee98. Fix: 468544a4. Pushed; no PR (cap 8/8; E20 and B17b are ahead in the queue).

## Before → after
- **Before:** `render_form_control` (crates/rustkit-layout/src/lib.rs) painted a 1px frame for any border style except `none`. `<input style="border:40px solid red">` drew a hairline, while Chromium 143 draws a 40px ring. Layout already sized the box with the author width (`content_box_control_extra`), so only the paint was wrong.
- **After:** the painted width reads `border-top-width`. `Length::Zero` (unset) keeps the 1px UA stand-in. An author width paints as written, and an author `0px` paints nothing. The renderer already insets four strips and seats the text by that width.
- Scope: text inputs and textareas (both use the same `border_width`). Buttons/selects paint their frame elsewhere (forms.rs) and are not touched.

## Pin
- `tests::an_author_border_width_is_the_painted_control_frame` (rustkit-layout lib): 40px → 40, 3px → 3, 0px → 0, unset → 1. Red on develop: 1 vs 40. Green with the fix.

## Gates at 468544a4 (gates.py, base 3b4561e3)
- rustkit-layout lib: 907 passed, 0 failed.
- Campaign: 26/26. One case moved: **css-selectors, 12767 → 12561 diff pixels (toward Chrome)**.
- All-site A/B (ab5.py, `ab-b18c.txt`): **four movers, all 0 within each arm and the same value on all four cross pairs.**
  - bing 0.12%: changed pixels in x 200–413, y 174–195 (the search box band).
  - netflix 0.08%: x 953–1099, y 4–799.
  - x 0.07%: x 46–409, y 523–542.
  - wikipedia 0.02%: x 133–1186, y 164–185 (search row).
  - These regions match bordered inputs. Their direction is NOT yet checked against Chromium.
  - The rest is noise: linkedin/walmart/google vary inside one arm (served variants), and cnn hit the 30 s limit 4/4 in both arms.
- Parity sha256: base d431d078d5c18183210d40f9e55983b2d9168a8ec36a43a6c83239ee2fa07e82, candidate 6e3e27bd6024b123436375dee8e00711cca262981348c887ca3bcf7f2e983ba3.
- **OWED:**
  1. A pinned-Chromium look at the bing and netflix mover regions (toward or away from Chrome).
  2. The headless engine `input|control|textarea|form` filter, and the full headless suite (2084).
  3. The real-window `e22_focus_ring` check (expected 7/7 with this fix).
  4. The PR when the cap allows.
- Worktrees `z-ch2-b18c` and `z-base-3b4561e3` are KEPT for the owed gates.
