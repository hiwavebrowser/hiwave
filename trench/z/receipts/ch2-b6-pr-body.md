**CH2.B6** (PLAN-z, chrome board): the system font stack is not the gap. `text-transform` is.

### Measurement first (probe of chrome.html's stack at its sizes and weights)
`-apple-system, BlinkMacSystemFont, 'Segoe UI', …` resolves to `.SFNS-*`. A 20-character run at 10/11/12/13/14/16 px and weights 400/500/600/700 matches Chromium 143.0.7499.4 within **±0.4 px** in all 24 cases (400 and 700 within 0.03; 500 is +0.23 to +0.37 and 600 is −0.25 to −0.39). The row's "±1 px" criterion already passes on develop. The rows that missed:

| probe | Chromium | develop |
|---|---:|---:|
| 11px 600 `letter-spacing:.04em; uppercase` | 142.06 | 122.71 |
| 12px `letter-spacing:.7px; uppercase` | 154.27 | 132.20 |
| 13px `capitalize` | 133.88 | 127.17 |

Paint already drew the transformed text, with advances matching Chromium (141.87 / 154.25 / 133.87). Layout measured the **untransformed** text, so an uppercase title's box was ~15 px narrow at 12 px. The next inline sibling started inside the painted glyphs, a flex row's next item moved in, and shrink-to-fit parents were too small. chrome.html uses `text-transform: uppercase` on five rules (section titles and badges).

### Fix
The engine builds the text run from the transformed text when the transform keeps the character count. `text_sources` maps run characters 1:1 to the DOM text. A count-changing case (`ß` → `SS`) stays raw and is still transformed at paint, as it is today. uppercase, lowercase and capitalize are idempotent, so paint and selection, which re-apply the transform, are unchanged. (`innerText` reads from the run and is now transformed, which is what Chromium does.)

### Red first
- `73dd4a90` `text_transform_layout_tests` (3 tests): an uppercase span vs an already-uppercase control span, the next sibling's x, a flex badge after an uppercase + letter-spacing title, and capitalize plus its shrink-to-fit parent. Develop: 3 of 3 FAIL (67.08 vs 81.77, 75.12 vs 89.42, 53.60 vs 57.38).
- `8fbb7d95` fix: 3 of 3 pass. The sibling-x assertion is loosened to 0.5 px (the board's geometry threshold). Span box and inline advance differ by ~0.06 px on any run (0.18 on develop), and that is unrelated to the transform. The width assertions stay at 0.05.
- Oracle files on the hub: `trench/z/receipts/ch2-b6-oracle.mjs`, `ch2-b6-tt.html`, `ch2-b6-chrome-tt.json` (Chromium: uppercase 81.72, next x 81.72; flex title 89.58, badge 95.58; capitalize 57.39).

### Tests
- `rustkit-engine --lib`: 695 passed, 0 failed, 6 ignored.
- `rustkit-engine --features headless --lib` filtered to `text selection inner_text find transform`: 188 passed, 0 failed, 3 ignored.
- Chrome board row chrome/default/1280x800 (parity profile): pixel 3.185% → 3.185%, geometry diffs 210 → 208. This row's pixels are dominated by `#chromeMain`, so the effect on this row is small. The fix is for correctness on every transformed run.
- Not run here: the full headless suite, app tests, and the all-site A/B. The batch runs those.
- Build: z-cargo.py (lease + sccache). Host: macOS seat (Z lane). Base: develop e273c0bf.

### Expected movers for the batch A/B
Any page with `text-transform` on lowercase source text: nav bars and headings with uppercase or capitalize. Boxes get wider and siblings move right, toward Chromium.

Left on B6 (not in this PR): weights 500/600 run about ±0.3 px over 20 characters, which looks like named instance vs variable `wght` axis. That is under the row's threshold.

Needs Prometheus R1, then a batch with the all-site A/B (layout of every transformed run moves).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
