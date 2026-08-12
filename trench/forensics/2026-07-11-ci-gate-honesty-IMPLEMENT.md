# CI gate honesty — implement pin (path + schema + ceiling)

**Author:** Prometheus · **Date:** 2026-07-11 (grind tick)  
**Lane:** design only — no workflow merge from this seat  
**Hub:** `hiwave-macos` @ `origin/master` `8e00d22` · evidence from PR #37 run `29141476634`  
**Supersedes residual of:** `2026-07-11-pr-aggregate-PATH-BUG.md` §Orthogonal debt + WORK_QUEUE “PR CI gate honesty after path fix”  
**Does not supersede:** B2 APPROVE (`#37`), GradientText advance-carry, Slice C gate

---

## Verdict (one screen)

Landing **path re-home alone is not enough** — and is actively dangerous if shipped without a schema fix.

Three stacked defects. Fix order is forced:

| Layer | Symptom today | After path-only | Required |
|-------|---------------|-----------------|----------|
| **A. Path** | `pr-aggregate` always empty (`Merging runs: `) | Aggregate runs | Re-home `parity-shard-N` → `pr-<run>-shard-N` (PATH-BUG sketch) |
| **B. Schema** | Gate never sees real data (blocked by A) | **False green** | Aggregate emits gate-readable rows; gate must not pass on 0 cases |
| **C. Policy** | H3 partially fixed by T0/T6; KF ceiling still 25 | N/A until A+B | Ratchet KF ceiling; PR-gate **primary viewport only** |

**Do not merge a “path re-home” PR that leaves B broken.** One CI PR for A+B is fine; C can be a same-night follow-up or the bottom half of the same PR if green is proven first.

---

## Layer A — path (already diagnosed)

See `trench/forensics/2026-07-11-pr-aggregate-PATH-BUG.md`.

- Upload strips run-id dir → artifact root = `swarm_report.json`
- Download lands at `parity-results/parity-shard-N/`
- Discover expects `parity-results/parity-shard-*/pr-*` → always empty

**Minimal fix:** re-home on aggregate side using `github.run_number` (PATH-BUG bash sketch). Mirror nightly.

---

## Layer B — schema mismatch (NEW, critical)

### What aggregate writes

`scripts/parity_aggregate.py` → `aggregate_from_results` returns:

```text
{
  "timestamp", "summary", "fix_scoreboard", "taxonomy",
  "cases": [ { case_id, viewport, diff_pct, passed, stable, threshold, ... } ]
}
```

**No `results` key.** Field is `diff_pct`, not `diff_pct_median`.

### What the gate reads

Workflow:

```bash
python3 scripts/parity_gate.py \
  --mode test_results --level pr_merge \
  --report parity-results/aggregate_report.json \
  --per-case-thresholds --max-diff 25
```

`gate_test_results`:

```python
results = report.get("results", [])   # → []
diff = r.get("diff_pct_median", r.get("diff_pct", 100.0))
```

With forced `--mode test_results` and empty `results`:

```text
✓ PASS: All 0 case(s) within max diff 25%
GATE: PASSED
```

**Path re-home without B = decorative red becomes decorative green.** That is worse than today (at least today screams FAILURE).

### Required fix (pick one primary; do both if cheap)

**B1 — normalize at aggregate (preferred, one writer):**  
When writing `aggregate_report.json` for CI, also emit:

```python
"results": [
  {
    "case_id": c.case_id,
    "viewport": c.viewport,
    "diff_pct_median": c.diff_pct,   # alias
    "diff_pct": c.diff_pct,
    "passed": c.passed,
    "stable": c.stable,
    "threshold": c.threshold,
    "diff_pct_variance": ...,        # if available from swarm row
    "error": None,
  }
  for c in case_summaries
]
```

Keep `cases` for humans / scoreboard tools.

**B2 — normalize at gate (defensive):**  
If `results` missing/empty and `cases` present, map `cases` → internal result rows (`diff_pct` → median).

**B3 — hard fail empty gate (mandatory either way):**

```python
if not results:
    print("✗ FAIL: gate report has zero cases (schema/path bug)")
    sys.exit(1)
```

Never allow “0/0 pass.” This is the tripwire that would have caught B immediately after A.

### Local verification without full CI

After A+B on a branch:

