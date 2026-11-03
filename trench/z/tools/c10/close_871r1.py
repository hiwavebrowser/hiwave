#!/usr/bin/env python3
"""close_871r1.py: Z lane 2026-11-03 15:20 close-out: C10 row back to open, digest entry."""
import os

hub = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..")
plan = os.path.join(hub, "trench/z/PLAN-z.md")
digest = os.path.join(hub, "trench/z/digest-z.md")

s = open(plan).read()
a = "| any non-author | in-progress | 15:10 (11-03) Z lane: in-progress: 13:58 order, #871 R1 BLOCK findings 1-3, red first."
assert s.count(a) == 1, s.count(a)
s = s.replace(a, "| any non-author | open | 15:20 (11-03) Z lane: **#871 R1 BLOCK findings 1-3 fixed @ a7ec389b** "
              "(red 6e53614e, 10 of 36; comment 6614485567): compressible img before the px-width arm (card column 200, was 800), "
              "explicit self stretch, % img in auto/max-content columns 40x20. Narrow runs: replaced_ratio 34/34, layout 881/0, "
              "engine grid/image/aspect/flex 137/0; full gates in batch. Left, decision for Atlas: R1 card WITH height:auto reads "
              "200x400 (Chromium 200x100, develop 400x400): the builder cannot see an author height:auto, and layout_image_in "
              "scales a height= attr with max-width; fix together (cascade height_declared + clamp keeps a specified height), "
              "touches block flow: follow-up row (recommended) or fold into #871. Finding 4 (height:50% in auto row) to C12.")
open(plan, "w").write(s)

entry = """
## 2026-11-03 15:20 Z-lane C10 (#871 R1 BLOCK)

**Before -> after (Chromium 143 rows, `replaced_ratio`):** f79319a5 had 10 of 36 R1 rows wrong -> a7ec389b 34 of 34 (16 listed KNOWN). R1's card `<img width=800 height=400>` + `max-width:100%` in `1fr 1fr`: 800x400 -> 200x400 (= Chromium); explicit `justify-self`/`align-self: stretch` 40x20 -> 400x100 / 400x200 / 200x100 (= Chromium); `width:100%` image in an `auto`/`max-content` column 0x0 -> 40x20 (= Chromium; `auto` + `max-width:100%` was 0x0 on develop too).

**PR:** #871 @ `a7ec389b` (red `6e53614e`), plain push, comment 6614485567. Narrow runs: layout 881/0, engine `grid replaced image aspect flex_` 137/0; full gates in batch.

**For Atlas:** R1's exact card *with* `height:auto` reads 200x400 (Chromium 200x100, develop 400x400). The width is fixed; the height is the older KNOWN gap: the builder cannot see an author `height:auto` over `height=`, and `layout_image_in` scales an attribute height with `max-width` (a direct item gets 200x100 by accident). They must be fixed together (cascade `height_declared` + a clamp that keeps a specified height), block flow too: a follow-up row (recommended), or fold into #871. Finding 4 to C12.

**Tools:** `tools/c10/replaced_ratio_probe.mjs` (+13 R1 rows), `replaced_ratio_skip.txt`, `close_871r1.py`. Receipt: `receipts/2026-11-03-871-r1-fix-runs.txt`. Slot 15:05-15:20, no lease waits, load ~1.3.
"""
open(digest, "a").write(entry)
print("ok")
