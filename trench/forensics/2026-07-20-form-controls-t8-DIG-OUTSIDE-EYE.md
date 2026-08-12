# Outside-eye: form-controls t8 dig RESULT — HOLD lifted on #55 / #56

**Author:** Prometheus · **Date:** 2026-07-20 (grind tick, headless)  
**Lane:** design / outside-eye only — **no merge, no force-push, no spend**  
**Consumes:**  
- Pin `2026-07-17-form-controls-t8-DIG-IMPLEMENT.md` (Prometheus)  
- RESULT `2026-07-18-form-controls-t8-DIG-RESULT.md` (Atlas night 18)  
- Stack review `2026-07-17-pr54-55-56-STACK-REVIEW.md` (prior HOLD)  
**Live tips @ review:**  
- **#54** `dac2623` · OPEN · mergeable · prior APPROVE stands  
- **#55** `251b105` · OPEN · mergeable · **dig landed on tip** (was `7c5d507` InlineBlock-only)  
- **#56** `6725b4a` · OPEN · mergeable · base = `#55` tip `251b105` (dig included by merge)

---

## 0. Verdict (one screen)

| PR | Prior | **Now** | Action |
|----|-------|---------|--------|
| **#54** PAINT-0 probe | APPROVE | **APPROVE** | Merge anytime (probe-only; zero behavior) |
| **#55** DIG-buttons + bare-size dig | APPROVE design / **HOLD merge** (form-controls 10.09 > t8) | **APPROVE design + APPROVE merge** | Merge after CI green (already green @ review) |
| **#56** metrics-normal | APPROVE design / **HOLD merge** (inherits #55) | **APPROVE design + APPROVE merge after #55** | Merge stack **#55 → #56** |

