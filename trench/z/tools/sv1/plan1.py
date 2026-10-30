p = '/Users/petecopeland/Repos/.worktrees/z-hub/trench/z/PLAN-z.md'
s = open(p).read()
a = "| Z lane | Prometheus | any non-author | in-progress | 15:05 (10-30): lane on SV1, develop check at 62e745f1 first."
assert s.count(a) == 1
s = s.replace(a, "| Z lane | Prometheus | any non-author | open | 16:05 (10-30): **PR #836 (draft) @ `57e44dd2`** (red `0634ba6a`): parsed SVG elements take the SVG namespace and spec-table names; `innerHTML`/`insertAdjacentHTML` on an SVG context parse as SVG; `SVGElement` gains `dataset`/`tabIndex`/`nonce`/`autofocus`. dom 87/0, bindings 428/0, svg 51/0, headless 1256/0; campaign 26/26 0 moved; 20-site A/B no mover (shopify repeated twice: served variant). Needs Atlas to flip ready and ask R1. Gaps in the body: breakout position, `<svg><title>` RCDATA, MathML, createContextualFragment, className string.")
b = "| Z lane | Prometheus | any non-author | open | 12:55 (10-28): found during the #821 R1. After HT27F. |"
assert s.count(b) == 1
s = s.replace(b, "| Z lane | Prometheus | any non-author | in-progress | 16:05 (10-30): lane started; first open row with a concrete task (I0/D0/D1 have no named next step). 12:55 (10-28): found during the #821 R1. After HT27F. |")
open(p, 'w').write(s)
