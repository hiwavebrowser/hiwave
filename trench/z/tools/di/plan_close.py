#!/usr/bin/env python3
"""Row notes for the 21:05 session: DI back to open (R1 asked), CA1 item 2 PR, C2 in-progress."""
p = "/Users/petecopeland/Repos/.worktrees/z-hub/trench/z/PLAN-z.md"
s = open(p).read()

old = "| Prometheus | any non-author | in-progress | 21:10 (10-30): lane session: develop check at c25c1d71, then #817: develop merged, the 10-29 12:25 contents patch folded in red-first, fresh receipts, R1 asked. 09:45 (10-28)"
new = "| Prometheus | any non-author | open | 22:30 (10-30): **#817 updated, draft @ `ec8ee96c`** (develop c25c1d71 merged; red `b1cc2de8` 3/5, fix folds in the 10-29 12:25 contents patch). Headless 1274/0, app build rc=0, campaign 26/26 0 moved. 20-site A/B: apple 0.11% toward Chromium (nav 3 items to all, in a row; bar colour and list width unchanged); google arm-tie disproved by a swapped pass. **Needs Atlas to flip ready and ask R1.** 09:45 (10-28)"
assert old in s
s = s.replace(old, new)

old = "**(5) → PR #831 (draft) @ `fa333bd0`**"
new = "22:30 (10-30): **(2) → PR #841 (draft) @ `c2693048`** (red `c7791696` 5/6): `flex` keywords, lone basis, basis first, invalid values against a Chromium 143 table. Taken before the CSS-week note was read; it is CSS and finished, so Atlas's call whether it lands ahead of the C rows. github header 5.57% and cnn 0.28%, both toward Chromium. Headless 1273/2, both failures pass by name (A/B was running); whole suite not repeated quiet. Needs flip + R1. Found: `parse_flex_basis` answers auto for em, calc(), min/max-content (`flex: 1 1 10em`, Chromium 160px). **(5) → PR #831 (draft) @ `fa333bd0`**"
assert s.count(old) == 1
s = s.replace(old, new)

old = "| Z lane | Prometheus | any non-author | open | 10-30 22:40: NEW, CSS week; the biggest visible CSS gap in the ledger. |"
new = "| Z lane | Prometheus | any non-author | in-progress | 22:35 (10-30): lane started slice (a), red first. 10-30 22:40: NEW, CSS week; the biggest visible CSS gap in the ledger. |"
assert old in s
s = s.replace(old, new)
open(p, "w").write(s)
