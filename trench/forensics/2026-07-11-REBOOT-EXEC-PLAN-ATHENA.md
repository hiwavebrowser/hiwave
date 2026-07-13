# REBOOT EXECUTION PLAN — Athena (Windows seat)

**Author:** Prometheus · **Date:** 2026-07-11  
**Audience:** Athena, cold-start after reboot (Opus 4.8 class). Null memory + exchange intact; **session context is gone.**  
**Authority:** Pete-directed plan of record for this reboot. First read after briefing + exchange sync.

---

## 0. Who you are (30 seconds)

- **Seat:** Athena · Windows · Claude · hiwave-windows at the hub path Pete uses for that seat (typically Windows clone of `hiwavebrowser/hiwave-windows`).
- **Job:** Bring Windows visual parity + instrument honesty up to the **same contracts** as macOS so shared fixes transfer; do not invent a private browser.
- **You implement and open PRs;** Atlas often reviews/merges when Pete’s flow says so. Prometheus **design/review only** — never merge irreversible from that seat.
- **Hard lesson this week:** “waiting on merge” with **no open PR** is operator error. **Branches are not PRs.** After freeze, run `gh pr create`.

---

## 1. Board truth at reboot (re-verify)

| Fact | Value (plan write — **re-measure on Windows**) |
|------|--------------------------------------------------|
| `origin/master` | includes **#12–#19** (cascade, flex, gamma+gradients, flex-wrap, bg-clip:text, fidelity registry, canvas §14.2, form UA font) |
| Open PRs | **none** at plan write — confirm with `gh pr list` |
| macOS peer | campaign **~22/26**, holdout **6/6**, IFC A+B+B2+**C**, advance contract, CI honesty |
| Windows cases | registry exists (~23 cases); **holdout scope still empty** |
| Color contract | **linear CSS → color_to_linear → \*UnormSrgb** (opposite of macOS gamma-bytes→Unorm) |

**First commands after reboot (mandatory):**

```text
git fetch origin && git checkout master && git pull --ff-only
git log -8 --oneline
gh pr list --state open
# Run instrument_smoke.py — expect 3/3 (gamma + gradient midpoint)
# Run full parity suite you have; RECORD campaign P/N @ t15
# If no holdout: scoreboard is incomplete — Phase A fixes that
```

Post one exchange board line so Atlas/Prometheus share the same number.

---

## 2. North star (one sentence)

**Close the layout-quality gap with macOS: stand up holdout truth, then port IFC alignment + advance-contract + vertical-align in that order — so Windows stops being “paint-fixed, layout-stuck” and every Atlas dig becomes a port instead of a rewrite.**

Why this is the highest advancement now:

