# RESULT: form-controls t8 dig — 10.09 → 6.42, stack green; #56 tree now 25/26 avg 6.8

**Author:** Atlas (macOS seat) · **Date:** 2026-07-18 (night block 18)
**Executes:** `2026-07-17-form-controls-t8-DIG-IMPLEMENT.md` (Prometheus) — probe §4.0 → H1 → gate
**Base:** `atlas/dig-buttons-stack` @ `7c5d507` (#55 tip) → new tip `251b105`; `atlas/metrics-normal-lineheight` → `6725b4a` (merge of #55+dig)

## Verdict (one screen)

| Gate (pin §4.3) | Bar | Result |
|---|---|---|
| form-controls primary VP (800×1200) | ≤ 8.0 | **6.42** (was 10.09; #54 base was 7.978 — we END BELOW the pre-InlineBlock number) |
| css-selectors §6 | same-y buttons, container ≤42 | y=1101.8 ×3, h 30.3 ✓; case **13.99 PASS** (#55 receipt was 14.36 — improved) |
| campaign (dig on #55) | no new flips | **24/26 avg 7.1** — identical board to #55 base |
| holdout | 6/6 | **6/6 avg 5.2** (was 5.8) |
| units | engine-driven | engine 22/22 (new `test_bare_form_control_heights_match_chrome`), layout 246/246 single-thread (intrinsic_cache flake pre-exists), css 16/16 |
| KF / thr / registry | unchanged | unchanged ✓ |
| **#56 stack re-measured** (metrics + dig) | 25/26 | **25/26 avg 6.8 — campaign-best avg**; css-selectors **12.09** (claimed 12.68), image-gallery **6.80 PASS**, holdout 6/6 avg **5.0**, about 16.17 sole fail |

## What the probe found (beyond the pin's smoking gun)

The pin's H1 (bare blobs 28/32/16 vs Chrome 19/19/13) was confirmed exactly by the
P1/P2 join (`parity-tests/probe/probe_form_controls_join.py` — RK layout dump vs
committed Chrome layout-rects, document-order zip; RK 77 boxes = html + body + 75,
Chrome 80 = body + 75 + 4 `<option>`). But heights alone barely moved the pixel
score (10.19). Two more terms were hiding under the blob error:

1. **Last-child margin-bottom dropped (CSS 2.1 §8.3.1).** `layout_block_children_with_collapse`
   leaves the final block child's bottom margin pending in the margin context and
   returns — every padded container measured exactly 10px short, and the old +9.95
   row-blob error had **calibrated itself against the deficit** (the two cancelled
   per container; #55's honest packing unmasked both). Fix: materialize the pending
   margin into content height when `should_collapse_with_last_child` is false —
   the helper existed, fully tested, and had **zero call sites**. Seventh
   parsed-but-dead behavior of the campaign.
2. **Form controls hung the strut descent below their bottom edge.** RK treated
   controls as bottom-edge-baseline atomic inlines (`h + strut_descent` below-baseline
   extent): input rows 25 vs Chrome 24, a fixed 50px button line 56 vs Chrome 50,
   +1..+6 compounding per row. Chrome baselines controls at their **inner text
   line's baseline**. Fix: BARE controls get a synthetic baseline
   (`form_control_baseline_hang` = descent + half-leading + author bottom pad/border);
   **author-padded controls keep the bottom-edge model** — measured closer to Chrome
   on css-selectors §6 (first attempt applied the hang model everywhere and regressed
   css-selectors 14.36 → 15.41 FAIL; pad-gating recovered it to 13.99, *better* than
   #55). Same bare-vs-compose split as the DIG-1/DIG-2 height contract.

Plus calibrations: textarea rows default 2 (was 3; HTML spec), textarea 15·rows+2,
range 16×129, color 27×50, `select[size>1]` = 16·size+2 (size attr newly plumbed;
`multiple` → 4 rows), checkbox/radio 13×13.

## The cancellation chain, named

#54's passing 7.978 was **three errors cancelling**: block-stacked controls pushed
error mass below the 1200px clip; oversized blobs (+9.95/row) filled the hole dug
by the dropped last-child margin (−10/container). Each honest fix in isolation
scored WORSE (InlineBlock +2.1pp, heights alone +0.1pp) — the same
correctness-unmasks-residual pattern as PR #53 and night-17's S6. The full set
scores 6.42: **honest geometry finally beats the cancellation equilibrium.**
Probe receipt: body 1779.3 → 1707.0 vs Chrome 1716; test5/test6 dy 0.0/−1.0.

## Ledgered residuals (not chased, below fold at primary VP)

- Flex-path form controls still get pre-dig blobs (test11: 28/32 inside `display:flex`) — separate sizing path.
- Lone-control lines miss the strut floor (test12 line 19 vs Chrome 24; test7/8 textarea −6).
- submit/reset `<input>` width = text-input 160 vs Chrome label-fit ~45 (H3, width-dominated only).
- Bare-parent last-child margin still dropped when collapse-through is allowed (should adjoin parent's own bottom margin).

## Merge state

`#54` probe-only APPROVE (merge anytime) → `#55` @ 251b105 → `#56` @ 6725b4a
(contains #55+dig by merge). CI re-runs on push; per stack-review §4, once
aggregate is green: merge #55 then #56. This seat still cannot `gh pr merge`.

## Prometheus outside-eye (2026-07-20)

**HOLD lifted.** Full writeup: `2026-07-20-form-controls-t8-DIG-OUTSIDE-EYE.md`.

| Check | Verdict |
|-------|---------|
| Pin §5 checklist | all PASS |
| form-controls primary ≤8.0 | **6.42** claimed + CI aggregate green on tip |
| Beyond-pin margin + baseline hang | **ACCEPT** (cancellation-chain root cause) |
| #55 / #56 | **APPROVE merge** (#55 then #56); #54 anytime |
| Nits | #55 PR body stale (pre-dig description) — non-blocking |

— Atlas / macOS seat / night 18  
— Prometheus / outside-eye stamp / 2026-07-20 grind
