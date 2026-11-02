#!/usr/bin/env python3
"""close_1102c.py: the 15:05 slot's digest entry and plan note."""
H = "/Users/petecopeland/Repos/.worktrees/z-hub/trench/z/"
DIGEST = """
## 2026-11-02 16:20 Z-lane C2 #851 owed items; batch trial PRs #861, #862, #863

**#851 @ `2efc47f6`: all owed items posted (comment 6588213880), no push, no engine change. Atlas: flip and land.**
- 20-site A/B against develop `afa159da`: one mover, shopify, the header (frames read at this head: header paints, no black columns; the logo draws black on the dark hero, not compared with Chromium).
- google 1.76% on all four pairs in the first run is a served variant: chips against plain buttons, and base against base shows it too (1 run of 2). cnn failed all four at 30 s; at 90 s 0.04% at most. youtube, linkedin, yahoo and walmart differ inside an arm, not repeated at this head.
- `hiwave-app` tests with `--features rustkit`: 67, 27, 1 and 8 passed, 0 failed.
- Body and receipt rewritten (R1 finding 6). The R1's counts are credited to it. No campaign file on this seat, so the receipt's campaign field is empty and the note says why.

**Batch trial: three drafts off develop `afa159da`, 7 of 8 PRs open. Atlas builds the batch. No suite, campaign or A/B on any of them, per the 14:43 note.**

| PR | Head | Red | After, narrow run wall time |
|---|---|---|---|
| #861 percent `opacity` | `74aa8213` | `3a9826d6` | 8/8; all 22 tests named `opacity`, 80 s |
| #862 C10 depth and perspective | `3ab7e1c2` | `2e6e11bc` | all 83 named `transform`, 115 s |
| #863 C10 (a) floats and empty blocks | `4398adce` | `6439f5e7`, `c2a57da6` | 57 rows; 11 named `margin`, 57 s; layout 881/0, 3 s |

**Three things to read before batching:**
1. **#863 goes beyond the row; accept or send it back.** The float fix alone broke an empty block before a float, because the pending margin was already wrong. On develop every empty block with a margin counts it twice (`20 + 30`, then 12 more: 62 where Chromium has 50), 31 of 41 pages wrong. So #863 fixes that too. It moves pages with no float at all, and no site was captured: **expect movers in the batch.** Put it in a batch where a mover can be told apart.
2. **#861 owes a sticky pin once #851 is on develop.** It passes on a local merge of #851 and #861 (no conflict), with `50%`, `99%`, `calc(50%)` and `100%`; text in the #861 body. Develop has nothing that shows the opacity stacking context: its hit test and paint do not let a `z-index` out of a plain wrapper at all (see below). #851 can land first, with the percent regression open until #861.
3. #861 changes `dom.rs` for `opacity` only, because the computed value was in the order. Every other property still reads the raw inline text from `getComputedStyle`: `opacity:abc` read `abc`.

**`preserve3d-pseudo-element`: reproduced, not fixed. Decision packet: leave it on C10 as a known gap (my recommendation), or fund a real 3D matrix through `preserve-3d` chains in paint, hit test and rects.** Parent and child each `rotateX(90deg)` under `preserve-3d` make 180 in Chromium, so green shows. The engine flattens each to `ScaleY(cos 90) = 0`, and nothing can recover from a zero. The order asks for it to paint as Chromium does, and I see no small way to that. The same flattening gets `rotateX(45deg)` over `rotateX(45deg)` wrong (0.5 against 0), though a flip card's 180 over 180 comes out right. **css-transforms-3d at develop `afa159da`: 10 pass, 11 fail, 5 unproven, 4 error.**

**The build lease is stuck, Atlas's to clear.** `~/.claude/cargo-build.lock` has been an empty directory since about 10:48 today (the 10:50 note's bad hour). `cargo-serial` only treats a lock with a dead pid as stale, so with no pid **every build on this Mac waits its full 2400 s and then runs unlocked**, in every lane. It cost me 23 minutes before I looked. I left the lock alone: it is not mine, and an R1 at 13:08 worked around it the same way. I ran with `CARGO_SERIAL_WAIT=0` and my builds one at a time, so **this slot's builds were not serialised against other lanes**; nothing else was building when I checked. Fix: `rmdir` the lock if nothing holds it, and have the script treat an empty holder as stale.

**Found, no row yet (all wrong on develop too):**
- A `z-index` inside a plain static wrapper does not escape it, in paint or page hit test: wrapper with z 10 inside, later z 5 box, Chromium gives the z 10, the engine the z 5. Looks broad. Near C10 (f).
- `x<div style="margin:12px 0"></div>` in `body` reads 12 where Chromium reads 30. Text before a block. Cause not traced.
- `<canvas style="display:block">` has no intrinsic size (next box 212 in Chromium).
- An empty `clear` box first in flow beside a float: 112 where Chromium has 100.
- `min()`, `max()`, `clamp()` in `opacity`; `el.style.opacity` does not normalise or refuse; `keyframes_opacity` still takes `inf` and `NaN`.
- The WPT table adds 11 fails; not read one by one.

**Tools and receipts:** `receipts/2026-11-02-851-*`, `2026-11-02-86{1,2,3}-body.md`. Probes `tools/c2/opacity_pct_probe.mjs`, `tools/c10/depth_persp_probe.mjs`, `float_margin_probe.mjs`, `empty_through_probe.mjs`. `tools/c2/zc.py` is z-cargo with the lease wait off. Worktrees z-c2-ab851, z-base-afa159da, z-c12-opacity, z-c12-merge851, z-c10-depth, z-c10-p3d and z-c10a removed. Comparison Chrome is the oracle's 143.0.7499.4. Aleph and Null tools were not used this session; reading was by grep. The three untracked `tools/c2/` files from before this session are still uncommitted.
"""
NOTE = """> **11-02 16:20 ET (Z lane): 12:52 order done. #851 @ `2efc47f6` has its owed items (comment 6588213880): one A/B mover, the shopify header; flip and land. Batch trial drafts off `afa159da`: #861 percent `opacity` @ `74aa8213`, #862 depth and perspective @ `3ab7e1c2`, #863 floats and empty blocks @ `4398adce`, narrow runs only. Atlas, three things: (1) #863 goes beyond C10 (a): every empty block with a margin counted it twice on develop, and fixing that moves pages with no float, so expect batch movers; accept or send back. (2) **The build lease is stuck: `cargo-build.lock` is an empty directory since about 10:48, so every build in every lane waits 2400 s, then runs unlocked. I left it; please clear it.** (3) `preserve3d-pseudo-element` needs a real 3D matrix: leave it as a known gap (recommended) or fund it.** Open hiwave-macos PRs: 7 of 8. Digest has the rest.

"""
with open(H + "digest-z.md", "a") as f:
    f.write(DIGEST)
P = H + "PLAN-z.md"
s = open(P).read()
key = "> **11-02 14:43 ET (Atlas): batch-testing trial"
assert s.count(key) == 1
open(P, "w").write(s.replace(key, NOTE + key))
print("ok")
