## macOS timing receipt: #812 interleaved paired `--release` runs (Atlas 10-27 19:00 acceptance)

**CORRECTED 21:50 (`2026-10-27-fl-812-cnn-correction.md`): the cnn #812+#786 arm below did not run `display: contents`. The #782 arm shadowed #786's parse. Re-run: 22.55 s against develop's 18.27 s (1.234), which FAILS "≤ develop". yahoo/reddit stand.**

**Result as first posted: PASS on all three gates.** yahoo 0.936 and reddit 0.972 (both ≤ 1.10). cnn with #812 + #786 finished every run (0 killed, 0 hangs). Its median was 20.88 s against develop's 21.73 s.

| field | value |
|---|---|
| base (develop) | `469a8779` (develop tip at 21:05; it includes f3f281a3) |
| candidate | #812 `3051bdc9` (unchanged, nothing pushed) |
| candidate + #786 | `3051bdc9` + `origin/atlas/display-contents-recut` `f0e9b3e1`, one conflict (adjacent test-module lines; kept both), plus `Self::rebox_culled_inline` → `Engine::rebox_culled_inline`. Local merge `df83be60`, not pushed |
| profile | `--release`, `-p parity-capture`, each in its own fresh worktree + target via z-cargo.py |
| sha256 develop | `0a8d20b8bfc049e359f8cf65477b35c12427c0df93083a8ad40ffd619571eada` |
| sha256 #812 | `7e75e8847a9c8a3f3678176d7e66b5a47f6574fe52d4661958b1046ac22ccd7f` |
| sha256 #812+#786 | `4b3671115bfd9ae515040214b1ff664e042cbb75cf4bc5d5c433adaaa1d036b6` |
| toolchain | rustc 1.91.0 (f8297e351 2025-10-28) |
| host | macOS lane seat, launchd `ProcessType=Standard` |
| method | `trench/z/tools/pairtime.py`. Each round runs the arms back to back in the order shown. Live URL from `websuite/realsite-top20.json`, 1280x800, `--timeout-ms 60000`, hard kill at 240 s. Wall-clock is per process. The 1-minute load is read just before each run |
| load | 11.4-14.4 for the whole run. The top holders were not this session: `python` pid 1233 (the null daemon, 100% for 24 days), `BTLEServer` 99%, and Grok Bot helpers. As the 19:00 note says, the ratio is the number of record and the absolute numbers are not quiet numbers |

### yahoo (develop vs #812)

| round | develop s (load1) | #812 s (load1) |
|---|---|---|
| 0 | 6.67 (14.4) | 7.27 (14.0) |
| 1 | 5.61 (13.3) | 5.79 (13.1) |
| 2 | 6.32 (12.9) | 5.85 (12.6) |
| 3 | 5.94 (12.7) | 6.08 (12.4) |
| 4 | 6.25 (12.1) | 4.64 (11.9) |

Medians: develop 6.25 s, #812 5.85 s. **Ratio 0.936.**

### reddit (develop vs #812)

| round | develop s (load1) | #812 s (load1) |
|---|---|---|
| 0 | 0.44 (11.7) | 0.33 (11.7) |
| 1 | 0.36 (11.7) | 0.36 (11.7) |
| 2 | 0.37 (11.7) | 0.35 (11.7) |
| 3 | 0.35 (11.7) | 0.34 (11.7) |
| 4 | 0.34 (11.7) | 0.65 (11.7) |

Medians: develop 0.36 s, #812 0.35 s. **Ratio 0.972.**

**Caveat:** parity-capture only ever gets reddit's first-step interstitial. It doesn't follow the script navigation to the real page (the plan, 10-12 hand-test log item 7, and the tool has no flag for it). So this times about 0.35 s of interstitial, not reddit's real page. That meets the letter of the gate, but it says little about forced-layout cost on reddit. A real-page reddit timing needs the app, or a capture that follows script navigation.

### cnn (develop vs #812 + #786, with #812 alone as a third arm)

| round | develop s (load1) | #812+#786 s (load1) | #812 s (load1) |
|---|---|---|---|
| 0 | 22.53 (11.4) | 22.60 (11.8) | 18.47 (12.5) |
| 1 | 20.12 (12.3) | 18.72 (12.2) | 19.79 (12.7) |
| 2 | 21.73 (12.4) | 20.88 (13.2) | 20.03 (13.0) |
| 3 | 20.36 (12.4) | 19.98 (12.7) | 20.41 (12.3) |
| 4 | 27.54 (11.8) | 21.09 (12.1) | 17.93 (13.6) |

Medians: develop 21.73 s, #812+#786 **20.88 s** (ratio 0.961), #812 alone 19.79 s (0.911). Every #812+#786 run finished with a frame; none was killed. Before #812, #786 ran past 200 s. All 15 cnn runs are under the old ~25 s target except develop's round 4 (27.54 s), but at load ~12 that target is only indicative.

Raw JSONL: `2026-10-27-fl-812-paired-release-timing.jsonl` (all 40 runs).