| You already shipped (do not re-dig) | Still missing (multiplicative) |
|------------------------------------|--------------------------------|
| Gamma + linear gradients + 64-seg midpoint | **Holdout** (overfit invisible without it) |
| bg-clip:text, flex-wrap pack, canvas §14.2 | **IFC parent-only text-align + mixed-inline join** |
| Form UA font (#19), fidelity registry, dim hard-fail | **Advance contract** (DW advances on draw command) |
| Builtins transformed | **vertical-align / Slice C** (parsed dead property on macOS until #44) |

Paint was the right epic last week. **This week the bottleneck is layout contracts macOS already proved.** Porting them is more points-per-hour than inventing a new Windows-only dig.

---

## 3. Mission order (strict)

### Phase A — Truth infrastructure (first session, before big digs)

**A1. Holdout mirror (W1 — highest anti-overfit ROI)**

1. Copy **verbatim** from macOS hub (do not invent DOM):  
   `hiwave-macos/websuite/holdout/*` → your `websuite/holdout/*`  
2. Register six cases with `"scope": "holdout"` + policy “digs must not edit”.  
3. Capture **Windows Chrome for Testing** baselines yourself — **never** copy macOS PNGs.  
4. Run holdout; publish: `campaign P/N | holdout P/N`.  

Expect holdout to look **worse** than campaign at first — that is success (macOS saw 8.8 vs 22.2).

**A2. CI gate contracts (port once, from macOS master scripts)**

After A1, port in **one PR** (Atlas warned: four serial traps if piecemeal):

- empty-report tripwire  
- primary-viewport-only for gate  
- `pixel_runs >= 2` stability (skip require-stable on scout)  
- frozen `known_fail` ceilings per case  
- re-home artifact paths (upload-artifact@v4 strips run-id dirs)

Reference: macOS `scripts/parity_gate.py`, `parity_aggregate.py`, PRs #38–#40; brief `forensics/2026-07-11-ci-gate-honesty-IMPLEMENT.md`.

**Exit A:** holdout numbers exist · instrument_smoke 3/3 · PR gate cannot false-green.

### Phase B — **PRIMARY layout port stack** (main advancement)

Port **contracts**, not line-by-line file dumps. Order is dependency-real:

#### B1. IFC text-align ownership (macOS #31 A+B)

**Portable contracts (Atlas/Prometheus locked):**

1. Leaves **never** self-align; parent line pass owns alignment; shift recorded lines as units (`translate_subtree`).  
2. Fitting text joins the line from cursor 0 (no “first text goes block path”).  
3. Fixture: `parity-tests/repro/mixed-inline-center.html` (engine-agnostic) — expect one centered line for `Some <b>bold</b> text`.

#### B2. IFC B2 mid-line Center/Right (macOS #37)

Only after B1 green on fixture:

- Mid-line split under Center/Right; FLOW ⊕ ALIGN on line 0.  
- Brief: `forensics/2026-07-11-ifc-b2-midline-split-BRIEF.md`  
- Fixtures: `mixed-inline-wrap.html`, `mixed-inline-img.html`

#### B3. Advance contract (macOS #36 + #39)

When you next touch text paint (or after B1):

- `DisplayCommand::Text` carries **DirectWrite layout advances + ascent**  
- Renderer **places**, does not re-shape for width  
- `GradientText` must carry advances too (macOS residual closed in #39)  
- Unit: sum(advances) ≈ measure width ±0.5px  
- Briefs: `2026-07-11-text-stack-unification.md`, `…-advance-contract-IMPLEMENT.md`, `…-gradienttext-advance-carry-IMPLEMENT.md`

#### B4. vertical-align / Slice C (macOS #44)

- Confirm engine **applies** `vertical_align` (was dead property class).  
- Line ascent from member extents + strut floor; img bottom on alphabetic baseline.  
- Portable note in #44 body.  
- Brief: `2026-07-11-ifc-slice-c-baseline-BRIEF.md`

**Exit B:** mixed-inline fixtures green · advance unit test green · short dark page canvas already green (#18) · holdout improves on mixed-inline / toolbar if those were red.

### Phase C — Campaign scoreboard push (only after A + B1 at least)

Use Windows campaign numbers to pick **one** KF page:

| Likely target | Why |
|---------------|-----|
| card-grid / flex | #16 helped; residual may be max-content / track sizing |
| builtins forms | DIG-1 height compose + UA font partially ported — finish with probe fixtures |
| sticky / settings class | Port Atlas fixes only when you have a **Windows probe** matching |

**Method:** same instrument-first as Atlas — minimal repro, one cause per PR, freeze branch when ready, **always `gh pr create`**.

### Phase D — Continuous

1. **No 3rd open PR** until current open set ≤2 (or Pete overrides).  
2. **Freeze discipline:** ready branch → open PR → no silent tip moves during merge.  
3. **Dual-seat:** if fix is algorithm-shaped (flex free-space, grid rows), broadcast portable site + fixture to Atlas.  
4. Color: never “fix” midpoint by raising threshold; smoke probes are law.  
5. Do not copy macOS baseline PNGs or claim macOS holdout scores as yours.

---

## 4. Method rules (cold Opus 4.8)

1. **Read the portable note before the macOS diff.** Contracts first; code second.  
2. **Probe on Windows** even if macOS already green — DW vs CT will lie to you if you skip.  
3. **One PR = one contract.** “IFC+advance+valign mega PR” will race and drop commits (#12/#13 class).  
4. **Open the PR the same hour the branch is ready.** Freeze saves commits; it does not create GitHub PRs.  
5. **If stuck:** finish Phase A (holdout+CI) rather than half-port IFC. Truth infrastructure always advances the org.

---

## 5. Key references

| Need | Where |
|------|--------|
| Fidelity plan W1–W6 | `trench/forensics/2026-07-11-test-fidelity-HARDENING.md` |
| Gradient midpoint lock | `…/2026-07-11-gradient-midpoint-gamma-LOCK.md` |
| IFC sketch | `trench/IFC_PHASE3_SKETCH.md` |
| B2 / C briefs | `forensics/2026-07-11-ifc-b2-*`, `…-ifc-slice-c-*` |
| Advance contract | `…-advance-contract-IMPLEMENT.md` |
| Canvas / form ports you already did | PRs #18, #19 — do not redo |
| macOS holdout HTML | `hiwave-macos/websuite/holdout/` (copy text only) |

---

## 6. Doorbell

- Post board after Phase A and after each B* merge.  
- `to_atlas`: “ported contract X, fixture path, Windows score delta”.  
- Ask Prometheus for design only when contract is ambiguous — not for rubber-stamp.

---

## 7. Success criteria

| Horizon | Done means |
|---------|------------|
| First session | Holdout suite measured + board on exchange · smoke 3/3 |
| This cycle | B1 IFC align port **merged** with mixed-inline-center green |
| Stretch | B2 + advance contract landed · holdout ≥3/6 · campaign moving |
| Fail | New private HTML “suite”, threshold inflation, or “waiting on merge” with zero open PRs |

---

## 8. Explicit non-goals

- Re-solving gamma double-encode (done)  
- Fragment-shader gradients before IFC ports  
- Matching macOS PR numbers as vanity  
- Full WPT import this cycle  

---

**Prometheus standing offer:** design review on IFC/advance PRs when opened. No merges from Prometheus.

— Prometheus
