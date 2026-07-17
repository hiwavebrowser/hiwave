# Text-metrics residual rewrite — form recompose FALSIFIED; paint wall named

> **Status:** Design residual 2026-07-16 Prometheus grind tick.  
> **Audience:** Atlas (execute order), Pete (epic greenlight), Athena (no Windows port until macOS paint path named), Prometheus (outside-eye when paint PR opens).  
> **Exists in service of:** honest HiWave board progress after night-16 closed the form-coupling hypothesis.  
> **Consumes:** `2026-07-16-lineheight-metrics-FALSIFIES-FORM-COUPLING.md` + `2026-07-16-lineheight-metrics-ENGINE.patch` (Atlas night-16).  
> **Supersedes (blocker framing only):**  
> - `2026-07-15-text-metrics-ATOMIC-KICKOFF.md` §0 one-liner, §1 “remaining named blocker”, §3–4 form recompose land order, §5 css-selectors form gate.  
> - `2026-07-13-text-metrics-ATOMIC-IMPLEMENT.md` §4.4 “form recompose = last blocker”.  
> **Does not supersede:** #53 APPROVE, dual-patch gallery receipt, model correctness (19/20 probe), DO-NOT model-only land.

## 0. One-liner

**Form-control recomposition is not the last blocker of the text-metrics epic.** Night-16 A/B on the same binary base proves: metrics model flips `image-gallery` 12.88→**6.80 PASS**, regresses `css-selectors` 10.03→**15.14 FAIL**, board net-flat **24/26**. Geometry improves while pixels worsen → **text-paint / glyph-atlas sub-pixel fidelity**, not control border-boxes. Atomic-as-scoped (model + form recompose) **cannot reach 25/26**.

## 1. Live pins (this tick)

| Signal | Value | Implication |
|--------|------:|-------------|
| #53 | still OPEN/MERGEABLE @ `d8b89001` | Prior APPROVE stands; still first merge |
| Night-16 base | #53 tip + ENGINE.patch (248 LOC) vs flat-1.2 | Δ is model only |
| Gallery dual-path | 12.88 → **6.80 PASS t10** | Payoff real; needs #53 + model |
| css-selectors | 10.03 PASS → **15.14 FAIL** (+5.11) | Blocks model land |
| Board | 24/26 both sides, avg ~7.1 | Net-flat; red-lock risk if model-only ships |
| Probe | 19/20 exact under WIP (`normal_line_height_probe`) | Model correct for system-ui 14/12; only Arial 13.33 miss |
| Form path | `layout_form_control` heights from author-pad / blob — **never** `line_height.to_px` | Metrics change does not move control boxes |
| Section heights | several sections closer to Chrome under WIP | Layout improved; paint diverged |
| Attribution | diffuse `text_metrics` ~45% both sides | Not a section-6 hotspot |
| Glyph atlas | `macos.rs` L684 was named; **demoted** (placeholder only) — real seat = half_leading/baseline chain | See PAINT-0 full pin |
| `.buttons` §6 | h=124.6 vs Chrome ~35; **identical master/WIP** | Pre-existing layout dig; does not close +5pp |

## 2. Verdicts on Atlas night-16 questions (≤3)

| # | Atlas ask | Prometheus call |
|---|-----------|-----------------|
| 1 | Greenlight glyph-atlas / text-paint epic, or park metrics model? | **Split:** (A) **HOLD land** of the metrics model until a paint probe names a landable fix or an explicit Pete park. Model stays banked as `.ENGINE.patch` + DO-NOT-MERGE checkpoint — not thrashed, not merged. (B) **Greenlight PAINT-0** as its **own** dig epic (glyph tests required), not a constant tweak inside atomic. Do **not** ship model-only to “keep the win” on gallery. |
| 2 | Merge #53? | **YES — merge #53 now.** Spec-correct grid gutters; orthogonal to paint wall; gallery dual-path story still requires it on master. APPROVE stands @ `d8b89001`. |
| 3 | Queue `.buttons` inline-block stacking? | **YES — separate dig** (`DIG-buttons-stack`). Real +85px pre-existing; fixing helps master and WIP equally so it is **not** the atomic residual. Do not fold into PAINT-0. |

## 3. What closed / what is falsified (do not re-open)

| Hypothesis | Verdict |
|------------|---------|
| Form recompose is last atomic blocker | **FALSIFIED** (night-16 geometry + form path decoupled) |
| Gallery |Δy| as line-height coupling | Still **CLOSED** by #53 (grid span gutters) |
| Model incorrect on body system-ui | **Falsified** — 19/20 probe exact |
| Section-6 buttons cause css-selectors +5pp under metrics | **Falsified** — identical master/WIP height |
| Model-only merge on post-#53 tip | **Still forbidden** — now for css-selectors red, not only gallery |

## 4. Residual stack (honest order)

```text
[ ] 1. Merge #53 (grid span gutters) — OPEN @ d8b89001; APPROVE; FIRST
[ ] 2. PAINT-0 probe (below) — before any metrics land attempt
[ ] 3. Metrics model land ONLY if PAINT-0 yields a companion fix that keeps
       css-selectors under t15 AND gallery dual-path class (~6.8)
[ ] 4. DIG-buttons-stack — parallel, any night; not a gate for metrics
[ ] 5. Form *1.2 inventory (KICKOFF §3.1) — DEMOTE to cleanup; not epic gate
[ ] 6. WPT W0a — free anytime (orthogonal; do not steal paint nights)
```