**Sole prior merge hold was form-controls primary ≤ 8.0.** Dig receipts claim **6.42** (was 10.09; pre-InlineBlock #54 base 7.978). Live GitHub: **pr-aggregate PASS** + all four **pr-swarm PASS** on both #55 and #56. **HOLD lifted.**

Prometheus does **not** merge. Atlas owns land order.

---

## 1. Pin checklist (`form-controls-t8-DIG-IMPLEMENT` §5)

| Check | Result | Evidence |
|-------|--------|----------|
| InlineBlock retained for form UA arm | **PASS** | Dig does not revert #55 UA `display = InlineBlock`; §6 still same-y |
| Bare single-line heights → Chrome ~19 | **PASS** | Commit `251b105`: bare path `single_line_box(19.0 * ua_scale)` for input/button/select; unit `test_bare_form_control_heights_match_chrome` |
| Author-pad compose still ~31 for pad 8+8 | **PASS** | Explicit contract in unit + RESULT (pad-gated baseline hang); css-selectors **13.99 PASS** (was 14.36 under #55-only) |
| form-controls primary ≤ 8.0 | **PASS** | RESULT: **6.416** (gate line claimed 10.090 → 6.416); CI aggregate green on tip |
| sec6 / css-selectors not regressed past #55 | **PASS** | S6 y=1101.8 ×3, h 30.3; case **13.99** improved vs #55's 14.36 |
| No thr/scope/KF silent moves | **PASS** | RESULT + commit message: KF/threshold/registry **unchanged** |
| Paint-only not claimed as layout fix | **PASS** | All four fixes are layout/engine sizing + margin collapse + baseline hang |

### Beyond-pin scope (ACCEPT — not a reject)

Pin preferred H1 = bare height alone. Atlas found **cancellation chain** and fixed three co-conspirators:

1. **Bare border-box sizes** (pin H1 Option B + H2/textarea/range/color/select size) — in pin  
2. **Last-child bottom margin materialize** (CSS 2.1 §8.3.1) — **beyond pin**, justified: helper `should_collapse_with_last_child` had **zero call sites**; −10/container cancelled old +9.95 row blobs  
3. **Bare form-control synthetic baseline hang** — **beyond pin**, justified: strut-descent hang under bottom-edge baseline inflated line boxes; pad-gated so S6 author-pad path not broken  
4. **textarea rows default 2** (HTML/Chrome) — small honesty fix  

**ACCEPT as one dig unit.** Isolation would have scored worse (RESULT: heights alone +0.1pp). Same correctness-unmasks-residual pattern as #53 / night-17 S6. Do **not** demand a split PR after green receipts.

---

## 2. Live GitHub pins (2026-07-20 grind)

| Pin | Value |
|-----|------:|
| #55 head | `251b1051adf184b2029bd8e5429e07a7b9630deb` |
| #56 head | `6725b4a42acc44314d53ff9297c05951e04485c4` |
| #56 base | `251b105…` (= #55 tip; dig included) |
| #54 head | `dac2623…` |
| mergeable | all three **true** |
| #55 CI | pr-aggregate **pass**; pr-swarm 0–3 **pass**; audit **pass**; collect-metrics **pass** |
| #56 CI | pr-aggregate **pass**; pr-swarm 0–3 **pass** (run `29633516572` family) |
| #55 net diff | +348 / −10 (InlineBlock + dig; was ~+91 pre-dig) |

### RESULT campaign claims (Atlas; design-trust + CI corroboration)

| Gate | Bar | Claimed |
|------|-----|---------|
| form-controls primary 800×1200 | ≤ 8.0 | **6.42** |
| css-selectors | no regress past #55 | **13.99 PASS**; S6 same-y |
| campaign (dig on #55) | no new flips | **24/26 avg 7.1** |
| holdout | 6/6 | **6/6 avg 5.2** |
| #56 full stack | 25/26 | **25/26 avg 6.8** (campaign-best); gallery **6.80 PASS**; css **12.09** |
| units | engine-driven bare heights | engine 22/22 new bare-height test; layout 246/246 |

This seat did **not** re-run local pixel sim (no GPU grind requirement). CI green + commit message + RESULT + unit shape are enough to lift HOLD under standing outside-eye bar for this fleet.

---

## 3. Mechanism confirmation (design read of dig commit)

Smoking gun chain from RESULT matches probe+code:

```text
#54 form-controls 7.978 PASS  = three errors cancelling
  block-stack (pre-InlineBlock) hid error below VP clip
  + oversized bare blobs (+9.95/row)
  + dropped last-child margin (−10/container)

#55 InlineBlock alone → 10.090 FAIL  (honest packing unmasked residual)
dig (251b105)          → 6.42 PASS   (honest geometry beats cancellation)
```

Code symbols present in `251b105` diff (spot-checked via GitHub API):

- bare `single_line_box(19.0 * ua_scale)`  
- `form_control_baseline_hang` + author_pb_v gate  
- `should_collapse_with_last_child` call site + margin materialize  
- `test_bare_form_control_heights_match_chrome`  
- textarea `unwrap_or(2)`; `size` / `multiple` plumb  

**DO-NOT list honored:** no InlineBlock revert; no thr/scope raise; no known_fail; no metrics fold into dig; no paint-first thrash.

---

## 4. Ledgered residuals (not merge blockers)

From RESULT — accept as post-merge dig chores, not #55/#56 holds:

| Residual | Note |
|----------|------|
| Flex-path form controls still pre-dig blobs (test11) | Separate sizing path |
| Lone-control lines miss strut floor (test12 / textarea −6) | Below primary-VP fold |
| submit/reset width 160 vs Chrome label-fit ~45 | Pin H3 optional; width-dominated only |
| Bare-parent last-child margin when collapse-through allowed | Smaller residual |
| `about` still sole campaign fail (~16.17) | Named text wall; out of dig scope |

---

## 5. Nits (non-blocking)

1. **#55 PR body is stale.** GitHub description still sells InlineBlock-only night-17 story; tip includes dig `251b105`. Atlas should amend body (or land dig RESULT one-liner in merge commit) so merge receipt matches tip.  
2. **#56 PR body** still frames pre-dig form-controls hold in historical arc — fine as history; confirm dig base is visible to reviewers.  
3. Optional: cite dig RESULT path in PR #55 body for future archaeology.

None block APPROVE.

---

## 6. Merge order (Atlas)

```text
1. #54  PAINT-0 probe          — anytime (orthogonal)
2. #55  dig-buttons + dig      — NOW (t8 green; CI green)
3. #56  metrics-normal         — immediately after #55 (base is #55 tip)
```

Do **not** merge #56 before #55. Do **not** wait for flex-path residual. Do **not** seed Tank ceilings or claim website Tank from this stack.

**Athena:** still no Windows port until macOS #55+#56 on master.

**Pete:** no decision required (no known_fail / thr path).

---

## 7. Chapter status

| Item | Status |
|------|--------|
| form-controls t8 dig **design** | **CLOSED** (pin executed; RESULT banked) |
| form-controls t8 dig **outside-eye** | **CLOSED this tick** — APPROVE merge |
| Stack #54/#55/#56 | **READY TO LAND** (Atlas merge lane) |
| Post-merge Prometheus | standby only if land regresses aggregate; else website Tank / C3a residual / null #83+#84 |

— Prometheus / outside-eye only / 2026-07-20 grind tick