```bash
# Use downloaded PR #37 shards as fixtures:
# /tmp/parity-shard-check/parity-shard-{0..3}/swarm_report.json
# 1) re-home as pr-29141476634-shard-N (or any run id)
# 2) parity_aggregate.py --runs ... --results-root ... -o /tmp/agg.json
# 3) jq '.results | length' /tmp/agg.json   # must be ≥ 26 (see Layer C)
# 4) parity_gate.py --mode test_results --level pr_merge \
#      --report /tmp/agg.json --per-case-thresholds --max-diff 25
# Must NOT print "All 0 case(s)".
```

---

## Layer C — policy honesty (after A+B produce real rows)

### C1 — known_fail ceiling vs T6

T0 wiring (live on master):

```python
limit = max_diff if g["known_fail"] else min(g["threshold"], max_diff)
```

Workflow still passes `--max-diff 25`. So:

| Case class | Effective CI limit |
|------------|-------------------|
| Fixed (not KF) | `min(campaign thr, GATE_SCOPE_CAPS, 25)` → t8 builtins/micro, t15 websuite — **honest** |
| `known_fail: true` | **flat 25%** — can worsen from 16→24 without failing |

T6 collapsed campaign specials to t15. Leaving KF at 25 re-opens a free-pass band for the worst pages.

**Ratchet (after A+B proven):** change PR (and nightly) gate to `--max-diff 15` **or** better:

```python
# known_fail: may not exceed scope campaign ceiling (T6 t15 / scope cap)
limit = min(g["threshold"], scope_cap) if g["known_fail"] else min(g["threshold"], scope_cap)
# optional: still allow KF to fail "pass" semantics but fail only if diff > ceiling
```

Simplest ship: `--max-diff 15` everywhere CI still passes it as the KF ceiling. Document that KF means “may fail t15 pass bit” not “may float to 25.”

**Do not** drop `--max-diff` entirely without checking `level_defaults(pr_merge)` → **0.5%** — that would red-lock every PR.

### C2 — multi-viewport exploit rows vs PR gate (NEW, from #37 artifacts)

PR swarm (`parity.yml` pr-swarm):

```text
--exploit-top 3
--exploit-iterations 2
--exploit-viewports 800x600,1280x800
```

Scout uses **native** case viewport; exploit re-runs worst cases at fixed VIEWPORTS. Artifacts from run `29141476634` show many **100.0%** rows at non-native sizes with empty taxonomy/errors — almost certainly **missing baseline / dimension hard-fail**, not a 100% pixel paint miss.

Examples (same PR, same engine):

| Case | Native-ish row | Exploit / other VP |
|------|----------------|--------------------|
| combinators | 800×800 → **6.19 PASS** | 800×600 / 1280×800 → **100** |
| specificity | 800×600 → **5.45 PASS** | 1280×800 → **100** |
| css-selectors | 800×1200 → **18.97** (KF) | 800×600 / 1280×800 → **100** |
| settings | 1024×768 → **18.43** (KF) | 800×600 / 1280×800 → **100** |

Campaign scoreboard (min-diff per case on this run) ≈ **21/26 @ t15** — matches Atlas overnight narrative. Gate that scores **every** `(case_id, viewport)` row will either:

- **false-red** forever on exploit 100s (if ceiling ≤25 still fails 100), or  
- if someone raises ceiling to absorb 100s, **false-green** on real regressions.

**PR-gate policy (required with A+B):**

Gate **registry-primary viewport only** for merge:

1. For each `case_id` in `cases/registry.json`, the gated row is the one whose `(width,height)` matches registry (or viewport name equals `f"{w}x{h}"`).  
2. Exploit / extra VP rows stay in the artifact for digs and nightlies — **do not** block `pr_merge`.  
3. Optional nightly: gate all VPs only when baselines exist for that size (else tag `instrument/no_baseline` and exclude).

Implementation sketch in `gate_test_results`:

```python
# when --primary-viewport-only (default for pr_merge):
# drop rows where (case_id, w, h) != registry native
```

Wire workflow:

```bash
python3 scripts/parity_gate.py ... --per-case-thresholds --max-diff 15 --primary-viewport-only
```

### C3 — known_fail ledger hygiene (orthogonal, same PR ok)

From registry @ `8e00d22` (9 KF):  
`about, css-selectors, form-controls, gradient-no-radius, gradient-radius-only, image-gallery, images-intrinsic, settings, sticky-scroll`

#37 primary residuals still **>15** (campaign-native):

