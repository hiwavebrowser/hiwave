# REBOOT EXECUTION PLAN — Atlas (macOS seat)

**Author:** Prometheus · **Date:** 2026-07-11  
**Audience:** Atlas, cold-start after reboot (Opus 4.8 class). Null memory + exchange intact; **session context is gone.**  
**Authority:** Pete-directed plan of record for this reboot. Treat this as your first read after `null_briefing` + `null exchange sync` + last 20 stream lines.

---

## 0. Who you are (30 seconds)

- **Seat:** Atlas · macOS · Claude · hiwave-macos **hub** at `~/Repos/hiwave/hiwave-macos` (not stale `Repos/hiwave-macos`).
- **Job:** Ship pixel parity vs **Chrome for Testing 148.0.7778.216** on the campaign + holdout; keep CI honest; port portable notes to Athena.
- **You merge** on your seat when review is done (Prometheus does **not** merge irreversible work). Pete gates threshold policy only.
- **Null store:** your Atlas personality store (not Prometheus). Exchange is the org bus.

---

## 1. Board truth at reboot (re-verify before coding)

| Fact | Value (as of plan write — **re-measure**) |
|------|-------------------------------------------|
| `origin/master` tip | includes **PR #44 IFC Slice C** (`7563688` class) |
| Open PRs | **none** (start clean) |
| Campaign | **~22/26 @ t15**, avg **~8.3** (css-selectors **PASS** ~10) |
| Holdout | **6/6 @ t15**, avg **~5.8** (do not break) |
| Pin | `cases/registry.json` → chrome-148, dpr 1 |
| known_fail (7) | `about`, `settings`, `sticky-scroll`, `image-gallery`, `gradient-no-radius`, `gradient-radius-only`, `images-intrinsic` |

**First shell after reboot (mandatory):**

```bash
cd ~/Repos/hiwave/hiwave-macos   # hub only
git fetch origin && git checkout master && git pull --ff-only
git log -5 --oneline
gh pr list --state open
# full suite — use your normal parity_test / swarm path; record the number
# must print: campaign P/N @ t15 | holdout P/N | KF list
```

If numbers disagree with this table, **your measure wins** — update the digest, do not “fix” the plan’s numbers.

---

## 2. North star (one sentence)

**Clear product-chrome known_fails that still hurt real browser UI: land `settings` under t15, then cut `sticky-scroll` under t15 — without regressing holdout 6/6 or re-opening soft CI gates.**

Why this beats other options:

| Candidate | Why not first now |
|-----------|-------------------|
| WPT Tier-1 | High value long-term; **too wide** for cold Opus 4.8 first session; keep as Phase 2 |
| More IFC depth (nested inline frag) | Slice A/B/B2/C just shipped; diminishing returns vs product pages |
| about letter-spacing | Smaller product surface; do **after** settings if residual is text |
| Random micro polish | Coding to the meter — holdout already green |

`settings` + `sticky-scroll` are the two remaining **product-shaped** KF cases with highest user-visible impact. Micros (gradient-*) are paint residual; `image-gallery` is often asset/network — third priority.

---

## 3. Mission order (do not reorder)

### Phase A — Boot + truth (≤45 min, no engine PR)

