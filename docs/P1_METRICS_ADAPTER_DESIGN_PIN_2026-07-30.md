# P1 — Umbrella metrics adapter DESIGN PIN (2026-07-30)

> **Seat:** Prometheus (headless grind tick). Design only — no merge / force-push / master write.  
> **Reply chain:** Atlas tasking `651e57c1c09c` → Prom design `89bb0ef92772` → Linux ground `e8a6095e07b6` → Atlas R1 `681750d06603` → Prom advisory `db85c550cf0d` (hand-fill **withdrawn**) → Athena feed LIVE `1d77a07edef6` → Prom Option-(b) `6e3e586f7e8f` → **this pin**.  
> **PR dependency:** ship **after** umbrella [#8](https://github.com/hiwavebrowser/hiwave/pull/8) (P0a denominator + P0b build≠parity). Stack on `atlas/badge-honesty` or open fresh PR post-merge.  
> **Not a re-pin** of C1 LEAVE-IT, W0b implement, packaging CLEAR, GPU #68 ACCEPTED, weight-fit DEFER, or path-b hand-fill (still **withdrawn**).

---

## 0. Verdict

| Item | Ruling |
|------|--------|
| P1 adapter | **IMPLEMENT_NOW** (Atlas umbrella consumer) |
| Lane | **Option (b)** stands: Athena/Talos own platform feeds; Atlas wires `hiwavebrowser/hiwave` |
| Hand-fill `unified.json` | **HARD NO** (replace line erases it; decorative) |
| Parity windows/linux | **EMPTY** — never fill from CSV, build_ok, tests, or harness 100.0 |
| Source of truth | **`metrics-history` branch**, not submodule master checkout |
| Scope v1 | Windows + Linux **build + cargo tests** only; macOS parity path unchanged |

**One-sentence summary:** Wire the umbrella collector to the seats' append-only `metrics-history` feeds so public badges show real Windows/Linux build+tests without inventing parity and without writing numbers that the next collect erases.

---

## 1. Independent ground (measured this tick, not recalled)

### 1.1 Live feeds (HTTP raw — 2026-07-30)

| Platform | Branch | Primary | Last CSV row (measured) |
|----------|--------|---------|-------------------------|
| Windows | `metrics-history` @ live tip | `metrics/history.csv` | `2026-07-30T11:30:49Z,30929cf1,master,True,869,0,5,49` |
| Linux | `metrics-history` @ live tip | `metrics/history.csv` | `2026-07-30T05:43:29Z,4f0ba80c,master,True,742,0,5,46` |
| macOS | `metrics-history` exists | **different schema** (`avg_diff,passed,failed,total,…` — parity-oriented) | **no** `build_ok` column; **no** root `metrics.json` on that branch tip |

### 1.2 Master tip has **no** metrics files

Probed via GitHub Contents API on **master**:

| Repo | `metrics.json` on master | `metrics/` on master |
|------|--------------------------|----------------------|
| hiwave-windows | **404** | **404** |
| hiwave-linux | **404** | **404** |
| hiwave-macos | **404** | **404** |

Seat metrics live **only** on the orphan/side branch `metrics-history` (root `metrics.json` + `metrics/history.csv` + per-run JSON). They are **not** present in a normal submodule checkout of master.

### 1.3 Seat `metrics.json` shape (Windows ≡ Linux contract)

```json
{
  "timestamp": "…",
  "commit": "<full sha>",
  "branch": "master",
  "platform": "windows|linux",
  "build": { "ok": true, "exit_code": 0, "warnings": 49 },
  "tests": { "ok": true, "passed": 869, "failed": 0, "ignored": 5, "total": 869 },
  "not_collected": {
    "parity_pixel_diff": "requires a GPU adapter; … Deliberately omitted rather than emitting the harness's 100.0 default…"
  }
}
```

CSV columns (Win+Linux, verbatim):

```
timestamp,commit,branch,build_ok,passed,failed,ignored,warnings
```

### 1.4 Collector defect (why Win/Linux stay grey today)

`scripts/collect_metrics.py` `collect_platform_metrics()`:

1. Looks **only** for parity artefacts under the **submodule path** (`parity_test_results.json`, swarm, baseline).
2. If none found → prints `No metrics found` → **returns `None`**.
3. `main()` does `unified["platforms"] = platforms` — wholesale replace every non-test run.

So even after #44 / Linux CI, the umbrella never sees build/tests: it is not a "missing numbers" problem; it is a **wrong source path + parity-only early return**.

### 1.5 Badge contract post-#8 (target consumer)

From PR tip `atlas/badge-honesty` (`generate_badges.py`):

- `_build_ok(data)`: `build: bool` **or** `build: {"ok": bool}` → three-state; **never** infer from parity.
- `parity-overall`: always shows `N/3` denominator.
- `tests-*`: still `tests_passed` / `tests_total`.

Local master `generate_badges.py` may still be pre-#8 — implement P1 against **#8 tip or merged master**, not stale local.

---

## 2. Design pin — adapter shape

### 2.1 Where it lives

**Inside** the umbrella collect path (so it survives the platforms replace):

| Function | Change |
|----------|--------|
| `fetch_seat_metrics(platform) -> Optional[dict]` | **NEW** — load from `metrics-history` feed (see §2.2) |
| `map_seat_metrics_to_unified(platform, seat) -> dict` | **NEW** — map to badge fields (§2.3) |
| `collect_platform_metrics(...)` | **CHANGE** — after / beside parity extract: if seat metrics exist, merge build/tests provenance; **do not return None** solely because parity files are absent |
| `main()` | keep wholesale `platforms = …` replace; adapter must run **inside** the per-platform loop that builds `platforms` |

**Do not** hand-edit `metrics/unified.json` in git as a product fix.

### 2.2 Ingest mechanism (source ranking)

| Rank | Source | When |
|------|--------|------|
| **1 (primary)** | Last **master** data row of `metrics/history.csv` on branch `metrics-history` | Always for Windows + Linux v1 |
| 2 (optional enrich) | Root `metrics.json` on same branch | warnings object shape, `not_collected` text, full commit SHA |
| 3 (forbidden) | Exchange-typed numbers, WORK_QUEUE pins, seat chat | Never for badge numbers |
| 4 (forbidden) | Submodule working tree `metrics.json` on master | **Does not exist** — do not "wait for it" |

**Fetch options (Atlas picks one; pin requirements not implementation fashion):**

1. **CI-friendly (preferred):** workflow step before `collect_metrics.py`:
   ```bash
   # sparse / side checkout — illustrative
   git fetch https://github.com/hiwavebrowser/hiwave-windows.git metrics-history:refs/hiwave-metrics/windows
   git fetch https://github.com/hiwavebrowser/hiwave-linux.git   metrics-history:refs/hiwave-metrics/linux
   # then show file from that ref into .cache/metrics/{windows,linux}/
   ```
2. **HTTPS raw (acceptable for scheduled metrics.yml):**
   - `https://raw.githubusercontent.com/hiwavebrowser/hiwave-windows/metrics-history/metrics/history.csv`
   - same for linux  
   Verified this tick: URLs return live CSV.
3. **GitHub API** — fine; needs token on private forks only (these repos are public).

**Row selection rules:**

- Skip header.
- Prefer last row where `branch == master` (case-sensitive as written).
- If no master row: leave platform build/tests **NOT-MEASURED** (omit keys / no row), do not use PR branch rows.
- Prefer CSV over any number in this design doc (Athena 869→872 drift lesson).

**Freshness:**

- If fetch fails → leave unknown/no-data (fail closed on numbers).
- If last master row older than **14 days**: still publish, but set `metrics_stale: true` in the platform object (badge may ignore; PR should log warning). Do **not** invent fresher numbers.

### 2.3 Field map (CSV → `unified.json` platform object)

Target object keys consumed by post-#8 badges:

| Feed | unified field | Notes |
|------|---------------|-------|
| `build_ok` | `build: {"ok": <bool>, "warnings": <int>?}` | Dict form preferred (matches seat JSON + `_build_ok`) |
| `passed` | `tests_passed` | int |
| `failed` | `tests_failed` | int (metadata) |
| `ignored` | `tests_ignored` | int (metadata) |
| **formula** | `tests_total` | **`passed + failed` only** — do not add `ignored` (inflates denominator). Seat JSON `"total"` currently equals `passed` only — **do not trust it**; recompute. |
| `commit` | `git_commit` (short ok) + `metrics_commit` | Provenance |
| `timestamp` | `measured_at` | ISO from CSV |
| — | `tests_source: "cargo"` | **Required** — see §2.4 |
| — | `metrics_source: "metrics-history/history.csv"` | Provenance |
| — | **omit `parity` key** | Hard NO — badge stays "no data" |
| seat `not_collected` | optional passthrough under `not_collected` | Honesty trail |

**Linux uses the identical map.** Same CSV columns; same rules.

**macOS v1:** do **not** force this adapter. Keep existing parity-file collection for macOS. macOS `metrics-history` schema is parity-diff oriented and does not supply `build_ok`. macOS build badge remaining `unknown` after #8 is **correct** until a macOS seat publishes build in the Win/Linux schema (follow-up, not P1).

### 2.4 HARD PIN — do not mix test ontologies in overall

Today macOS `tests_passed` / `tests_total` are **parity-case** counts (e.g. 21/26), not `cargo test` counts.

Windows/Linux CSV counts are **cargo unit tests** (869 / 742).

| Badge | Rule |
|-------|------|
| `tests-windows.svg` / `tests-linux.svg` | Fill from cargo map (§2.3) — honest per-platform |
| `tests-macos.svg` | Unchanged (parity cases) |
| `tests-overall.svg` | **Must not sum cargo + parity-case platforms into one fraction** |

**Required overall behaviour (pick A; B only if A is blocked by time):**

- **A (pin):** `tests-overall` aggregates **only** platforms with the same `tests_source`. If ≥1 cargo and ≥1 parity_cases, prefer showing cargo sum **or** parity sum — **not both** — and append a source tag in the value string when mixed sources exist in the matrix, e.g. `1611/1611 · cargo` vs leaving overall as the pre-existing parity-only sum with denominator honesty. Simplest correct v1: **overall = sum of platforms where `tests_source == "cargo"`** once any cargo platform is present; if only macOS parity cases exist, keep current behaviour. Document the rule in the PR body.
- **B (weaker):** leave `tests-overall` macOS-only until a later P1.1; still fill per-platform Win/Linux tests. Acceptable if A is cut for size — say so in PR.

**Forbidden:** `21/26 + 869/869 + 742/742` rendered as `1632/1647` with no source label.

### 2.5 Parity cells (restate — load-bearing)

| Cell | Value |
|------|-------|
| `parity-windows` | no data |
| `parity-linux` | no data |
| `parity-overall` | min(measured) with **N/3** denominator (from #8) — still 1/3 until GPU parity exists |
| harness 100.0 on empty capture | never promoted into unified |

If `not_collected.parity_pixel_diff` is present on the seat feed, that is evidence **not** to invent a number.

### 2.6 Early-return fix (load-bearing)

```text
BEFORE: no parity files → return None → platform missing
AFTER:  no parity files + seat build/tests → return {build, tests_*, tests_source, …} without parity
        no parity + no seat feed → return None (or explicit empty) → badges unknown/no data
```

Parity extract and seat-metrics extract are **orthogonal**. Either may populate a platform row.

### 2.7 Workflow touchpoints

| Workflow | Change |
|----------|--------|
| `metrics.yml` / `parity-unified.yml` collect step | Fetch Win+Linux `metrics-history` **before** `collect_metrics.py` |
| Badge generation | Prefer **fail loud** on generate_badges (P0c residual — **not** bundled in P1 unless free). Named: `parity-unified.yml` `generate_badges.py \|\| echo …` still fail-open |
| Committed badge SVGs | Match existing repo pattern (commit regenerated SVGs if that is how master works today) |

---

## 3. Acceptance criteria (Atlas PR checklist)

- [ ] Depends on / stacked after #8 (P0a+P0b on tree under test).
- [ ] No hand-filled `unified.json` platform rows in the product path.
- [ ] Live CSV last **master** row drives Windows + Linux numbers (receipt: commit SHAs in PR body match CSV, not this doc).
- [ ] `build-windows` / `build-linux` → passing or failing from feed; not unknown solely because parity absent.
- [ ] `tests-windows` / `tests-linux` filled; `tests_total == passed+failed`.
- [ ] `parity-windows` / `parity-linux` still **no data**.
- [ ] `parity-overall` still shows coverage denominator (`· 1/3` until more parity lands).
- [ ] `tests-overall` obeys §2.4 (no silent cargo+parity mix).
- [ ] Unit tests: at least T-RED style fixtures with a fake CSV → unified platform dict (no network in unit test); optional integration mark for live fetch.
- [ ] PR body states: **parity intentionally empty**; **tests_source cargo**; **fetch path**.
- [ ] No `__pycache__` / `*.pyc` in the PR.
- [ ] No metrics-history rewrite from Atlas (read-only consumer).

---

## 4. Explicit non-goals (this PR)

| Out of scope | Why |
|--------------|-----|
| Path-b hand-fill | Self-erasing; withdrawn |
| Windows/Linux parity floats | No GPU board; harness lie risk |
| macOS build via this adapter | Schema mismatch on macOS metrics-history |
| App-shell / launch readiness cell | Design debt after P1; build ≠ demo-ready |
| P0c fail-open badge step | Separate workflow slice |
| Tank R4 / W0b / #33 | Orthogonal queues |
| Changing seat CSV schema | Consumer adapts; seats own producer |

---

## 5. Live numbers **as of this tick** (informational only)

Consumer must re-read CSV; these are **not** SoT:

| Platform | commit (short) | build | cargo tests | parity |
|----------|----------------|-------|-------------|--------|
| Windows | `30929cf1` | ok | 869 passed / 0 failed / 5 ign | NOT-MEASURED |
| Linux | `4f0ba80c` | ok | 742 passed / 0 failed / 5 ign | NOT-MEASURED |
| macOS | (parity path) | still no build feed | parity cases in unified | MEASURED ~88.1% |

---

## 6. Seat asks

| Seat | Action |
|------|--------|
| **Atlas** | Implement P1 from this pin after #8; open umbrella PR; do not self-merge if ownership still Pete-flagged. |
| **Athena** | Keep appending master CSV rows; keep `not_collected.parity_pixel_diff`; do not open umbrella consumer PRs. |
| **Talos** | Same as Athena for Linux feed; no second metrics path. |
| **Pollux** | On P1 PR: CLEAR only if §3 checklist holds (esp. parity empty + no overall mix + CSV-driven). |
| **Argos** | Idle on this slice. |
| **Pete** | Merge #8 when ready; then P1; umbrella ownership gap still flagged (no formal R1 on umbrella). |

---

## 7. Prometheus next

- Outside-eye **P1 PR** when open (pin §3).
- Do **not** re-measure this board unless tip moves (new CSV schema, #8 abandoned, or parity capture becomes real).
- Do not re-pin #8 advisory APPROVE / Option (b) / hand-fill withdrawal / C1 LEAVE-IT unless measurement changes.

---

*Prometheus · 2026-07-30 · design pin only*
