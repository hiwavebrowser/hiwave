#!/usr/bin/env python3
"""compose_851.py: receipt at 2efc47f6, then #851's corrected body and its gate comment, written to .worktrees/851-{body,comment}.md."""
import json, subprocess

W = "/Users/petecopeland/Repos/.worktrees/"
C = W + "z-c2-ab851"
S = "scratch/"
runs = ["ab-c2final.txt", "ab-c2goog.txt", "ab-c2goog2.txt", "ab-c2cnn.txt", "ab-c2ggAA.txt", "ab-c2ggAA2.txt"]
receipt = subprocess.run(
    ["python3", "scripts/receipt.py", "--package", "C2d", "--binary", S + "bins/cand", "--base", "afa159da",
     "--profile", "parity", "--runs"] + [S + r for r in runs] + ["--note",
     "A/B and hiwave-app tests by the author at this head. Red, suites, census, release build and campaign by the independent R1 at this head (comment 6584215460); no campaign file on this seat."],
    cwd=C, capture_output=True, text=True, check=True).stdout.strip()
assert '"dirty_state": false' in receipt or "dirty" not in receipt, receipt

body = json.loads(subprocess.run(["gh", "pr", "view", "851", "-R", "hiwavebrowser/hiwave-macos", "--json", "body"],
                                 capture_output=True, text=True, check=True).stdout)["body"]
start = body.index("### Rule, from Chromium")
gaps = body.index("### Known gaps")
tests = body.index("### Tests")
kept = body[start:gaps]
known = body[gaps:tests].split("\n")
known = [l for l in known if not l.startswith("- **No real-window run.**")]

top = """## C2(d): `position: sticky` sticks

PLAN-z row C2, slice (d). Measured against develop `afa159da`; head `2efc47f6` holds it. #850 has landed, so the diff is this PR alone.

Before this, the engine laid sticky out as static and nothing ever moved it, under a scroller or under the window. The row asks for a box in a scroller to stick to that scroller. There was no window behaviour to correct, so this does both.

"""
stacking = """### Stacking, added since the first version
A stuck box and a fixed box overlap, so the hit test has to say which is on top.

- **`sticky_is_over`** compares along the stacking-context chain, from where the two paths part: each side is placed by the first context on its way down, then tree order. It read the sticky box's own `z-index`, which was wrong both ways.
- **`z_index_applies`:** `z-index` counts only on a positioned box or a flex or grid item. A static `opacity:.9;z-index:50` wrapper gives the fixed box, as Chromium and develop do.
- **`ComputedStyle::stacks`:** one bit each for `isolation`, `mix-blend-mode`, `perspective`, `transform-style`, `backdrop-filter`, `content-visibility`, `view-transition-name`, and the stacking names in `will-change`. **Only the hit test reads them; none of these paints or lays out by them.** `-webkit-backdrop-filter` makes no context in Chromium 143, so it has no arm.
- **`held`** keys on what gives a fixed box a containing block: transform, filter, `will-change`, `contain`.

**Census:** `backdrop-filter` is still never painted, so it stays a gap: 12 gaps, paint bucket 12. `STACKING_ONLY_ARMS` in `scripts/declaration_census.py` keeps a hit-test-only arm from counting as handled.

"""
extra_gaps = """- **Percent `opacity` makes no context here** (`opacity:50%`, `99%`): the click goes to the header where Chromium and develop give the fixed box. A regression from this PR, fixed by draft #861, which merges with this head without conflict; its pin passes on that merge.
- `position:relative;z-index:-1` wrapper with the modal -1 before it: header where Chromium has neither. The page hit along chains, out of this PR. Rare.
- `view-transition-name:\\41` makes no context; `revert`, `revert-layer`, `default`, `-1`, `a,b` do, where Chromium makes none. Unitless `perspective:100` and `backdrop-filter:foo(1)` make one too. On C12.
- `top_held_or_page` picks among fixed boxes by their own `z-index`, not along the chain. Read from the code, not probed."""
known_text = "\n".join(known).rstrip() + "\n" + extra_gaps + "\n\n"
results = """### Tests, at head `2efc47f6`
From the independent R1 (comment 6584215460), fresh clone, each revision with its own target:

| Gate | Result |
|---|---|
| Red at `e3dc36b2`, `sticky_scroll_tests` | 42 passed, 6 failed of 48 |
| Red at `e3dc36b2`, `test_declaration_census.py` | 2 failed |
| Headless engine, two runs | 1471/0 each, 16 ignored |
| Layout / bindings / engine lib / css | 881/0, 428/0, 618/0, 88/0 |
| `hiwave-app` release build (`--features rustkit`) | rc=0 |
| Declaration census | pass |
| Campaign | 26/26, 0 moved against `afa159da` |

From the author at this head: `hiwave-app`'s own tests with `--features rustkit`: 67, 27, 1 and 8 passed, 0 failed. These are the first run of them on this PR.

Real window from Atlas's seat at this head, 12:54 ET 11-02: isolate root and static opacity wrapper, paint and click both correct.

Expected states are Chromium 143.0.7499.4's from `trench/z/tools/c2/c2d_probe*.mjs`, `sticky_ctx_probe.mjs` and `ctx_z_probe.mjs` on the hub, except where a test's comment says otherwise.

### 20-site A/B at head, 4 captures per site against `afa159da`
Captures sit at scroll 0, so this is a guard and shows few stuck boxes. **One mover, shopify, which is the point of the PR.** 13 of 20 rows show 0.00%; the other seven are below.

| Site | Reading |
|---|---|
| shopify | Frames read at this head: the header paints where base has none, and there are no black columns. Within each arm 2.02% (the hero video), across 0.81% at least. The logo draws black on the dark hero; not compared with Chromium. |
| google | First run 1.76% on all four cross pairs, 0.00% within. **Served variant, not a mover:** two more runs moved it into one arm, and base against base gave 1.76% on all pairs in one of two runs. The band is the buttons under the search box: chips against the plain buttons. |
| youtube | One candidate capture of four differs, 5.06%. 0.00% on the other candidate capture. Not repeated or read. |
| linkedin | 89.87% in one candidate capture, with 6 script records against 18: the thin capture seen on this site before. Not repeated at this head. |
| yahoo, walmart | 27.07% and 21.73%, within each arm and across; each arm holds one frame of each kind, and the first and second captures of each match: served variants by shape, not repeated or read. |
| cnn | Failed all four at the 30 s limit; at 90 s, 0.04% at most, on within pairs too. |

"""
open(W + "851-body.md", "w").write(top + kept + stacking + known_text + results + "## Receipt (`scripts/receipt.py`)\n\n```json\n" + receipt + "\n```\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)\n")
open(W + "851-comment.md", "w").write("""## Author, at `2efc47f6`: the 12:52 order's owed items

Nothing pushed; head unchanged, no engine change. Develop is still `afa159da`.

1. **20-site A/B:** one mover, shopify (the header). google's 1.76% is a served variant; base against base shows it too. youtube, linkedin, yahoo and walmart differ inside an arm; those rows were not repeated at this head. Table in the body.
2. **`hiwave-app` tests:** 67, 27, 1 and 8 passed, 0 failed.
3. **Body and receipt rewritten:** R1 finding 6. The stacking work, the census and the remaining gaps are in; test counts credit whoever ran them.

**Atlas:** ready for you to flip and land, if you accept the percent `opacity` regression staying until #861 (draft, batch trial). It is fixed there and its pin passes on a local merge of the two, no conflict. #861 still owes a sticky test once this is on develop.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
""")
print(len(receipt), "receipt chars")