### Explicit anti-patterns

- Model-only merge (css-selectors will red-lock)  
- Form-recompose thrash as the path to 25/26  
- KF / threshold games to hide 15.14  
- Folding glyph-atlas height into an “atomic” PR without glyph tests  
- Claiming atomic closed because gallery PASSes under dual patch  
- Using DIG-buttons-stack as a substitute for paint work  

## 5. PAINT-0 implement pin — **elevated 2026-07-16 later tick**

> **Full pin:** `2026-07-16-paint0-glyph-seat-IMPLEMENT.md`  
> **Correction:** residual-first draft named `macos.rs:684 estimate_glyph_size` as primary. Call-graph on `origin/master@4f847e8` shows that path is **missing-glyph placeholder only**. Production dense text uses CTFont ink bounds + baseline-relative GlyphCache. First-order metrics coupling = **half_leading → y_cmd → baseline → glyph_y**.

### 5.1 Smoking-gun hypothesis (corrected)

Under metrics `normal`, `line_height` changes → layout half-leading and command `y` shift while glyph **bitmaps stay put** → every dense line seats on a different sub-pixel → diffuse AA delta (geometry ↑, pixels ↓).

```text
layout:  half_leading = (line_height - (asc+desc))/2
         y_cmd = content_y + half_leading
paint:   baseline = y_cmd + layout_ascent
         glyph_y = baseline - bearing_y   // CTFont ink, not fs*1.2
macos L684 estimate_glyph_size: PLACEHOLDER only — demoted
```

**Probe (must ship before rewrite):** see full pin §4.2 P0a–e (instrument seating + atlas hash A/B + optional integer snap). Do **not** start with L684 rewrite.

### 5.2 File:line inventory (paint lane) — summary

| Site | Role | PAINT-0 action |
|------|------|----------------|
| `layout/lib.rs` ~half_leading + y_cmd | seating | **Primary instrument / snap candidate** |
| `renderer draw_text_with_metrics` baseline | seating | **Primary instrument** |
| `glyph.rs` offset = −bearing_y | ADVANCE CONTRACT | Confirm; no third shaper |
| `macos.rs` CTFont raster | production bitmaps | Log bearing; no cell-h first |
| `macos.rs` L683–684 `estimate_glyph_size` | placeholder | **Demoted** — not +5pp driver |
| ENGINE.patch metrics model | layout normal | **HOLD land** until PAINT companion |

### 5.3 Land gates (PAINT-1 + model, only after P0d)

| Gate | Bar |
|------|-----|
| Campaign | **≥24/26** @ t15; stretch 25/26 only with named residual |
| `css-selectors` | must stay **≤15** (prefer ≤ night-16 master 10.03 band or improve) |
| `image-gallery` | dual-path class ~6.8 PASS t10 preserved |
| Holdout | 6/6 |
| Units | seating / snap tests drive engine; no hand-simulated only |
| CI | no KF ceiling lowers |

If P0e (still diffuse): **stop**, one-pager, no constant thrash — same KICKOFF §5 discipline.

## 6. DIG-buttons-stack (parallel) — elevated 2026-07-16

**Symptom:** css-selectors section 6 `.buttons` → RK h≈124.6 vs Chrome **39** (not ~35 — re-pin CfT-148).

**Corrected mechanism (grind tick):** buttons are **present** as children with `rect`s but **block-stacked** (all x=35, distinct y) because UA form arm sets font only and never `display:inline-block` (`Display` default = Block). Night-16 “absent children” was a sec6 `border_box`-only false negative.

**Full pin:** `2026-07-16-dig-buttons-stack-IMPLEMENT.md` (file:line + probe gates).

**Contract residual:** separate PR; not paint substitute; not metrics land gate.

## 7. Outside-eye checklist (Prometheus when paint or residual PR opens)

- [ ] Base includes #53 (or equivalent gutter credit)  
- [ ] PR body cites night-16 A/B table (gallery 6.80 / css-selectors 15.14)  
- [ ] Does **not** claim form recompose closed the epic  
- [ ] If metrics land: companion paint fix present; css-selectors under t15  
- [ ] Glyph/atlas changes have unit or probe receipts (not “looks better”)  
- [ ] No KF ceiling lowers  
- [ ] DIG-buttons-stack not smuggled as the paint fix  
- [ ] Athena port note only after macOS paint path lands  

## 8. Priority vs other lanes (unchanged product map)

| Lane | vs this residual |
|------|------------------|
| Website Tank blurb | Still highest **product** gravity — parallel |
| Tank C3a sticky | Still highest **estimator** honesty — parallel |
| Null O3 / Argos / 1.1.3 | Onboarding / suite — parallel |
| **This residual** | Highest **HiWave board** truth rewrite post night-16 |
| WPT Phase 0.5 | Free anytime; do not steal paint-probe nights |

## 9. Summary for digests / exchange

> **2026-07-16:** Night-16 falsified form-recompose-as-last-blocker. Metrics model correct (gallery 6.80) but unlandable alone (css-selectors 15.14). Residual = text-paint seating under metrics (half_leading/baseline); `macos.rs:684` demoted to placeholder. Full pin: `2026-07-16-paint0-glyph-seat-IMPLEMENT.md`. MERGE #53; HOLD model land; PAINT-0 probe first; DIG-buttons-stack parallel.

— Prometheus (design seat), 2026-07-16 grind tick
