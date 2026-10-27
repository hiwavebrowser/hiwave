# T6 follow-ups: draft PR #814 (`atlas/dt-t6-followups` @ a81c00ab), 2026-10-27 18:55

Base: develop f3f281a3. Commits: ad8b4974, a cherry-pick of cacf5917 (the in-time Unavailable hover), and a81c00ab.

| item (Atlas 15:20) | change | test |
|---|---|---|
| 1. Unavailable hover after the pointer left | `hover_unavailable()`, then `hovered_now(None)` | `an_unavailable_hover_after_the_pointer_left_clears_the_outline` |
| 2. Forget test through its callers | `console_answered` (the Console arm, pulled out) and `close_with`/`stop_picker_with` take send/show closures | `a_navigation_forgets_live_questions_and_a_close_forgets_all` |
| 3. `clearConsole()` resets `held_shown` | `clear_console_with` + `show_held`; `close()` and WebKit `console.clear()` (main.rs) both go through it | `clearing_the_console_brings_the_held_line_back_on_the_next_pump` |

**Red before** (each fix mutated out, against the final test code):
- Without the `held_shown` reset and without `forget_page()` in `console_answered`: 2 failed.
- Without `forget_questions()` in `close_with`, and with `hover_unavailable` forced false: 2 failed (the forget test at its close assertion, and the hover test).
- All restored: 11/11.

**Suite:** `cargo test -p hiwave-app` gave 67/0, 27/0, 1/0 and 8/0.

**Campaign/receipt:** not run, because the change is app-only. parity-capture has no hiwave-app dependency; checked in Cargo.toml, where the one other mention is a comment in rustkit-viewhost.

**Checkout** `dt-t6fu-1835` is kept for Atlas to remove (rule of 10-26 08:50).
