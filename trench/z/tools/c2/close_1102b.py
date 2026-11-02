#!/usr/bin/env python3
"""Session close 11-02 09:05: red-run receipt, digest section, plan note, C2 state."""
import subprocess

H = "/Users/petecopeland/Repos/.worktrees/z-hub/trench/z/"
R = "/Users/petecopeland/Repos/.worktrees/z-c2d-red/"
out = subprocess.run(["python3", H + "tools/c2/classify_log.py", R + "red.log"], capture_output=True, text=True).stdout
ser = subprocess.run(["python3", H + "tools/c2/classify_log.py", R + "red-serial.log"], capture_output=True, text=True).stdout
ret = subprocess.run(["python3", H + "tools/c2/classify_log.py", R + "red-retry.log"], capture_output=True, text=True).stdout
with open(H + "receipts/2026-11-02-851-red-e3dc36b2-NOT-A-RED-COUNT.txt", "w") as f:
    f.write("e3dc36b2, sticky_scroll_tests, load 40-110. NOT a red count: the environment failed most of it.\n\nthrough z-cargo, parallel:\n" + out + "\nbuilt binary, one thread:\n" + ser + "\nbuilt binary, one thread, filter makes_a_context:\n" + ret)

digest = """
## 2026-11-02 10:50 Z-lane C2 #851 gates at 2efc47f6: NOT DONE, C2 blocked by the stop rule

**Before -> after: nothing changed on #851.** Head is still `2efc47f6`, draft, no gates posted, nothing pushed. No receipt exists at this head.

**What ran:**
- Head already holds develop `afa159da` (merge: already up to date).
- I read the fix diff against the 23:55 order. Items (1), (2), (3) and the (4) arms are there, and the `isolation:isolate` root case is in the 48 tests. `opacity:99%` is not touched and I did not add it to the C12 row. Read only: no green run backs it.
- Census pins: `2efc47f6` pass, `e3dc36b2` fail 2 (`census measured gaps`, `bucket paint has 12 declarations`), as the order wants.
- Red at `e3dc36b2` did NOT confirm 6 of 48. Through z-cargo: 12 passed, 36 failed, of which 25 are GPU guard timeouts, 9 are the root-store error below, and 2 are real asserts (`a_view_transition_name_makes_a_context` 4 of 9 wrong, `will_change_of_a_mask_image_or_transition_name_makes_a_context` 5 of 8 wrong). The built binary on one thread: 0 of 48 pass, every one the root-store error; a retry at 10:46 on 4 tests, the same.

**Not run:** green at the head, layout, bindings, engine lib, headless suite, app build, campaign, 20-site A/B. I stopped the sequence at about 10:50 during the green compile: the red compile had taken 47 min, so it could not finish and run by the 11:08 cap.

**Blockers:**
1. `TLS error: no usable platform root certificates (... first error: failed to load system trust settings: I/O error.)`, from `load_native_certs` in `rustkit-http`, at engine creation. Cause not found. `security dump-trust-settings` needs approval on this seat, so I could not test the keychain outside the engine. The code's own comment calls this "keychain busy under load", which fits but is not shown. It fails tests that use no network, so **a suite run in this state reads as a mass regression and says nothing about the PR.**
2. Load 40 to 110 all session. What is driving it was not identified.

**Decision packet (C2 blocked, second session on #851 with no receipt): Atlas, reopen C2 for one slot on a quieter machine (my recommendation, the code is finished and only gates are owed), or run the gates yourself; either way run one sticky test first and start the gates only if it gets past the root-store error.**

**C10 not started:** about 20 min left, and no engine build fits in that at this load. It is next in table order.

**Tools:** `tools/c2/finish_851.py` (the full sequence), `serial_bin.py`, `classify_log.py` (failures by cause, not count). Receipt: `receipts/2026-11-02-851-red-e3dc36b2-NOT-A-RED-COUNT.txt`. Worktrees `z-c2d-finish` and `z-c2d-red` kept for the sweep: acceptance not passed. Left uncommitted: `tools/c2/ctx_z_fix.py`, `r1_850.mjs`, `r1b.mjs`, from before this session. Aleph and Null were not available in this session, and the Null MCP failed to connect. Open hiwave-macos PRs: #847, #851 (2 of 8).
"""
with open(H + "digest-z.md", "a") as f:
    f.write(digest)
subprocess.run(["python3", H + "tools/c2/setstate.py", "C2", "blocked", "10:50 (11-02) Z lane: BLOCKED, stop rule. #851 @ `2efc47f6` has no gates: engine tests fail on the root store (`failed to load system trust settings: I/O error`) at load 40-110, cause not found. Atlas: reopen for one slot on a quieter machine (recommended) or run the gates yourself; run one sticky test first."], check=True)
p = H + "PLAN-z.md"
s = open(p).read()
anchor = "> **11-01 22:30 ET (Z lane): 18:30 order done."
note = "> **11-02 10:50 ET (Z lane): 07:30 ORDER NOT DONE. #851 @ `2efc47f6` has no gates and nothing was pushed; do not flip it. Engine tests fail at engine creation on `no usable platform root certificates` (`failed to load system trust settings: I/O error`), 48 of 48 on one thread, so the red count of 6 of 48 is not confirmed. C2 is blocked by the stop rule. Atlas: reopen C2 for one slot on a quieter machine (recommended) or run the gates yourself; run one sticky test first, because a suite in this state reads as a mass regression.** C10 not started. Open hiwave-macos PRs: #847, #851 (2 of 8). Digest has the rest.\n\n"
assert s.count(anchor) == 1
open(p, "w").write(s.replace(anchor, note + anchor))
print("closed")
