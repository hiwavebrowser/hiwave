T16: `parity-capture --save-html <dir>` saves the settled page, and `--html-file` replays it

Branch `atlas/dt-t16-save-html`, base develop 232fca86. Red 36198817, fix 71e24dae. This file is the draft PR body. Open it with `gh pr create --draft --base develop` once fewer than 8 PRs are open.

## Why
Reducing a live page needs the page as it stood when the capture ended: the DOM after its scripts ran, and the sheets that styled it. The reduction on github was blocked for lack of this (11-04).

## Change
- **Engine (opt-in, off by default).** `Engine::keep_sheet_texts(view)` makes the view keep the text of every external sheet it fetches from then on, keyed by URL, exactly as parsed: `url()`s already absolute (`absolutize_css_urls`). This includes a sheet that arrives after the subresource budget (Z row S6). The map is cleared with the rest of the per-document state on navigation. When keeping is off, the cost is one `None` clone per sheet fetch.
- **`Engine::settled_html(view)`** (new `save_html.rs`) serializes the view's DOM as it stands:
  - every `<link rel=stylesheet>` is replaced in place by a `<style data-saved-sheet="link">` holding that text, keeping the link's `id`/`class`/`media`/`title`;
  - a link with no kept text (never requested, failed, or keeping off) becomes an empty `<style data-saved-sheet="missing">`, so sibling structure is unchanged;
  - adopted sheets go last in `<body>`;
  - scripts stay as empty `<script type="text/x-hiwave-saved-script">` elements, keeping only `id`/`class`. They hold their place for selectors, and nothing runs them;
  - `<noscript>` is emptied when the capture ran script, because it was text then;
  - a `<base>` is added: the page URL without query, fragment or userinfo;
  - a `</style` inside sheet text is split.
- **parity-capture `--save-html DIR`** writes `DIR/page.html` from the final state, after actions and the live loop, and reports `saved_html`.
- No cookies, headers or response bodies other than the sheets' are written.

## Tests
- Red first @ 36198817: `a_saved_page_replays_the_settled_dom_and_its_late_sheet` failed with `page.html written: NotFound`.
- The fix commit corrects the test's JSON paths (the diagnostics record is `box`/`h`, not `layout_box`/`height`). The red failed before reaching them.
- The test page links `/a.css` and `/late.css`. The server holds `/late.css` for 8.6 s, past the 8 s budget, so the sheet is applied on a live turn. A `setTimeout` inserts `p#added.made`, which only the late sheet sizes. The page also has a `<noscript>` block 400 px tall. The capture runs `--url …/page?tok=SECRET#frag --live-ms 11000 --save-html`.
  - **Live capture:** `#early` 33 px, `#late` 77 px, `#added` 55 px.
  - **Saved file:** contains `#added` once, the late sheet's text, the absolute `url()`, no `<link`, and the base without query. It contains none of `SECRET`, `frag`, `createElement`, the script's marker, or `#ns`.
  - **Replay** with `--html-file` (script on, so a script that ran again would show): the four border boxes are identical to the capture's.
- `cargo test -p parity-capture --profile parity`: **73 passed, 0 failed**.
- Engine `--features headless --lib sheet`: **31/1**. The one failure, `a_sheet_that_misses_the_budget_applies_when_it_arrives`, is a wall-clock bound (load 15). It passes alone in 4.8 s.
- `check -p hiwave-app`: clean.
- Full headless engine suite: **1806 passed, 23 failed, 29 ignored** in 3369 s, at load 4 to 18.
  - 22 of the 23 log "GPU test guard: waited 120s". 11 of those wait behind `computed_read_tests::r1_cases` (row T23) and 11 behind `grid_block_axis_align_tests` (a known GPU-guard class). This is the same class and count as T20's 1599/23 run.
  - The 23 were **not** re-run single-threaded this session (out of time). R1 should re-run them by module with `--test-threads=1`.

## Campaign
- Candidate 71e24dae: 26/26, mean **1.0931%**.
- Develop arm 232fca86, built in its own checkout: 26/26, mean **1.0931%**.
- **0 of 26 cases differ.** The move from the older receipts' 1.1095% is develop's own (66 commits since c959570f), not T16.
- Both arms ran on z-cargo parity builds: `target/release` was symlinked to `target/parity`, and a no-op cargo shim was put first on PATH. The seed release binary was moved aside first.

## Witness: github.com (live, headless, shape only)
- **Capture:** `--live-ms 8000 --save-html`, status ok, 2009 boxes.
- **Saved file:** 6.9 MB.
  - 28 sheets inlined. The event log shows exactly 28 stylesheet requests.
  - 19 links came out `missing` (14 with `media`). None of the 19 was ever requested.
  - 13 scripts made inert.
- **Replay** with `--html-file`: status ok, 1996 boxes. 2.66% of frame pixels differ.
- What the replay lacks: images (`load_html` fetches none), script, and the product UA.
- **Lead for the Z plan (not T16):** stylesheet discovery runs only at load (`discover_external_stylesheets`, called from `load_external_stylesheets_slotted`). So a `<link rel=stylesheet>` that script inserts later is probably never fetched. github's 19 unrequested links fit that. Which of the 19 were inserted by script is not checked.

## Limits (stated in `save_html.rs`)
- Not carried: shadow roots, form state set from script (`value`/`checked` properties), canvas pixels, frames' documents, and rules added through the CSSOM to a sheet that has no text.
- The replay fetches no images (an `--html-file` load fetches nothing). An unsized `<img>` lays out differently.
- Attributes come out sorted (rustkit-dom keeps them in a HashMap).
- The serializer duplicates rustkit-bindings' private `serialize_node` (about 40 lines) rather than moving it. Moving it into rustkit-dom would be a follow-up.

## Cost
- Off: one `Option` clone per external-sheet fetch. No text is kept.
- On: one copy of each fetched sheet's text for the view's lifetime. The serializer runs once at the end of the capture.

## Receipt (`scripts/receipt.py`)
```json
{
 "base_sha": "232fca86",
 "binary_sha256": "4f7af4bf1515fff450ce50b87de8b6ddb9fd455e81219714e5055289ffb6f59e",
 "branch": "atlas/dt-t16-save-html",
 "campaign": {"cases": 26, "failed": 0, "mean_diff_pct": 1.0931, "passed": 26,
  "sha256": "95dd49a022845a03c2a7d20d547a1181defefdc2a89b6c7557b8d4db1cbb96f0"},
 "candidate_sha": "71e24daeb4fdbcec14aabdd0bbeedbd62218e68e",
 "cargo": "cargo 1.91.0 (ea2d97820 2025-10-10)",
 "dirty_state": false,
 "note": "develop arm 232fca86: 26/26 mean 1.0931%, 0 of 26 cases differ",
 "profile": "parity",
 "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)",
 "work_package": "T16-save-html"
}
```

🤖 Generated with [Claude Code](https://claude.com/claude-code)
