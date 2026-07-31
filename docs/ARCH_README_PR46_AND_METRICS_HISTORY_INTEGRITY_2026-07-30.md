# Arch README PR #46 + metrics-history integrity DESIGN PIN (2026-07-30)

> **Seat:** Prometheus (headless grind tick). Design only — no merge / force-push / master write.  
> **Trigger:** Pete tasking (Athena relay `cac3552fbde7`) — each arch updates its top-level README; Atlas umbrella; he still cannot see metrics.  
> **Primary open PR:** [hiwave-windows #46](https://github.com/hiwavebrowser/hiwave-windows/pull/46) (`athena/readme-engine-status` @ `eca23a4`).  
> **Related pins that stand:** P1 adapter IMPLEMENT_NOW (`P1_METRICS_ADAPTER_DESIGN_PIN_2026-07-30.md`); empty parity HARD NO; C1 LEAVE-IT ledgered; Gradient DEFER; Engine 51 GO / cluster-before-PR; #33 HARD HOLD; hand-fill unified.json HARD NO.

---

## 0. Verdict

| Item | Ruling |
|------|--------|
| hiwave-windows **#46** (README Engine Status) | **DESIGN CLEAR / APPROVE merge** on structure + honesty doctrine |
| Number anchoring on #46 | **Non-blocking R1 nit** — pin last *complete* suite SHA, not bare "master today" |
| Fleet arch-README contract | **PINNED** — copy Athena shape (status table · empty parity · gaps · provenance) |
| metrics-history **integrity defect** (Win tip) | **IMPLEMENT_NOW** residual (producer + consumer filter) — separate from #46 |
| Umbrella P1 adapter | Still **IMPLEMENT_NOW** after #8; **amend:** never trust last CSV row alone |
| Pete's "I still don't see the metrics" | **Consumer gap** (P1) not producer gap — README #46 is not a substitute for umbrella badges |

**One-sentence summary:** Approve Windows README #46 as the fleet template for honest engine status, but do not treat the latest CSV row as authoritative — master tip `fda40abe` published a crash-truncated 260-pass row while the job stayed green because Enforce ignores `tests.ok`.

---

## 1. Independent ground (measured this tick)

### 1.1 Live board (open PRs)

| Repo | Open | Notes |
|------|------|-------|
| hiwave-windows | **#46** README; **#33** net-cache | #33 HARD HOLD stands (not this unit) |
| hiwave | **#8** badge honesty | Prior advisory APPROVE; still OPEN (P0a/P0b) |
| hiwave-macos | **#68** GPU pin docs | Prior ACCEPTED |
| hiwave-linux | *(empty)* | Talos still owes Linux README under Pete tasking |
| tank | *(empty)* | #8 packaging MERGED prior tick |

### 1.2 Windows `metrics-history` CSV (full, live)

```
timestamp,commit,branch,build_ok,passed,failed,ignored,warnings
2026-07-30T00:28:01Z,34296db1,master,True,839,0,4,49
2026-07-30T11:30:49Z,30929cf1,master,True,869,0,5,49   ← last COMPLETE suite
2026-07-30T13:43:20Z,fda40abe,master,True,260,0,0,49   ← CRASH-TRUNCATED
```

### 1.3 Crash-truncated run (master tip after #45 merge)

Source: `metrics/20260730_134323_fda40abe….json` on `metrics-history`.

| Field | Value |
|-------|--------|
| commit | `fda40abe` (master tip = #45 C1 ledger merge) |
| build.ok | true (49 warnings) |
| tests.ok | **false** |
| tests.exit_code | **3221225477** = `0xC0000005` STATUS_ACCESS_VIOLATION |
| tests.passed | **260** (partial parse before process death) |
| crates with tests | 18/21 listed vs 37/73 on the good run |
| missing vs 869 run | layout 206, text 51, engine 22, test 85, net 28, … all zeroed |

So the **last CSV row looks green** (`build_ok=True`, `failed=0`, `passed=260`) while the full JSON correctly marks `tests.ok=false` and a fatal exit.

### 1.4 Why the CI job still went green

`.github/workflows/metrics.yml` step **Enforce build and tests**:

```python
if not m["build"]["ok"]:
    bad.append(...)
if m["tests"]["failed"]:
    bad.append(...)
# MISSING: if not m["tests"]["ok"]:  # crash / non-zero exit with failed==0
```

A mid-suite crash can leave `failed=0` and a partial `passed` sum. Enforce does not consult `tests.ok` or `exit_code`. Job SUCCESS + history **publish** still run on master.

### 1.5 CSV schema hole

History writer appends only:

`timestamp, commit, branch, build_ok, passed, failed, ignored, warnings`

It does **not** record `tests_ok` or `tests_exit_code`. Any consumer (README human, P1 adapter, Tank) that reads **only** the last CSV row will treat a crash-truncated suite as a legitimate smaller baseline.

### 1.6 #46 README claims vs ground

PR #46 @ `eca23a4` (docs only, CI collect-metrics SUCCESS ×2):

| Claim | Ground |
|-------|--------|
| Engine ~83k / 38 crates | Plausible; not re-counted this tick; Athena measured 82,973 |
| Tests **869** pass / 0 fail / 5 ign | True for **complete** suite at `30929cf1` — **not** for tip `fda40abe` metrics |
| "Measured on master, 2026-07-30" | Ambiguous date without SHA; tip metrics are the 260 crash row |
| Parity empty + reason | **Correct** (GPU harness / 100.0 default) — same as P1 HARD NO invent |
| Gaps: gradient local, C1 ledger, ported≠wired | **Correct** and load-bearing honesty |
| Provenance → metrics.yml + metrics-history | **Correct** and fleet-copyable |

### 1.7 Linux history (informational)

Last master rows both `742/0/5` complete (`638f6d36`, `4f0ba80c`). No crash-truncated tip observed on Linux this tick.

---

## 2. Design rulings

### 2.1 hiwave-windows #46 — DESIGN CLEAR

**Approve** the PR as the **fleet template** for arch top-level READMEs under Pete's tasking.

Required properties (already present in #46):

1. **CI badge** only if workflow exists and is meaningful.
2. **Engine Status** table: build · tests · size · **parity empty-or-measured**.
3. **Parity never invented** — if harness defaults to 100.0 without GPU, say not measured + why.
4. **Known gaps** named, especially **registered/tested ≠ wired into render path**.
5. **Provenance** subsection pointing at the metrics workflow + `metrics-history` branch (re-derivable numbers).

### 2.2 Non-blocking nits on #46 (Athena may amend or stack)

| Nit | Severity | Fix |
|-----|----------|-----|
| Date without commit | **R1** | State `last complete master suite @ 30929cf1 (2026-07-30)` next to 869 |
| Tip metrics stale vs claim | **R1** | Do **not** imply tip `fda40abe` measured 869; if re-run after integrity fix, update |
| Line-count precision | cosmetic | "~82,900" vs "82,973" is fine; optional exact |

**Merge authority:** Athena under constitutional amendment + Pollux R1 when process green. Prometheus does not merge.

### 2.3 Fleet arch-README contract (PINNED for Talos / Atlas)

| Seat | Artifact | Pin |
|------|----------|-----|
| Athena | hiwave-windows README | **#46** is reference shape |
| Talos | hiwave-linux README | Same table + empty parity + provenance; numbers from **Linux** metrics-history complete rows only |
| Atlas | hiwave-macos README | Prefer existing parity path honesty; do not invent Win/Linux numbers into macOS README |
| Atlas | umbrella README | **Not** a hand-typed clone of arch tables — **P1 adapter** is the deliverable Pete still cannot see |

Priority if capacity is tight (Athena's relay already said this — **confirm**): **P1 adapter > macOS README polish**, because Pete has now said twice he cannot see the numbers on the front page.

### 2.4 metrics-history integrity — IMPLEMENT_NOW (producer)

**Owner:** Athena (Windows recipe); Talos mirror on Linux if same shape.

| Fix | Where | Contract |
|-----|-------|----------|
| **E1** Enforce consults `tests.ok` | `metrics.yml` Enforce step | `if not m["tests"]["ok"]: fail` — crash / non-zero exit reds the job |
| **E2** CSV columns | history writer | Add `tests_ok` (bool) and preferably `tests_exit_code` (int) |
| **E3** Optional completeness heuristic | collect or Enforce | Flag `incomplete` if `passed` collapses >50% vs previous complete master row **and** `tests.ok` is false (do not auto-fail pure real regressions that fail tests properly) |
| **E4** Re-run master | workflow_dispatch after E1 | Obtain a complete tip row for `fda40abe` or successor so tip matches honest suite |

Do **not** delete historical crash rows — they are forensic. Consumers filter; producers stop painting them green.

### 2.5 P1 adapter amend (Atlas) — stands + filter

Prior P1 pin stands. **Add completeness filter:**

| Rule | Meaning |
|------|---------|
| Prefer full `metrics.json` (artifact or history file) over CSV alone | JSON has `tests.ok` |
| If only CSV available | Require `tests_ok` column once E2 lands; until then, **reject** rows where `passed` is an outlier vs recent complete baseline **or** require human/path-b only for build badges |
| Last-row-wins | **HARD NO** without `tests.ok==true` |
| Parity | still **EMPTY** for Win/Linux |

### 2.6 What #46 does **not** solve

- Pete still will not see umbrella badges until **P1** lands after/with **#8**.
- Crash-truncated history will poison a naive adapter if shipped before E1/E2 + filter.
- Engine Slice-1 (51 fns) is **orthogonal** — Athena still owes cluster map before engine PRs (prior ruling `6e1a701c7d25`).

---

## 3. Seat asks

| Seat | Owe |
|------|-----|
| **Athena** | Pollux R1 on #46; optional R1 nits (SHA pin); **E1–E2 integrity PR** IMPLEMENT_NOW (small, high leverage); no umbrella consumer PRs; engine cluster map still owed before Slice-1 PRs |
| **Pollux** | R1 on #46 (docs honesty + no behaviour delta); when integrity PR opens, verify Enforce fails on `tests.ok=false` fixture |
| **Talos** | Linux README under Pete tasking using #46 shape + Linux complete metrics only |
| **Atlas** | P1 adapter with completeness filter; umbrella after #8; macOS README second to P1 if forced to choose; no exchange-authed master merge |
| **Prometheus** | No further #46 design unless scope expands or integrity PR needs outside-eye |
| **Pete** | No irreversible ask. Merge #46 when Athena+R1 green; P1 still the "I can see the numbers" gate |

---

## 4. Explicit non-actions

- No merge / force-push / delete from this seat.
- Do not re-pin P1 SoT (metrics-history), empty parity, hand-fill NO, C1 LEAVE-IT, Gradient DEFER, Engine 51/10 split, #33 HOLD, W0b implement, Tank packaging CLEAR, weight-fit DEFER.
- Do not treat 260 as a new baseline.
- Do not invent parity % on any arch README.

---

## 5. Artifact / exchange

- This file: `hiwave/docs/ARCH_README_PR46_AND_METRICS_HISTORY_INTEGRITY_2026-07-30.md` (uncommitted Atlas umbrella docs lane — Prometheus does not push/merge).
- Exchange doorbell-note posted this tick (schema:1 from prometheus).
