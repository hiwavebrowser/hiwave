## CH2.B18c: an author border width is a text control's painted frame

Row CH2.B18c in `trench/z/PLAN-z.md` (hub `atlas/z`). Base develop 3b4561e3. Red: 01e7ee98, then 01f3ffde. Fix: 468544a4, then cfb8e2b5 (head).

### Before → after
- **Before:** `render_form_control` (rustkit-layout) painted a 1px frame for any border style except `none`. `<input style="border:40px solid red">` drew a hairline where Chromium 143 draws a 40px ring, which is why the real-window `e22_focus_ring` check was stuck at 5/7. Layout already sized the box with the author width, so only the paint was wrong.
  - The same rule painted a 1px frame for `border: 0` and for `border-width: 0; border-style: solid`. Chromium paints none for both. The shorthand `border: 0` leaves our side styles set, so the old `style == none` test never fired.
- **After:** the painted width is the author width when all four sides agree:
  - unset (`Length::Zero`) keeps the 1px UA stand-in;
  - `0px` paints none;
  - widths snap the way Chromium's do: 0 < w < 1 paints 1, otherwise floor.
  - When the sides disagree (`border: 1px solid; border-top: 0`, underline inputs), the frame stays as on develop. The `TextInput` command carries one width, and the top side's 0 must not erase the other three. Per-side frames are a follow-up: a command and renderer change.
- Buttons go through the same painter (the probe shows `border: medium solid` → 3px, as in Chromium).

### Pins
- `tests::an_author_border_width_is_the_painted_control_frame` (rustkit-layout lib). Each case gives the painted width and the Chromium value:
  - 40px → 40 and 3px → 3 (red on develop at 1);
  - 0px → 0;
  - unset → 1;
  - 0.65px → 1;
  - 2.5px → 2;
  - 1px with top 0 → 1 (the 468544a4 head painted 0; red at 01f3ffde).
- Reduced page with 15 rows of border forms, base / candidate / Chromium 143 (oracle):
  - **The candidate matches Chromium** for `border:0`, `border-width:0 solid`, `thin`, `medium`, `3px`, `0.0625rem`, `calc(1px)`, `var(--w)` and `transparent`.
  - The mixed-sides row matches develop. Both differ from Chromium's three-sided frame, which needs the follow-up.
- `e22_focus_ring.html` rendered headless at rest: **red border pixels 1196 on develop, 41600 on the candidate, 41600 in Chromium**. The click/Tab half of the check needs Accessibility + Screen Recording; this seat has neither, so the real-window run is owed to a seat with grants.

### Receipt (hand-written fields; receipt.py is Prometheus's step)
- base 3b4561e3 / candidate cfb8e2b5
- toolchain 1.91.0 (rust-toolchain.toml); host: macOS seat (Darwin 25.5.0); Chrome: campaign baselines chrome-148, probes in the oracle Chromium (`tools/parity_oracle`)
- parity binaries (`--profile parity`), sha256: candidate 3627b4bb194c99c7f00897e839ab9d2301f23a69416406e9c2b74766651ab417, base d431d078d5c18183210d40f9e55983b2d9168a8ec36a43a6c83239ee2fa07e82
- fixture sha256: probe `bw.html` 29b6e617d5d2544ba235f7fd70c0d80d599a48bc1be19c5f4e48be55b9fca98d, `e22_focus_ring.html` 7ccec4d3d4c855281687809f99df55643cbf0ec22432e284f524cdb0bd1b9fff
- **Campaign at cfb8e2b5:** 26/26 pass. One case moved vs develop: css-selectors, 12767 → 12561 diff px (toward Chrome). It is identical to the 468544a4 run.
- **All-site A/B (`ab5.py`, 3b4561e3 vs cfb8e2b5, 20 sites, A,B,A,B): four movers.** Each is 0 within each arm and the same on every clean cross pair, and each is toward Chrome:
  - **bing 0.12%:** the search box loses an inner 1px rectangle drawn inside its rounded frame.
  - **x 0.07%:** the login field loses an inner rectangle inside its rounded box.
  - **wikipedia 0.02%:** the "hide" / "move to sidebar" buttons lose a frame. Chromium's computed style on the live page is `0px none` for both buttons.
  - **netflix 0.08%:** the language `<select>` and the email input lose a frame. Chromium's computed style is `0px solid`.
  - The same four movers, with the same values, appear at 468544a4.
- A/B noise:
  - google, yahoo, netflix, squarespace and linkedin/walmart (at 468544a4) vary inside one arm.
  - cnn hits the 30 s limit in both arms.
  - At cfb8e2b5, github (2/4) and weather (3/4) failed captures while the engine suite ran beside the A/B. At 468544a4 both were 0.00% across with no failures.
- Crate suites at cfb8e2b5:
  - rustkit-layout lib 907/0;
  - headless engine `input|control|textarea|form` filter 220/0 (3 ignored).
- Headless engine suite at cfb8e2b5: @@SUITE@@

Receipts: hub `trench/z/receipts/ch2-b18c/`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
