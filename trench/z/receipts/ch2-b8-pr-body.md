## CH2.B8: percent height chain pins + an explicit html height is the root rect

Row CH2.B8 (disclosed on #903): with `html, body { height: 100% }` and `.row { display: flex; height: 100% }`, `.row` read 102px (its content) in a 300x200 viewport. Chromium 143 gives 200.

**The row's own case already passes on develop 34afa3b6.** #902 (CH2.B1) fixed it, and that PR landed after the row was written. This PR pins the case for flex row, flex column, block, grid, the #903 reduced page, and a page with no doctype. All of them read 200 on develop.

**What was still wrong on the same pages: the document element's rect.** `root_element_geometry` folded body's margin box into an explicit html height, then floored the result at the root box, which is stretched to the viewport. On develop:

| page | develop html | branch html | Chromium 143 |
|---|---|---|---|
| `html,body{height:100%}`, body margin 8 | 216 | 200 | 200 |
| `html{height:50px}`, 136px body | 200 | 50 | 50 |
| `html{height:300px}`, 20px body | 200 | 300 | 300 |
| `html` auto, body margin 8 (control) | 36 | 36 | 36 |

The fix: the rect now takes html's own height, resolved against the initial containing block, plus html's padding and border. `auto` still uses body's margin box. Scroll height is unchanged, so this changes geometry reads only (`documentElement.getBoundingClientRect()`, `offsetHeight`). Layout and paint are untouched.

### Red first
- `eb16e867`: the chain pins (pass on develop) and the html-rect pins (3 of 4 fail on develop).
- `ca97472d`: the fix. 2/2 pass.

The expected values come from Chromium 143.0.7499.4 (pinned oracle, deterministic launch, 300x200) on the same pages. Oracle script: `trench/z/receipts/ch2-b8-oracle/`.

### Runs (targeted; the batch runs the full gates)
- `rustkit-engine --features headless --lib -- css_display_tests feed_reveal_trigger sticky_flex_grid is_complex_argument script_scroll root_element document_element percent_height`: 79 passed, 0 failed (5 ignored).
- `rustkit-engine --features headless --lib -- root html scroll_height offset_height bounding`: 56 passed, 0 failed.

### Batch notes
This touches script geometry reads, so it needs the all-site A/B. Pages that read `documentElement` height under `html{height:100%}` with a body margin will see 200 where they saw 216. It edits `rustkit-engine/src/lib.rs` (`root_element_geometry`), which is far from #913's arms.

Receipt fields: base develop `34afa3b6`, candidate `ca97472d`, toolchain from `rust-toolchain.toml`, host macOS seat (Darwin 25.5.0), Chromium 143.0.7499.4. Profile: the debug test profile (no pixel measurement).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
