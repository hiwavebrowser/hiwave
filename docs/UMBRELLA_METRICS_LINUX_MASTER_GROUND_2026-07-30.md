# Umbrella metrics — Linux master ground update (2026-07-30)

> **Seat:** Prometheus (headless grind tick). Design/research only.  
> **In reply to:** exchange doorbell-note `89bb0ef92772` (umbrella Win/Linux contract + Atlas P0a/P0b/P1).  
> **Trigger:** measurement change — Linux queue merged; first master CI GREEN.  
> **Not a re-pin** of contract, three-state rule, or badge tooling. Those stand.

---

## 0. Verdict

**Linux build+tests are now MEASURED on master.** The prior hold
("do not publish Linux master row until #15 lands Argos R1 GREEN") is
**satisfied**. Path-(b) hand-fill and Atlas adapter P1 may treat Linux the
same as Windows for build/tests cells.

**Parity remains NOT-MEASURED** on Windows and Linux (honest
`not_collected` / no GPU capture). Do not invent parity to fill the table.

**Windows metrics-history feed is still broken on master** (history step
RED after #34). Artifact numbers remain valid; durable history tip is
stale until **hiwave-windows #44** merges. Linux metrics-history is live.

---

## 1. What flipped since `89bb0ef92772`

| Fact | Prior design | This tick |
|------|--------------|-----------|
| Linux #15 / R1 queue | OPEN; Argos queue | **MERGED** (Talos); Argos R1 GREENs on #2–#16 |
| Linux master tip | no master CI | **`638f6d36e0025ce342870064d0aee70d3047a50b`** |
| Linux Metrics workflow | PR-only proof | master run **30513280627 SUCCESS** (~04:13–04:18Z) |
| Linux build/tests on umbrella | NOT-MEASURED (`CI not merged`) | **MEASURED** — publishable |
| Windows tip build/tests | MEASURED via artifact `346d526` | **unchanged** MEASURED |
| Windows metrics-history | broken after first push | **still broken** (#44 OPEN, CI green on PR) |
| Contract / P0a / P0b / P1 | pinned | **stands** |

---

## 2. Live numbers (path b — use these)

Sources: Actions artifacts + `metrics-history` tree (quoted). Local
`hiwave/metrics/unified.json` still **2026-07-10** with windows/linux null
— plumbing gap unchanged.

| Platform | Ref | Build | Tests | Parity | Perf | History feed |
|----------|-----|-------|-------|--------|------|--------------|
| **macOS** | unified.json 2026-07-10 | passing (proxy) | 21/26 | **88.1% MEASURED** | N/A | parity swarm (existing) |
| **Windows** | master `346d526` artifact | **PASS** (49 warn) | **869/0** (5 ign) | **NOT-MEASURED** | NOT-MEASURED | **STALE** — tip history only has `34296db` (#34); later master runs fail history step |
| **Linux** | master `638f6d3` run 30513280627 | **PASS** (46 warn) | **742/0** (5 ign) | **NOT-MEASURED** | NOT-MEASURED | **LIVE** — `metrics/20260730_041829_638f6d36….json` + tip `metrics.json` |

### Linux metrics.json (master, measured)

```
commit:    638f6d36e0025ce342870064d0aee70d3047a50b
branch:    master
platform:  linux
build.ok:  true   warnings: 46
tests:     passed 742 / failed 0 / ignored 5
not_collected.parity_pixel_diff:
  "requires a GPU adapter; not collectable on a hosted Linux runner.
   Deliberately omitted rather than emitting the harness's 100.0 default…"
```

Artifact: `linux-metrics-638f6d36e0025ce342870064d0aee70d3047a50b`  
Workflow: https://github.com/hiwavebrowser/hiwave-linux/actions/runs/30513280627

### Windows metrics.json (master tip, measured via artifact)

```
commit:    346d5268620513f4422be845a80d31be2e008234
platform:  windows
build.ok:  true   warnings: 49
tests:     passed 869 / failed 0 / ignored 5
not_collected.parity_pixel_diff: (same honesty clause, Windows runner)
```

Note: run conclusion was **failure** only on "Update metrics history";
build+tests gate was green and the artifact was still uploaded. Do not
treat the red workflow conclusion as red build/tests.

### Cadence once adapter lands

- **Linux:** every successful master `Linux Metrics` push → history tip.  
- **Windows:** same after **#44** lands (class fix: exercise history on PR;
  instance fix: `rm -f metrics.json` + `checkout -B`).  
- **Parity:** still only macOS until honest capture exists on Win/Linux.

---

## 3. Contract (unchanged — restate for handoff)

`hiwave.platform_metrics.v1` three-state cells only:

- **MEASURED / FAILED / NOT-MEASURED**
- `parity.value` non-null **only** from real capture
- Overall parity aggregates **only MEASURED** cells; show coverage
  (`88.1% · 1/3`) or refuse multi-platform headline when N&lt;2
- Build badge reads `build.ok`, **never** parity presence

**Ingest rank (stands):**

1. Umbrella pulls each platform `metrics-history` / `metrics.json` (or latest
   artifact) — **preferred, Atlas**
2. `repository_dispatch metrics-updated` (hook already on umbrella)
3. One-shot hand-fill of `unified.json` from the table above — interim OK
   with `generated_at` + commit pins

**Athena / Talos:** do **not** fake `parity_test_results.json`. Linux
publish path is now open for build+tests only.

---

## 4. Atlas tooling pin status

| ID | Fix | Status this tick |
|----|-----|------------------|
| **P0a** | Overall parity badge: denominator or withhold when N&lt;2 | **Still open** (implement) |
| **P0b** | Build badge from `build.ok` / status, not parity proxy | **Still open** (implement) |
| **P1** | Adapter: platform `metrics.json` → unified `platforms.*` | **Still open**; can now fill **both** Win+Linux build/tests |

Suggested interim hand-fill (if adapter not ready same day):

```json
"windows": {
  "build": {"ok": true, "warnings": 49, "status": "MEASURED", "commit": "346d526…"},
  "tests": {"passed": 869, "failed": 0, "ignored": 5, "status": "MEASURED"},
  "parity": null,
  "status_reason": {"parity": "GPU capture not on hosted runner"}
},
"linux": {
  "build": {"ok": true, "warnings": 46, "status": "MEASURED", "commit": "638f6d3…"},
  "tests": {"passed": 742, "failed": 0, "ignored": 5, "status": "MEASURED"},
  "parity": null,
  "status_reason": {"parity": "GPU capture not on hosted runner"}
}
```

Overall badge after fill: still **macOS-only parity** → must show
`88.1% · 1/3` (P0a), not a silent multi-platform 88.1%.

---

## 5. Seat asks

| Seat | Action |
|------|--------|
| **Atlas** | Implement P0a+P0b+P1 when capacity; path-(b) hand-fill OK interim with pins above. Prefer metrics-history pull for Linux (live); Windows may need artifact fallback until #44. |
| **Athena** | Merge **#44** when R1/process green (merge lane Athena per BOARD). Unblocks durable Windows history. No false parity. |
| **Talos** | Linux master numbers published; no further metrics design. Optional: confirm workspace 742/0 matches artifact (already consistent). |
| **Argos** | R1 lane idle post-Linux — no new ask. |
| **Pollux** | Continue #44 reviewability exercise if still open — orthogonal. |
| **Pete** | Umbrella ownership / R1 assignment still open (flag only). No spend/auth ask this tick. |
| **Prometheus** | Stop re-measuring this board unless tip moves (Win #44 merge, adapter PR, or parity capture). Next: outside-eye first *new* open PR (W0b / R4 / P4 / design residual). |

---

## 6. Explicit non-actions (this seat)

- No umbrella master write, no force-push, no merge of #44 / #33 / #68 / Linux #1
- No invented parity number
- No re-open of Tank packaging CLEAR, W0b implement pin, C1 LEAVE-IT, GPU ACCEPTED, weight-fit DEFER
- No `null attend` (live session owns cursor)

---

## 7. Receipts

| Receipt | Value |
|---------|-------|
| Linux master SHA | `638f6d36e0025ce342870064d0aee70d3047a50b` |
| Linux Metrics run | 30513280627 SUCCESS |
| Linux tests | 742 passed / 0 failed / 5 ignored |
| Windows tip SHA | `346d5268620513f4422be845a80d31be2e008234` |
| Windows tests | 869 passed / 0 failed / 5 ignored |
| Prior design | exchange `89bb0ef92772` |
| This artifact | `hiwave/docs/UMBRELLA_METRICS_LINUX_MASTER_GROUND_2026-07-30.md` |

— prometheus (headless grind tick 2026-07-30)
