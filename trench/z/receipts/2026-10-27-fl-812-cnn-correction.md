## Correction to my timing receipt above (comment 6458147831): the #812 + #786 cnn arm was not running `display: contents`

**What was wrong:** develop's #782 (`63aee4b3`, @container HOLD 2) added an early `display` arm. For `contents` it only sets `display_contents_declared` and returns, because develop had no author `display: contents` then. When #786 is merged onto anything that contains #782, that arm silently shadows #786's parse. Git reports no conflict. So the "#812 + #786" binary I timed gave every author `display: contents` element a block box, the same as develop. I found it while merging develop into #786 for the re-open: 4 of its 7 `css_display_tests` went red after the merge (getComputedStyle read `block`). They're green again once the arm also sets `Display::Contents`. The frames show the same thing: that arm differed from #812 alone by only 0.16% on cnn.

**yahoo and reddit are unaffected** (those were #812 alone): 0.936 and 0.972 stand.

**Corrected cnn run.** Same method (`pairtime.py`, five interleaved triples, `--release`). The #812 + #786 binary now carries the one-arm fix: `display: contents` sets `Display::Contents` and keeps the flag for `@container`. sha256 `8049de418a1126d2f64a1b2f5ad9bb09a7e238e267060e8186b0f1c0492be787`. Its cnn frame now differs from #812 alone by 0.53% on every run (deterministic), so #786 is in effect.

| round | develop s (load1) | #812+#786 s (load1) | #812 s (load1) |
|---|---|---|---|
| 0 | 18.76 (13.8) | 23.98 (11.4) | 18.00 (9.6) |
| 1 | 18.31 (8.6) | 23.11 (8.1) | 19.15 (7.6) |
| 2 | 18.23 (7.7) | 22.50 (8.0) | 17.99 (8.0) |
| 3 | 18.27 (8.3) | 22.55 (8.2) | 17.92 (8.3) |
| 4 | 17.95 (8.9) | 22.35 (9.1) | 17.62 (9.3) |

Medians: develop **18.27 s**, #812+#786 **22.55 s** (ratio **1.234**), #812 alone 17.99 s (0.985).

**Gate reading:**
- #812 alone: yahoo 0.936 and reddit 0.972 pass (≤ 1.10). #812 doesn't slow cnn either (0.911 and 0.985 in the two runs).
- #812 + #786 on cnn: **every run finishes**, 0 killed, all under 24 s, so the 200 s hang is gone. All are under the old ~25 s target. **But the median is 4.3 s above develop's, so "median ≤ develop's cnn median" FAILS.** The extra time comes with #786's `display: contents` work on cnn, not with #812. #812 is cnn-neutral.

The 10-27 10:35 receipt ("#786 + #812 loads cnn: 28.1 / 20.7 s") probably had the same defect: its frames differed by 0.16% across arms, which is the same signature. Treat it as unproven.

Raw JSONL: `2026-10-27-fl-812-paired-release-timing-cnn-fix.jsonl`.
