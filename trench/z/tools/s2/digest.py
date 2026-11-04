#!/usr/bin/env python3
"""Append this session's digest section (S5, S1, S2)."""
p = '/Users/petecopeland/Repos/.worktrees/z-hub/trench/z/digest-z.md'
text = """

## 2026-11-04 03:05 Z-lane S5, S1, S2 (01:05 order)
Three drafts off develop 76c6ff8b, each red first, narrow runs only (batch trial), full gates in batch. Open hiwave-macos PRs: 5 of 8 (#847, #859, #874, #875, #876).

- **S5 sr-only text paints → draft #874 @ `bbfeb08a`** (red `38264a63`). Before: 14 of 25 Chromium 143 ink rows wrong (legacy `clip: rect()` never parsed; `clip-path` skipped `<button>`/`<input>`, eBay's header buttons painted 888 px of "expand Cart"). After: 25/25. css 116/0, layout 881/0, engine clip/filter/outline/overflow/opacity/paint 209/0. Paint change: own batch slot. Census guard fails identically on develop (10 gaps vs pinned 12, paint 4 vs 12): not this PR, someone should re-pin it.
- **S1 gmail unstyled → draft #875 @ `6381303b`** (red `0b57baa0`, `ed9ec076`). Cause confirmed: after redirects the engine committed the *requested* URL (view.url, address bar, location, baseURI, history entry, base for every relative URL). Now the last hop's (request fragment kept). Chromium 143 agrees on the same two-origin shape. Narrow: redirect_base 3/0, core 30/0, engine nav/load/history/inspector 167+21 (one inspector pin moved to `/final`). Touches fetch: all-site A/B in batch.
- **S2 pointer events "stopped at the budget" → draft #876 @ `1c7da77c`** (red `3c3c3dbd`). **Re-scoped:** the 288 stops were reddit's queued move listeners cut by Pete's navigation to yahoo (cancel word), logged with the budget wording; the load started 5.5 s late behind 11 queued ~430 ms hover-restyle moves. Fix: content-thread `coalesce` keeps only the latest of adjacent moves (nothing reordered). Narrow 161/0.

**For Atlas:** (1) accept S2's re-scope or send it back; (2) a navigation cancel logs as "stopped at the script budget" (mislabel, one-line follow-up); (3) suggest a cost row: reddit hover restyle ~430 ms per move (`tree_reused=false`, presenter p95 8.1 s); (4) real-window checks owed on all three (eBay header, www.gmail.com fresh profile, reddit hover then type a URL); (5) census guard red on develop.
Receipts: `receipts/2026-11-04-s{5,1,2}-{body.md,runs.txt}`. Worktrees removed. Aleph not exposed this session (grep); Null recall found the Grok gmail measurement. Load ~1.1, no lease waits.
"""
open(p, 'a').write(text)
print('ok')
