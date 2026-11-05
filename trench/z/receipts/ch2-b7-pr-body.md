## CH2.B7: a `height:0` column flex is 0 tall (and three neighbours)

Row CH2.B7 (disclosed on #903): `display:flex; flex-direction:column; height:0` laid out at its content height (84px for two 40/44px children; Chromium 0).

**The row's premise is too narrow.** The cause was not column flex. A unitless `0` in a sizing property parses to `Length::Zero`, which is the enum's default. Layout's sizing code reads only `Px` as a specified size, so on develop:
- `height:0` laid out as `auto` on any box (block, row flex, column flex). `height:0px` was correct.
- `max-height:0` / `max-width:0` laid out as `none`.

Writing the red tests against Chromium turned up three more gaps on the same pages:
- A column flex container with an indefinite height and a `max-height` kept its items at their stacked size, so they overflowed. Chromium flexes them into the max-height: 40/44px items in `max-height:20px` come out 10/10.
- `min-height` with a smaller `max-height` came out at the max on any block. CSS 2.1 §10.7 and Chromium: min wins.
- `height:100%` under a definite `height:0` parent took its content height. The zero base was treated as "unknown".

### Fix
- `rustkit-engine`: `width`, `height`, `min-*` and `max-*` store a unitless `0` as `Px(0.0)` (new `parse_size_length`), the same way `font-size: 0` already did. getComputedStyle prints `0px` for both, so the read is unchanged. `min-width: 0` still turns off the flex automatic minimum, because that check matches only `Length::Auto`.
- `rustkit-layout/flex.rs`: a new `max_inner_main_size` (the counterpart of `min_inner_main_size`) clamps the indefinite vertical main size, both at entry and at step 11d. If steps 4–10 shrank a content-sized item below its automatic minimum, the item now asks for the step-11d rerun, so text rows stay at their text height instead of overlapping.
- `rustkit-layout/lib.rs`: `calculate_block_height` clamps to `max(max_height, min_height)`. `definite_content_height_for_children` takes `base_is_definite`, so a percentage of a definite 0 resolves to 0.

### Red first
- `c1ead7b0`: unitless zero height/max-height. 3 of 4 tests fail on develop.
- `0b42ce15`: max-height column flex and min-over-max pins. Both fail on develop. The text-rows guard passes on develop and caught one regression from my first draft of the fix.
- `5c5d9a71`: the fix. 6/6 pass.

The expected values come from Chromium 143.0.7499.4 (pinned oracle, deterministic launch, 1280x800) on the exact same pages. Oracle script: `trench/z/receipts/ch2-b7-oracle/`.

| page | develop | branch | Chromium 143 |
|---|---|---|---|
| col flex `height:0` | c=84, kids 40,44 | c=0, kids 0,0 | c=0, kids 0,0 |
| block `height:0` | c=84 | c=0 | c=0 |
| col flex `max-height:0` | c=84 | c=0, kids 0,0 | c=0, kids 0,0 |
| col flex `max-height:20px` | c=20, kids 40,44 | c=20, kids 10,10 | c=20, kids 10,10 |
| col flex `max-height:20px; min-height:30px` | c=20, kids 40,44 | c=30, kids 14,16 | c=30, kids 14,16 |
| block `max-height:20px; min-height:30px` | 20 | 30 | 30 |
| `height:0` > col flex `height:100%` | c=84 | c=0, kids 0,0 | c=0, kids 0,0 |
| text rows in `max-height:20px` col | 18,18 @ 0,18 | 18,18 @ 0,18 | 18,18 @ 0,18 |

### Runs (targeted; the batch runs the full gates)
- `rustkit-layout --lib`: 896 passed, 0 failed (13 ignored).
- `rustkit-engine --features headless --lib -- flex height percent grid sticky aspect inset collapse`: 217 passed, 0 failed (9 ignored), 796 s.
- The full engine lib suite was not run on this seat: it hit the 20-minute background limit under load and was stopped. The batch runs it.

### Expected batch A/B movers
Any page that writes `height:0`, `max-height:0` or `max-width:0` (collapsed accordions, hidden menus, `max-height:0; overflow:hidden` transitions), and column flex lists with a `max-height`. This is a layout change, so the all-site A/B belongs in the batch.

Receipt fields: base develop `34afa3b6`, candidate `5c5d9a71`, toolchain from `rust-toolchain.toml`, host macOS seat (Darwin 25.5.0), Chromium 143.0.7499.4. Profile: the debug test profile (no pixel measurement in this PR).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
