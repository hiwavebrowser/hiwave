**CH2.B3** (PLAN-z, chrome board): the white blocks in the chrome.html workspace rows were transparent buttons painted with ButtonFace, and the squeezed names came from a button label that kept its template whitespace. Neither was a glyph problem: 🔒 and ▾ already paint from the cascade or emoji face, and they match Chromium in the frames.

### Causes
1. **ButtonFace was a paint substitute.** The engine UA arm left `<button>` with no background on purpose (`lib.rs` "leave them to the themed paint path"). `DisplayList` then swapped any alpha-0 button background for rgb(239,239,239), so an author `background: transparent` could never win. This is the #83 bug, which was fixed for fields and never for buttons. The expander (`.workspace-expander`) and the tab lock buttons (`.workspace-tab-lock-btn`) are both `border:none; background:transparent`, and Chromium computes `rgba(0,0,0,0)` for every button on the page.
2. **`input[type=submit|reset|button]` got the white field.** They lay out as buttons but fell under the input arm's WHITE. Chromium uses ButtonFace.
3. **The button label kept every space.** `node.text_content()` went into the label raw. chrome.html builds the expander as `<button>\n<32 spaces>▾\n<28 spaces></button>`, so it measured ~113 px and its `flex: 1` sibling (`.workspace-name`) got 0 px ("R …"). Chromium gives 15.7 px and 97 px.

### Fix
- engine UA arm: button and `input[type=button|submit|reset]` get rgb(239,239,239); input/select/textarea keep white.
- layout paint: the `Button` command takes the computed background as it is.
- engine box build: a text-only button's label collapses white space under `normal`/`nowrap`/`pre-line` (CSS Text §4.1.1).

### Red first
- `018ca8f0` `button_background_tests`: transparent `button`, flex `button`, and `input[type=button]` paint no background; unstyled `button`/submit/reset keep ButtonFace; an authored colour is kept. Develop failed 2 of 3.
- `043dab67` `a_button_label_collapses_its_whitespace`: develop FAIL (label kept its spaces).
- `7fb3d262` fix: 4 of 4 pass.
- Oracle: Chromium 143.0.7499.4 (`trench/z/receipts/ch2-b3-oracle.mjs` on the hub). The values are v/L/I `rgba(0,0,0,0)`, plain/Go/R `rgb(239,239,239)`, c `rgb(1,2,3)`, and both whitespace buttons 14.671875 px.

### Board (chrome/default/1280x800, parity profile, this worktree)
| | pixel diff | geometry diffs |
|---|---:|---:|
| develop e273c0bf | 3.185% | 210 |
| this branch | 2.445% | 201 |

The workspace rows now match Chromium (name, count, lock badge, transparent ▾, and lock buttons with no white block). What is left on this row is `#chromeMain` and a ~12 px vertical offset of the whole sidebar, which are separate items.

### Tests
- `rustkit-engine --lib`: 696 passed, 0 failed, 6 ignored.
- `rustkit-layout --lib`: 896 passed, 0 failed, 13 ignored.
- `rustkit-engine --features headless --lib` filtered to `form_ positioned_form_control select_popup button outline_tests leaving_input`: 182 passed, 0 failed, 5 ignored.
- Not run here: the full headless suite, app tests, and the all-site A/B. The batch runs those.
- Build: z-cargo.py (lease + sccache), parity profile for the board, debug for the tests. Host: macOS seat (Z lane). Base: develop e273c0bf.

### Expected movers for the batch A/B
Any page with an unstyled `<input type=submit|reset|button>` changes from white to ButtonFace, which is the Chromium colour. Pages with transparent buttons lose a grey block. Pages whose text-only buttons have indented labels get narrower buttons.

Needs Prometheus R1, then a batch with the all-site A/B (this PR touches paint).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