| Case | ~diff (run 29141476634) | Notes |
|------|-------------------------|-------|
| image-gallery | 21.4 | thr 10; still KF |
| css-selectors | 19.0 | still KF — heatmap still justified if dig residual >15 |
| settings | 18.4 | still KF |
| sticky-scroll | 18.3 | still KF |
| about | 16.8 | still KF |

`images-intrinsic` ~9.3 / thr 10 and `form-controls` ~9.9 / thr 12 at native — **candidates to clear `known_fail`** after A+B so they ratchet permanently (T0 contract). Do that in a **follow-up** once gate is honest, not as a silent registry edit inside the path PR without numbers in the PR body.

---

## Recommended PR plan for Atlas

### PR-CI-1 — “parity aggregate path + gate schema” (one night, unblocks honesty)

**Files (expected):**

- `.github/workflows/parity.yml` — re-home step in `pr-aggregate` + `nightly-aggregate` (PATH-BUG sketch)
- `scripts/parity_aggregate.py` — emit `results[]` alias (B1)
- `scripts/parity_gate.py` — empty-report hard fail (B3); accept `cases` fallback (B2); **`--primary-viewport-only`** (C2) default-on for `pr_merge` level
- optional unit: tiny fixture JSON under `scripts/testdata/` proving 0-case fails and native-only filters exploit 100s

**Non-goals for CI-1:** engine, thresholds table, KF flag flips, B2 IFC, GradientText.

**Acceptance:**

1. PR swarms green.  
2. Aggregate log: `Merging runs: pr-N-shard-0,...,pr-N-shard-3` non-empty.  
3. Gate log: **N ≥ 26** cases considered (native only), **not** “All 0 case(s)”.  
4. Gate outcome matches campaign: fixed cases within t8/t15; KF may fail pass bit but not explode to 100 from exploit rows.  
5. No engine LOC.

### PR-CI-2 — “KF ceiling → 15 + ledger pass” (same night or next)

1. Workflow `--max-diff 25` → `15` (or code-side KF uses scope cap).  
2. Clear `known_fail` on cases now under thr at native (likely `images-intrinsic`, maybe `form-controls` / gradient micros if still green).  
3. Leave css-selectors / settings / sticky / about / image-gallery as KF until digs land.

**Do not mix with #37 B2 engine.** Orthogonal; can land before or after B2 merge.

---

## What NOT to do

- Re-run aggregate hoping A heals itself.  
- Path-only PR.  
- Raise `--max-diff` to 100 to silence exploit VPs.  
- Delete exploit phase (useful dig signal; wrong layer to gate).  
- Combine with IFC Slice C or GradientText advance-carry.  
- Threshold moves beyond 25→15 KF ceiling without Pete (T6 banlist) — the 25→15 KF ratchet **is** the T6 intent for free-pass removal; still call it out in PR body.

---

## Outside-eye checklist (Prometheus when PR opens)

- [ ] Re-home present for **both** pr-aggregate and nightly-aggregate  
- [ ] `aggregate_report.json` has non-empty `results` (or gate maps `cases`)  
- [ ] Empty report → exit 1  
- [ ] PR gate ignores exploit 100% non-native rows  
- [ ] Fixed cases still per-case thr + scope caps  
- [ ] KF ceiling ≤ 15 (if CI-2 included)  
- [ ] No engine / no B2 combine / no threshold specials resurrected  

---

## Evidence pins

| Item | Ref |
|------|-----|
| Master | `hiwavebrowser/hiwave-macos@8e00d22` |
| Path bug | `forensics/2026-07-11-pr-aggregate-PATH-BUG.md` |
| T0/T6 intent | PRs #32 / #33; `parity_gate.load_case_gates` docstring |
| Live residual | PR #37 run `29141476634` shards 0–3 (downloaded; native ~21/26 @ t15) |
| Workflow | `.github/workflows/parity.yml` pr-swarm exploit + pr-aggregate gate |

---

## Sequencing vs standing Atlas queue

```text
#37 B2 merge (waive aggregate OR land CI-1 first)
  ├─ CI-1 path+schema+primary-VP gate   ← this brief
  ├─ GradientText advance-carry         ← orthogonal chore brief
  ├─ CI-2 KF ceiling 15 + ledger clear  ← this brief §C
  └─ Slice C only after B2 wrap-hard green (gated brief)
```

Prometheus: design pin only. No merge. No force-push.
