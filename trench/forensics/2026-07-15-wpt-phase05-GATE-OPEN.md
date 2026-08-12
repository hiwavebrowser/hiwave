# WPT Phase 0.5 — GATE OPEN (IMPLEMENT pin)

> **Status:** GATE OPEN 2026-07-15 grind tick. Design complete; ready for Atlas **after** #53 merge + atomic text-metrics (or parallel W0a-only docs/manifest anytime).  
> **Audience:** Atlas (execute), Athena (port runner later), Pete (Friday trendline consumer), Prometheus (outside-eye when PR opens).  
> **Exists in service of:** the PLAN.md north star — WPT Tier-1 pass-rate on Fridays, absolute conformance, not “matches Chrome’s bug.”  
> **Companions:** `trench/LINE_BOX_WPT_ROADMAP.md` · `trench/WPT_TIER1_SUBSET.md` · `trench/PLAN.md` Phase 0.5 · atomic kickoff `2026-07-15-text-metrics-ATOMIC-KICKOFF.md`.  
> **Not this unit:** DIG-3 form paint · Tank estimator · website Tank · Aleph hero · public re-cuts.

---

## 0. One-liner

**Dig preconditions for WPT are met.** Wrap is in production layout; IFC A/B/B2/C shipped; gallery confound closed (#53); text-metrics epic greenlit. **Phase 0.5 is still a stub** — January `rustkit-test` work-order is labeled “completed” but the reftest path never renders the engine. This pin gate-opens a **minimal honest runner + ≤30-test seed** so Friday can plot a real Tier-1 % without thrashing campaign nights.

---

## 1. Why gate opens now (not 2026-07-10)

| Precondition (roadmap) | 2026-07-10 truth | 2026-07-15 truth |
|------------------------|------------------|------------------|
| Slice 0 — production wrap callers | **OPEN** (`wrap_text` zero callers) | **CLOSED** — `lib.rs` ~1148 / ~1251 call `wrap_text` / `wrap_text_with_first_line` on `origin/master@4f847e8` |
| IFC mixed-inline quality | sketch only | **A+B+B2+C shipped** (#31/#37/#44) |
| Campaign board not thrashing | early sticky/paint nights | 24/26 @ t15; last mile = atomic form recompose |
| Gallery / sticky digs | active unknowns | gallery **named closed** (grid span gutters); sticky epic already paid |
| WPT runner | stub admitted | **still stub** (this pin) |

**Refuse:** opening WPT while the text wall and form recompose still own every night.  
**Allow:** bank the runner **now**, execute **after** atomic (or land W0a manifest-only anytime with zero board risk).

---

## 2. Live scaffold autopsy (do not trust “completed”)

Pin: `hiwave-macos origin/master@4f847e8` (read-only; local seat may be dirty+behind).

| Artifact | Claim | Measured truth |
|----------|-------|----------------|
| `.ai/work_orders/wpt-harness.json` | `status: completed` (2026-01-02) | Gates only check Cargo.toml + docs exist + crate builds — **not** that tests exercise the engine |
| `crates/rustkit-test/src/reftest.rs` | “Reference (visual) tests” | `run_comparison` **normalizes HTML strings and strcmp** — never parse / style / layout / paint |
| `crates/rustkit-test/src/layout.rs` | Layout tests | Builds empty `LayoutBox` + default `ComputedStyle`; if no `.expected` file → **always PASS** |
| `tests/wpt/` | harness usage docs point here | **Absent** on origin tree |
| Campaign path | honest pixel meter | **Real** — `scripts/parity_test.py` + registry `cases/registry.json` (32 cases) + CfT-148 baselines |

**Method that worked this campaign (portable):** measure truth first; do not inherit January identity. Same rule as smoke-runner lie #6 and reset-less baselines.

---

## 3. Design choice — three paths ranked

| Path | What | Effort | Honesty | Call |
|------|------|--------|---------|------|
| **P0 (recommended)** | Thin **WPT reftest adapter** over the **existing capture/pixel path** (parity_oracle / headless HiWave render → pixel compare test vs `-ref`) + checked-in **manifest** of ≤30 WPT ids | 1–2 nights after atomic | High — real pixels, real engine | **DO THIS** |
| P1 | Revive `rustkit-test` reftest to call engine layout+paint | 2–4 nights; fights dead stubs | Medium until capture path shared | Only if P0 blocked |
| P2 | testharness.js JS assertions only | 2+ nights + JS host | Wrong for layout-first north star | Defer |

**Why P0:** campaign already has the expensive parts (render HTML → PNG, pixel diff, registry schema). WPT reftests are `== test.html ref.html` — same shape as match reftest.list. Do not rebuild a second engine host.

**Why not “just report campaign t15 as WPT”:** campaign is **pinned Chrome** parity (trap #2 in roadmap). North star must stay **spec reftests**, independent of CfT.

---

## 4. Implement stack (Atlas)

### W0a — honesty + pin + manifest (≤0.5 night, **anytime**)

No engine change. Cannot red-lock CI.

1. Add `trench/wpt/README.md` pointing at this pin + roadmap.  
2. Add `trench/wpt/MANIFEST.yml` (or `.json`) with:
   - `wpt_pin`: git SHA of [web-platform-tests/wpt](https://github.com/web-platform-tests/wpt) (Atlas picks; freeze deliberately)  
   - `seed_n`: ≤30  
   - `entries[]`: `{ id, path, kind: reftest|unit, tier: 1A|1B|1C, maps_to: slice-0|A|B|E|flex }`  
3. Add `scripts/wpt_sync.sh` — sparse-checkout or subtree of **only** paths listed in manifest into `third_party/wpt/` (gitignored bulk OK; **manifest is source of truth**).  
4. Doc fix: one-line note in `docs/RUSTKIT-TESTING.md` (if present) or `crates/rustkit-test` module docs — **reftest path is HTML-normalize stub; do not report as WPT %**.  
5. Flip `WPT_TIER1_SUBSET.md` header from “menu” to “seed source for MANIFEST”.

**Exit W0a:** `MANIFEST` lists ≤30 concrete paths; clone script dry-runs; no CI metric yet.

### W0b — first honest K/N (1–1.5 nights, **after atomic preferred**)

1. Runner CLI: `scripts/wpt_tier1.py` (or extend parity_lib) that:
   - reads MANIFEST  
   - for each reftest: render `test` and `ref` through **same** HiWave headless path used by parity capture (viewport from manifest default **800×600** unless test meta says otherwise)  
   - pixel-diff with existing oracle thresholds **or** stricter exact-match for pure-black/white reftests  
   - emits `trench/wpt/last-run.json`: `{ pin, n, pass, fail, skip, rate, ts, git_sha }`  
2. **Skip policy:** missing ref / unsupported `@supports` / needs JS → `SKIP` with reason (not FAIL).  
3. First seed composition (from `WPT_TIER1_SUBSET.md` menu — resolve exact filenames against pin):

| Bucket | Count | Why first |
|--------|------:|-----------|
| **1A css-text** white-space / soft wrap / word-break-normal overflow | 15–18 | Slice 0–1 already paid; should not all be red |
| **1B css-inline** vertical-align baseline/middle only | 6–8 | Slice C shipped (#44); cheap signal |
| **1C flex** definite item height / align-items basic | 4–6 | settings-class residual; keep small |

4. **Do not** import full css-text tree. Grow only when a campaign dig would have been clearer with a WPT id (roadmap rule).

**Exit W0b:** `Tier1 pass = K/N` printed; `last-run.json` committed or CI-artifacted; N≥20 including ≥1 PASS and ≥1 FAIL (all-green on day one = liar harness).

### W0c — Friday trendline field (≤0.5 night)

1. Append to `trench/digest-macos.md` template: `WPT Tier-1: K/N (rate%) @ pin <sha7>`.  
2. Optional CI: nightly or Friday-only job; **must not** gate PR merges until Pete locks a floor.  
3. PLAN.md Phase 0.5 exit: mark **MET** only after first digest row exists.

---

## 5. Contracts (load-bearing)

1. **Campaign metric unchanged** — still t15 vs CfT 148 on registry cases. WPT is additive.  
2. **QUIRKS.md** — if a WPT fails because Chrome deviates and we match the **spec**, record and leave campaign red if needed; do not “fix” toward Chrome.  
3. **Runtime budget** — full Tier-1 seed **&lt; 5 min** local (subset cap, not full WPT).  
4. **No second truth** — do not publish rustkit-test HTML-strcmp results as conformance.  
5. **Pin freezes** — change WPT pin only at campaign boundaries (same discipline as CfT pin).  
6. **Athena** — Windows gets the same MANIFEST + pin; runner port after macOS W0b green (or parallel if idle). Do not invent a different subset per OS.

---

## 6. Sequencing vs live epics

| Work | Priority vs WPT | Collision? |
|------|-----------------|------------|
| **#53 merge** | Higher — unblocks atomic | None |
| **Atomic text-metrics** (form recompose) | Higher — board last mile | Shared layout nights — **W0b after** |
| **Website Tank / hero / C3a / O1** | Launch-critical product (other repos) | None |
| **W0a** | Free anytime | None |
| **DIG-3 form chrome paint** | After atomic forms settle | Paint-only; parallel OK post-atomic |
| **W0b/W0c** | First free Friday runway after atomic | Prefer dedicated night |

**Atlas default order:** merge #53 → atomic → (optional W0a earlier) → W0b → W0c.  
**Do not** steal an atomic night for WPT.

---

## 7. Outside-eye checklist (Prometheus when PR opens)

### W0a
- [ ] Manifest ≤30; every path resolves against declared pin  
- [ ] Sync script does not vendor entire WPT into the monorepo without gitignore  
- [ ] Stub reftest honesty note present (no false “WPT green” claim)

### W0b
- [ ] Renders through **engine**, not HTML strcmp  
- [ ] `last-run.json` has pin + N + K + at least one intentional FAIL or SKIP  
- [ ] Viewport defaults documented; no silent DPR mismatch  
- [ ] Campaign CI gates **unchanged** (no hard WPT floor yet)

### W0c
- [ ] Digest field matches last-run.json arithmetic  
- [ ] PLAN Phase 0.5 exit criteria only flipped after real K/N

### Reject
- Full WPT import “for completeness”  
- Counting campaign t15 as Tier-1  
- Lowering reftest thresholds to force a pretty %  
- Merging model-only atomic changes under a WPT PR

---

## 8. Explicit non-goals (this gate)

- Tier-2 (grid full matrix, animations, sticky edge matrix, full fonts) — still closed.  
- testharness.js host.  
- Replacing CfT campaign with WPT.  
- 100% / 98% folklore revival.  
- Windows runner before macOS W0b (unless Athena idle and wants W0a twin).

---

## 9. Seat actions

### Atlas
1. Merge #53 (prior APPROVE stands @ `d8b89001`).  
2. Atomic kickoff §4–5 (form recompose).  
3. Land **W0a** when a short gap appears (even before atomic).  
4. Open **W0b** first free night after atomic lands on master.  
5. Bank this forensics file on hub when convenient.

### Athena
- No engine port required for W0a. After W0b, twin MANIFEST runner on Windows capture path; label digests if soft-crop still differs.

### Pete
- Friday: expect first `WPT Tier-1 K/N` row after W0b — interpret as north-star seed, not ship gate.  
- Optional: lock “no WPT floor in PR CI” until N≥50 and rate stable two Fridays.

### Prometheus
- Outside-eye on W0a/W0b/W0c PRs per §7.  
- Challenge any digest that claims “WPT green” from HTML-normalize or campaign-only numbers.

---

## 10. Irreversible deferred

- merge any PR · force-push · public re-cut · seeding Tank ceilings · hard WPT CI floor without Pete

---

*Prometheus grind tick 2026-07-15 — no open execution PR for outside-eye; #53 still only OPEN (APPROVE stands). Highest unbanked strategic unit after dig settle = Phase 0.5 WPT gate-open.*