1. `null_briefing` + last exchange messages (`null exchange sync`; read Prometheus reboot plan + Atlas/Athena last 5).  
2. Hub path check: `git rev-parse --show-toplevel` must be under `Repos/hiwave/hiwave-macos`.  
3. Full campaign + holdout measure; write **one** noon-style board line to exchange.  
4. Confirm CI still honest: empty aggregate cannot pass (PRs #38–#40). Do not weaken gates.

### Phase B — **PRIMARY: settings under t15** (1–2 solid sessions)

**Goal:** `settings` known_fail **cleared** (diff ≤15, flag removed, ratchet permanent).

**Historical root-cause family (start here, re-probe — do not trust memory):**

1. Flex item **ignores definite height** when height comes from children sum (toggle rows ~26px → 40–67px).  
   - Fixture exists: `parity-tests/repro/toggle-height.html`  
   - Method: `parity-tests/repro/y_table.py` at **case viewport 1024×768** (not 1280×800).  
2. `position:absolute; inset:0` fill of parent (slider/toggle track).  
3. Secondary: margin-collapse h1→subtitle, etc. — only after (1)(2).

**Execution loop (instrument-first — non-negotiable):**

```text
1. Capture Chrome + RustKit settings at 1024×768
2. y_table / first-divergence element (not heatmap guess)
3. Minimal HTML repro that fails Chrome vs RK the same way
4. One root cause → one PR → re-measure settings + full suite + holdout
5. If settings ≤15: clear known_fail in registry, CI ratchets
```

**Exit B:** settings PASS @ t15 · holdout still 6/6 · no new KF · PR merged.

### Phase C — **PRIMARY-2: sticky-scroll under t15** (after B)

**Goal:** sticky-scroll ≤15, clear KF (currently ceiling ~19.3; was ~48 before sticky epic).

**Approach:**

1. Do **not** re-open “sticky never works” — epic day-1 already PASS’d sticky-scroll once at higher threshold; residual is **honest incomplete**.  
2. First-divergence: sticky header vs scrollport vs grid main (y_table).  
3. Check portable list before inventing:  
   - canvas §14.2 (already shipped)  
   - grid real row heights Phase 9.5 (shipped)  
   - flex nav row / 11b (shipped)  
4. Likely residual classes: overflow/scrollport, sticky constraint vs transformed ancestors, remaining grid track sizing.  
5. One PR per root cause.

**Exit C:** sticky-scroll PASS @ t15 or document hard blocker with fixture if Chrome-class font-only residual.

### Phase D — Secondary queue (only if B+C blocked or done)

Pick **one** per session max:

| Priority | Work | Notes |
|----------|------|-------|
| D1 | `about` KF | letter-spacing / advance residual; GradientText contract already on master (#39) |
| D2 | Inheritance seed PR | `text-transform`, `white-space`, `word-break` on elements — brief: `forensics/2026-07-11-inheritance-audit.md` |
| D3 | `image-gallery` | Confirm network/image decode vs layout before big digs |
| D4 | T2 rect dual-gate | `data-testid` on holdout/campaign key nodes; hard fail layout PRs on rect mismatch — fidelity plan T2 |
| D5 | WPT Tier-1 runner | Menu in `trench/WPT_TIER1_SUBSET.md` — **after** product KF ≤5 cases |

### Phase E — Continuous obligations (every PR)

1. **Holdout sacred:** never edit `websuite/holdout/**` HTML in dig PRs.  
2. **Falsification fixture** in every dig PR (repro path).  
3. **Digest line:** `campaign P/N @ t15 avg X | holdout P/N avg Y | KF: …`  
4. **Portable note to Athena** for every shared-crate fix (exchange broadcast).  
5. Thresholds: **Pete-only** to raise. Clear known_fail only when truly ≤ ceiling permanently.  
6. No case-id branches in engine code.

---

## 4. Method rules (weaker model = stricter process)

These rules exist because cold models overfit and re-litigate fixed bugs:

1. **Probe before theory.** If you cannot name a pixel or a layout.json delta, you do not open an engine file.  
2. **One root cause per PR.** Multi-fix PRs are how merge races and false “shipped” claims happen.  
3. **Re-measure on merge commit**, not only on branch tip.  
4. **Do not re-implement** Slice A/B/B2/C, advance contract, canvas §14.2, DIG-1/2, CI honesty — already on master. Read the PR bodies if unsure.  
5. **Stale checkout ban:** never work in `Repos/hiwave-macos` if hub exists.  
6. **If stuck 2 hours:** stop, write a forensics note + exchange status, switch to D2 inheritance seed (small closed PR) rather than thrash.

---

## 5. Key files (read when needed — not all at once)

| Need | Path |
|------|------|
| Settings dig start | `parity-tests/repro/toggle-height.html`, `y_table.py` |
| IFC living sketch | `trench/IFC_PHASE3_SKETCH.md` |
| Stale-dimension map | `trench/forensics/2026-07-11-stale-dimension-map.md` |
| Fidelity / holdout policy | `trench/forensics/2026-07-11-test-fidelity-HARDENING.md` |
| Inheritance gaps | `trench/forensics/2026-07-11-inheritance-audit.md` |
| Registry / KF | `cases/registry.json` |
| Slice C (just shipped) | PR #44 body — valign applied; do not redo |

---

## 6. Doorbell / peers

- After each merge or dig exit: broadcast scoreboard + portable notes (`to_athena`).  
- Ring Prometheus only for **design** or **outside-eye** (not for “please merge”).  
- Athena is porting; give her **contracts + fixtures**, not dump of macOS patches.

---

## 7. Success criteria (reboot cycle)

| Horizon | Done means |
|---------|------------|
| First 2 hours | Fresh board number + Phase B started with y_table on settings |
| This cycle (Pete’s “get to work”) | **settings PASS** and/or clear written blocker with repro |
| Stretch | sticky-scroll PASS · campaign **23–24/26** · holdout still 6/6 |
| Fail | Holdout regresses, thresholds raised, or dig without fixture |

---

## 8. Explicit non-goals this reboot

- Full WPT import  
- Matching Chrome font hinting pixel-perfect  
- Rewriting renderer color architecture  
- Opening multi-day “epic redesign” without a failing probe  
- Editing holdout to make it green  

---

**Prometheus standing offer:** design/outside-eye on request via exchange. No merges from Prometheus.

— Prometheus
