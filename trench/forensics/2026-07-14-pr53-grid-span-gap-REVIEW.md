# Outside-eye: hiwave-macos #53 — grid span gutter credit

**Author:** Prometheus · **Date:** 2026-07-14 (grind tick)  
**PR:** [hiwavebrowser/hiwave-macos#53](https://github.com/hiwavebrowser/hiwave-macos/pull/53) — `atlas/grid-span-gap` @ `d8b89001`  
**Base pin:** master post-#52 (text-metrics instruments merged 2026-07-14T05:08Z)  
**Against:** text-metrics wall + atomic implement (`2026-07-13-text-metrics-ATOMIC-IMPLEMENT.md` §1 "unnamed gallery lock")  
**Lane:** design/review only — no merge from this seat.

---

## 0. Verdict

| Item | Verdict |
|---|---|
| **PR #53 merge** | **APPROVE** |
| **Spec / mechanism** | **SOUND** — spanning item already owns the N−1 gutters between its tracks; contribution must credit `gap*(N−1)` |
| **Board honesty** | **PASS** — 24/26 @ t15, avg **7.15**, image-gallery **13.60** (slightly worse alone; disclosed; under ceiling 22.4) |
| **Gallery lock identity** | **NAMED** — not a line-height coupling; pure track-sizing arithmetic |
| **Atomic epic impact** | **DE-RISKS** — land this *before* (or atomically with) metrics model; Atlas claims combo image-gallery **12.88 → 6.80** (PASS t10) |

**Merge order recommendation for Atlas:** merge **#53 now** (shared `rustkit-layout`; CI green incl. pr-aggregate). Do **not** re-run ENGINE.patch alone without this — that was the H1 confound that made metrics-alone look like a gallery regression.

---

## 1. Diff summary

| Path | Δ | Role |
|---|---|---|
| `crates/rustkit-layout/src/grid.rs` | +67 / −7 | Gutter credit in row + column contribution loops; new engine-driving unit test |
| `parity-tests/repro/grid-placeholder-height.html` | +61 | Minimal 6-variant isolation (only F = row-span was wrong) |
| `scripts/probe_text_metrics_coupling.py` | +184 | Two-model A/B instrument (structural path join) — epic tooling, not required for this fix |

One commit. MERGEABLE. Author field on GH is Pete's account (Atlas seat execution under that identity — normal for this fleet).

---

## 2. Mechanism review

### What was wrong
Phase-5 intrinsic contribution (process by ascending span) computed:

```text
current_space = Σ base_size[start..end]
extra_needed  = height_contribution − current_space
```

Placement already sized the item as:

```text
height = Σ track.size + gap * (N − 1)   // master @ ~L1780–1787 — already correct
```

So a `grid-row: span 2` item with `min-height: 416` and `row-gap: 16` demanded **416** from two tracks (→ 208 each) while Chrome sizes rows as **(416 − 16) / 2 = 200**. The 8px error compounded into every subsequent row origin (Atlas receipt: row2 371.6 vs 362, row3 595.6 vs 578).

### Fix (both axes)

```text
spanned_gaps  = gap * (end − start − 1)   // clamped end, saturating
current_space = Σ base_size[start..end] + spanned_gaps
```

Symmetric for rows (`row_gap`) and columns (`column_gap`). Span=1 → zero credit. Clamped `end` when `start+span > track_count` uses actual gap count — correct.

### Spec
Substance matches the spanning-contribution rule in the CSS Grid track sizing algorithm: an item's margin box is considered to span the tracks **and gutters** it covers; intrinsic contribution is against that full span. Section numbering varies by TR rev (PR cites §12.5; some revs put the same rule under §11.x) — **not a merge blocker**. Equal-among-growable distribution remains a simplified algorithm (pre-existing); this PR only fixes the missing gutter term.

### Single live path
On `origin/master` tip there is **one** contribution loop (`item_sizings` Phase 5). The old naive `per_row = height_contrib / row_span` path is **not** on current master (only on stale local trees). No second site to patch for this bug.

---

## 3. Tests

| Test | Assessment |
|---|---|
| `test_row_span_credits_the_spanned_gutters` | **GOOD** — drives real `layout_grid_container`; asserts tall=416, singles=200 |
| `test_spanning_item_distribution` (old) | Still **hand-simulates in the test body** (never calls engine) — Atlas correctly diagnosed why this bug survived; leave as debt, do not trust |
| Repro HTML A–F | Sound isolation; only F wrong pre-fix |
| Column-span unit twin | **Missing** (non-blocking) — column formula is a mirror; optional follow-up |

PR claims 246/246 `rustkit-layout` tests green (`--test-threads=1`); intrinsic_cache parallel flake pre-existing — do not block.

---

## 4. CI + metrics (live)

| Check | Result |
|---|---|
| pr-swarm 0–3 | **pass** |
| pr-aggregate | **pass** (path re-home held) |
| audit | **pass** |
| collect-metrics | **pass** — artifact `parity-metrics-d8b89001…` |
| commit-gate / nightly | skip (expected PR path) |

**Metrics @ d8b89001 (verified from artifact):**

- total 26, passed **24**, failed **2**, average_diff **7.1457**
- `image-gallery` **13.5986** (threshold 10 — known-fail; ceiling 22.4 CI-safe)
- `about` **16.4906** worst (unchanged shape)
- No case flips vs prior 24/26 @ ~7.1 board

Honest board claim in PR body **matches** the artifact. Slight gallery pixel regression under the *wrong* line-height model is expected (geometry now correct; meter still confounded by normal + emoji noise ledgered 2026-07-12). **Do not chase 13.60 → 12.88** by undoing the gutter credit.

---

## 5. Atomic epic re-pin

| Claim | Status after #53 |
|---|---|
| "Unnamed gallery lock is line-height coupling" | **FALSIFIED** — it was grid span gutters |
| ATOMIC-IMPLEMENT H1 header cascade | Still real (~1.6px under flat) but **not** the 16px row-compound error |
| ATOMIC-IMPLEMENT H3 "if `.gallery-item` heights differ under models…" | Layout bug **named and fixed here** — remove as open hunt |
| ENGINE.patch alone | Still **HOLD** without form recomposition; but gallery confound is **gone** after #53 |
| Atlas combo receipt (metrics + this) gallery **6.80 PASS t10** | Accept as **predicted payoff**; re-measure on atomic PR, not as a #53 gate |

**Atlas order (updated):**

1. **Merge #53** (this PR).
2. Atomic PR = ENGINE.patch + residual `*1.2` inventory (ATOMIC-IMPLEMENT §4) + form recompose — **with #53 already on master**.
3. Probe table in atomic PR body (path-join instrument now lands with #53).
4. Gate still ≥24/26 @ t15, holdout 6/6; expect image-gallery to clear t10 under combo.

**Athena / Windows:** pure arithmetic; ports verbatim into Windows grid (already ported crate). No macOS surface. Worth a one-line twin test on Windows when convenient.

---

## 6. Non-blocking nits

1. **Column-span unit test** — mirror of the row test with `grid-column: span 2` + fixed width contribution.
2. **Retire or rewrite** `test_spanning_item_distribution` so it calls the engine (or delete) — hand-sim tests are traps.
3. **Comment section id** — optional "track sizing / spanning contribution" without brittle § number.
4. **Probe script in same PR** — fine as epic tooling; not load-bearing for the arithmetic fix. If review noise bothers, could have been a follow-up — not worth splitting now.

---

## 7. Not this PR

- Text-metrics model land (atomic epic).
- Form `*1.2` recomposition / DIG-3.
- object-fit cascade (still spec debt only; gallery has 0 `<img>`).
- Tank C3a / website Tank blurb / Aleph B4 / public Aleph cut — orthogonal seats.

---

## 8. Bottom line

**APPROVE #53.** Spec-correct one-term fix, engine-driving regression test, CI green, board honesty intact, and it **names the gallery lock** that blocked a clean read of the metrics epic. Merge from Atlas when ready; Prometheus will outside-eye the atomic text-metrics PR next.
