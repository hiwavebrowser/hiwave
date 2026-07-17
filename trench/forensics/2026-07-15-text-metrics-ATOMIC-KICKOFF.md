# Atomic text-metrics epic — KICKOFF (post night-15)

> **Status:** Design complete 2026-07-15 grind tick. **Blocker framing SUPERSEDED 2026-07-16** by night-16 form-coupling falsification — see `2026-07-16-text-paint-FIDELITY-RESIDUAL.md`.  
> **Audience:** Atlas (execute), Athena (port after macOS land), Prometheus (outside-eye when PR opens).  
> **Exists in service of:** honest line-height:normal + form dependents so campaign can leave the text-metrics wall.  
> **Supersedes (hypothesis phase):** `2026-07-13-text-metrics-ATOMIC-IMPLEMENT.md` §§1–3 gallery hunt — residual inventory §4 still useful as demoted cleanup; §4.4 “form = last blocker” **falsified night-16**.  
> **Companions:** `2026-07-14-pr53-grid-span-gap-REVIEW.md` (APPROVE) · Atlas night-15 digest · #52 MERGED instruments · **night-16** `2026-07-16-lineheight-metrics-FALSIFIES-FORM-COUPLING.md` + residual rewrite above.

## 0. One-liner

**Gallery confound is CLOSED** (#53 grid span gutters). Dual-patch still flips gallery → **6.80 PASS**.  
**Night-16 update:** form recompose is **not** the last blocker (falsified). Metrics model is correct but **unlandable alone** (css-selectors 10.03→15.14). Next HiWave unit = **PAINT-0 glyph-atlas / text-paint probe** per `2026-07-16-text-paint-FIDELITY-RESIDUAL.md`. Merge #53 still first.

## 1. Live pins (2026-07-15 grind)

| Signal | Value | Implication |
|--------|------:|-------------|
| `origin/master` | `8d7264d` (#51 merge tip; local seat may differ) | #52 instruments merged earlier; #53 **not** on master |
| Open PR | **#53** `atlas/grid-span-gap` @ `d8b89001` | MERGEABLE + green (prior Prometheus APPROVE stands) |
| Campaign on master | 24/26 @ t15, avg ~7.1, holdout 6/6, KF 7 | Board unchanged until model lands |
| `LineHeight::Normal` | still `font_size * 1.2` in `rustkit-css` | Wall claim holds; ENGINE metrics path still required |
| Gallery dual-patch (Atlas night-15) | grid alone 12.88→**13.60**; grid+model →**6.80 PASSES t10** | Must land model on post-#53 tip; grid alone is honest slight worsen |
| Gallery root cause | `rustkit-layout/.../grid.rs` span tracks omitted `gap*(N-1)` (css-grid-1 §12.5) | **Not** line-height coupling (H3-class layout, closed by #53) |
| Remaining named blocker | form-control recomposition under metrics | ATOMIC-IMPLEMENT §4.4 only |

### 1.1 Decision answers (Atlas night-15 → Pete / seats)

| # | Question | Prometheus call |
|---|----------|-----------------|
| 1 | Merge #53 standalone vs hold inside atomic? | **MERGE #53 now.** Spec-correct, exact vs Chrome on span tracks, cannot red-lock CI (gallery stays known-fail under KF), de-risks epic by removing biggest confound. Cost: ~0.72pp on one already-noisy meter. |
| 2 | Greenlight text-metrics epic? | **YES.** Payoff measured (gallery 6.80 under dual patch). Scope = ENGINE metrics + form recompose + flex twins. |
| 3 | Concurrent Atlas seats / shared checkout? | Pete/ops — worktree allowlist; not a design blocker for this PR. |

## 2. What closed (do not re-hunt)

| Prior hypothesis (ATOMIC 07-13) | Verdict after night-15 |
|---------------------------------|------------------------|
| H1 header Y-cascade as primary gallery residual | **Secondary.** Under metrics, text boxes exact; residual was grid row inflation. |
| H2 abs caption paint coupling | Not the board driver once grid fixed. |
| H3 abs-in-grid / track sizing | **CLOSED by #53** — span charged full size without gutter credit; `span 2` @ min-height 416 / gap 16 → 208+208 vs Chrome 200+200. |
| object-fit dig | Still **falsified** (0 `<img>` on gallery). Spec debt only. |
| Model-only merge without #53 | **Forbidden** — model alone previously red-locked board (24→23); dual path is the measured story. |

**Method that worked (portable):** two-model A/B probe — identical box trees join on path; attribute residual without selector plumbing. Athena: same method once chrome-148 rects exist.

## 3. Residual `* 1.2` / form inventory (re-verified this tick)

Pin: local `hiwave-macos` tree (read-only). ENGINE.patch still retargets `line_height.to_px` → `resolve_line_height`; these sites are **not** rewritten by the patch alone.

### 3.1 Hard-coded form / UA chrome (must twin lib ↔ flex)

| Site | Formula (live) | Atomic action |
|------|----------------|---------------|
| `layout/lib.rs` ~723 | TextArea: `fs*1.2*rows+8` | Re-measure under metrics; rewrite only if |Δh|≥0.5 vs Chrome |
| `layout/lib.rs` ~732 | Checkbox/Radio: `fs*1.2` square | **Likely keep** (UA chrome, not line-height); probe first |
| `layout/lib.rs` ~717 / 728 / 736 | TextInput / Button / Select blob heights (`fs*1.5+8/12`) | Re-validate DIG-1/2 under metrics; author-pad branch preferred |
| `layout/flex.rs` ~701–708 | FormControlType arms (same formulas) | **Mirror lib** — both or neither |
| `layout/flex.rs` ~983–1077 | Axis::Vertical twins for same controls | **Mirror lib** |
| `layout/forms.rs` ~117, 147 | caret / selection height `fs*1.2` | Low board impact; twin after controls settle |
| `rustkit-text/.../macos.rs` ~638 | glyph atlas `ceil(fs*1.2)` | **OUT OF SCOPE** this PR |

### 3.2 Form recompose rules (unchanged contract)

1. Chrome control border-boxes from committed `css-selectors` rects (no live Chrome required).  
2. Under metrics model, list RK control heights.  
3. Adjust **only** formulas that miss Chrome by ≥0.5px.  
4. Prefer keeping `single_line_box` / author-pad branch; change blob constants if bare controls miss.  
5. **Never** lower KF ceilings to hide a miss.  
6. After recompose: css-selectors must not re-red t15.

## 4. Land order (Atlas — execution checklist)

```text
[x] 0. Merge #52 (instruments) — DONE
[ ] 1. Merge #53 (grid span gutters) — OPEN @ d8b89001; APPROVE stands; do this FIRST
[ ] 2. Worktree off post-#53 master: apply ENGINE metrics path; build; do NOT merge model-only
[ ] 3. Confirm dual-patch receipt on gallery (expect ~6.8 / PASS t10 class) before form churn
[ ] 4. Recompose form controls (§3) under metrics; flex twins mandatory
[ ] 5. Residual *1.2 decisions table in PR body (keep / rewrite / defer)
[ ] 6. Doc honesty: Normal comment + resolve path rustdoc (Blink-rounded normal px)
[ ] 7. Full campaign gate (see §5)
[ ] 8. Single PR (or stacked with ONE merge gate). Title:
       "fix: line-height:normal from font metrics + form dependents (atomic)"
[ ] 9. Port note: Athena ports call sites, not the model; shared crates inherit grid fix
```

### Explicit anti-patterns

- Model-only merge on pre-#53 master  
- Re-opening gallery |Δy| hunt after #53 (closed)  
- object-fit dig on gallery  
- KF / threshold games  
- Rewriting glyph atlas height in the same PR  
- Mixing Tank estimator work into this PR  

## 5. Merge gate (atomic PR)

| Gate | Bar |
|------|-----|
| Campaign | **≥24/26** @ t15 (stretch **25/26** if gallery clears t15 under dual patch) |
| Holdout | **6/6** green |
| `css-selectors` | not re-red t15 after form recompose |
| `image-gallery` | dual-patch class: expect large improve vs master 12.88; do not hide grid-alone 13.60 as “metrics fail” |
| `about` | should move if pure metrics wall; not a hard fail if residual is non-metrics |
| Unit | span-distribution tests drive **engine**, not hand-simulated arithmetic (night-15 smell) |
| CI | pr-swarm + aggregate honest; no ceiling lower |

If board is still 23/26 with a **named** residual after dependents: stop, one-pager, no constant thrash.

## 6. Outside-eye checklist (Prometheus when PR opens)

- [ ] Base includes #53 (or equivalent gutter credit) — reject model-only on old master  
- [ ] PR body has dual-patch or A/B gallery number, not only final score  
- [ ] Form formula table: each site keep/rewrite with Chrome Δ  
- [ ] flex.rs twins match lib.rs for every touched control  
- [ ] No KF ceiling lowers; no glyph-atlas scope creep  
- [ ] Campaign/holdout bars in §5 met  
- [ ] Shared-crate port note for Athena present  

## 7. Athena / Windows

- Grid gutter fix is in **shared** `rustkit-layout` — Windows inherits once crate syncs.  
- No engine port of metrics until macOS atomic lands.  
- When landing: port `resolve_line_height` call sites; do not re-derive Blink rounding.  
- Test smell sweep: any test that re-implements layout math in the test body without calling the engine.

## 8. Priority vs other lanes (honest)

| Lane | vs this kickoff |
|------|-----------------|
| Website Tank blurb | Still highest **product** gravity (launch honesty) — parallel, different repo |
| Tank C3a sticky | Still highest **estimator** honesty — parallel, different repo |
| Hero token reframe | Public credibility residual — parallel |
| This atomic | Highest **HiWave board** lever once #53 merges |

No shared files with Tank/website. Atlas may sequence product vs trench by Pete gravity; design seats do not block each other.

## 9. Summary for digests / exchange

> **2026-07-15:** Night-15 closed gallery unknown as grid span gutters (#53). Dual-patch flips gallery 12.88→6.80 PASS t10; grid alone 13.60 known-fail. Prometheus re-confirms MERGE #53 then atomic = metrics model + form recompose only. Residual inventory re-pinned on lib/flex/forms. Gate ≥24/26 holdout 6/6; outside-eye when atomic PR opens.

— Prometheus (design seat), 2026-07-15 grind tick
