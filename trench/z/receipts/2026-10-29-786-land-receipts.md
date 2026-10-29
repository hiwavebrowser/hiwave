## #786 land receipts @ `0b072190` (Z lane, 2026-10-29 09:10–09:55 ET)

Atlas's 10-28 17:30 order, re-issued 10-29 04:40. Code untouched; nothing pushed to this branch.

**What was measured.** develop moved three merges past this branch's last develop merge (#821, #815, #818). So the candidate is `0b072190` merged locally onto develop `662b1651` (local commit `47f2c7e9`, clean merge, not pushed). It is measured against develop `662b1651`.

| field | value |
|---|---|
| base | develop `662b1651` |
| candidate | `0b072190` + develop `662b1651` (local merge `47f2c7e9`) |
| parity binaries (sha256) | develop `ac1fa027…23f15`, candidate `31c64997…f97529` |
| release binaries (sha256) | develop `53822271…168ea`, candidate `2e35a64e…160903` |
| toolchain / host | rustc 1.91.0, macOS 26.5.2 arm64, macOS seat |
| oracle | pinned Chrome 148.0.7778.216 |

### Timing (`--release`, interleaved develop/candidate pairs, 1280x800, 60 s capture limit)

| site | pairs | develop median | candidate median | ratio | gate |
|---|---|---|---|---|---|
| cnn | 10 | 32.62 s | 38.03 s | **1.166** | ≤ 1.25 ✓ |
| yahoo | 5 | 5.71 s | 6.04 s | 1.058 | ≤ 1.10 ✓ |
| reddit | 5 | 0.34 s | 0.33 s | 0.971 | ≤ 1.10 ✓ (interstitial only) |

- The machine was loaded (1-min load 8.9–21.2 during cnn), so the absolute times are higher than 10-28's (18.2 s against 22.7 s). Only the paired ratio is meaningful.
- No run was killed. One candidate cnn run (round 3, load 20.4) **reached the 60 s capture limit without a frame**. Its develop partner took 41.9 s at load 21.1. The develop maximum was 44.1 s.
- Raw cnn runs, develop / candidate (s): 30.85/39.62, 28.85/36.44, 41.93/58.46, 41.94/60.03 (no frame), 39.63/52.62, 44.06/46.36, 34.39/34.20, 28.96/33.83, 25.90/34.90, 25.17/24.88.

### Campaign
26/26 on both arms. **0 cases moved.**

### 20-site A/B (A,B,A,B, parity binaries)
These are the same movers as at `ce830b72` (10-28):
- weather 10.33%
- apple 2.52% (the `display: inherit` gap, #817)
- google 1.57% (develop varies 1.68% within its own arm)
- microsoft 1.15%
- instagram 0.30%
- yahoo 0.30% (develop varies 35% within its own arm)
- netflix 0.16%

**One more needs a line: github 0.63%.** It is stable in both arms; a repeat A,B,A,B gave 0.63% in every cross pair and 0.00% within each arm.
- It is confined to the header band (y 34–67).
- develop: the nav items sit low and are clipped, with no Sign up button.
- candidate: one row of items, the search box, Sign in, and a black Sign up button. This is Chrome's arrangement.
- Both arms still lay the header out about 776 px wide; Chrome uses the full 1280.
- So by structure the candidate is nearer Chrome, but by pixels it is further: 9315 → 12952 px more than 8 off in the band, 351516 → 355153 over the whole frame. Moved glyphs now land on different background.
- I read this as `display: contents` taking effect on github's header wrappers, like the 10-28 movers.

Not comparable in this pass:
- cnn and squarespace timed out at 30 s in all four captures in both arms (load around 30).
- shopify failed 3 of 4 captures.
- linkedin, bing and walmart vary within their own arms (served variants).

**Gate (Atlas 10-28 03:50, amended):**
- Met: cnn ≤ 1.25, yahoo ≤ 1.10, reddit ≤ 1.10, campaign 26/26.
- Met with a note: A/B movers. They are the known `display: contents` movers, plus github, whose structure is nearer Chrome and pixel count further. The one cnn run that hit the 60 s limit without a frame is also reported above.
