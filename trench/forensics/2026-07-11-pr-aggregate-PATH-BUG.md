# CI root cause: pr-aggregate always empty (not a flake)

**Author:** Prometheus · **Date:** 2026-07-11 (grind tick)  
**Lane:** design / infra diagnosis only — no workflow merge from this seat  
**Affects:** `hiwave-macos` `.github/workflows/parity.yml` (`pr-aggregate` + twin `nightly-aggregate`)  
**Unblocks:** honest green/red on every PR; currently every recent Parity Gate run fails aggregate even when all four swarms pass (incl. #37)

---

## Verdict

**Deterministic path bug in artifact layout ↔ aggregate discovery.**  
Not pixel failure. Not flake. **Re-running the job will not fix it.**

For `hiwave-macos#37` (B2): outside-eye **APPROVE still holds**. Swarm 0–3 green is the real PR signal today. Policy choice for Atlas/Pete:

1. **Waive aggregate** and merge #37 (engine is fine), **then** land a 10-line CI fix PR; or  
2. Land the CI fix first (or stacked under B2) so #37 gets an honest rollup.

Do **not** rewrite IFC/B2 engine code to chase this red X.

---

## Evidence (PR #37 run `29141476634`)

| Check | Result |
|-------|--------|
| pr-swarm 0–3 | SUCCESS |
| pr-aggregate | FAILURE |
| Log | `Merging runs: ` (empty) → `Error: No data to aggregate` |

Artifacts present and non-trivial:

| Artifact | Size |
|----------|------|
| parity-shard-0 | ~2.3 MB |
| parity-shard-1 | ~2.3 MB |
| parity-shard-2 | ~1.7 MB |
| parity-shard-3 | ~1.1 MB |

Downloaded `parity-shard-0` layout (actual):

```text
swarm_report.json          ← at artifact ROOT
summary.txt
about/...
css-selectors/...
gradients/...
```

**No** nested `pr-<run>-shard-0/` directory inside the artifact.

Same failure pattern on every recent Parity Gate run inspected (#33–#37 push/PR): aggregate red, not suite-specific.

---

## Root cause

### What swarm writes

```text
parity-results/pr-${{ github.run_number }}-shard-${{ matrix.shard }}/swarm_report.json
```

(`parity_swarm.py` → `results_root / run_id / …`)

### What upload does

```yaml
# pr-swarm
- uses: actions/upload-artifact@v4
  with:
    name: parity-shard-${{ matrix.shard }}
    path: parity-results/pr-${{ github.run_number }}-shard-${{ matrix.shard }}/
```

`upload-artifact@v4` uploads the **contents** of that directory. The run-id folder name is **not** preserved inside the artifact.

### What download does

```yaml
# pr-aggregate
- uses: actions/download-artifact@v4
  with:
    pattern: parity-shard-*
    path: parity-results/
    merge-multiple: false
```

With `merge-multiple: false`, each artifact lands under its **name**:

```text
parity-results/parity-shard-0/swarm_report.json
parity-results/parity-shard-1/swarm_report.json
…
```

### What discovery expects

```bash
RUNS=$(ls -d parity-results/parity-shard-*/pr-* …)
# expects: parity-results/parity-shard-0/pr-NNN-shard-0/
```

That path **never exists**. `RUNS` is always empty → `parity_aggregate.py --runs ""` → `No data to aggregate`.

`load_swarm_report` also wants `results_root / <run_id> / swarm_report.json` (e.g. `parity-results/pr-42-shard-0/swarm_report.json`), not `parity-results/parity-shard-0/swarm_report.json`.

### Nightly twin

Same bug shape:

```text
upload:  parity-results/nightly-…-shard-N/   (contents only)
discover: parity-results/nightly-shard-*/nightly-*
```

Fix both jobs in one PR.

---

## Recommended fix (minimal, one CI PR)

**Prefer re-home on the aggregate side** using known `github.run_number` — no change to swarm output contract, matches `parity_aggregate.py` run-id layout.

### Patch sketch — `pr-aggregate` "Aggregate shards" step

```bash
# After download-artifact@v4 (merge-multiple: false):
#   parity-results/parity-shard-N/{swarm_report.json, cases…}
# Re-home to layout parity_aggregate.py expects:
#   parity-results/pr-<run>-shard-N/swarm_report.json

set -euo pipefail
RUN_IDS=()
for art in parity-results/parity-shard-*; do
  [ -d "$art" ] || continue
  shard="${art##*-}"
  run_id="pr-${{ github.run_number }}-shard-${shard}"
  dest="parity-results/${run_id}"
  if [ ! -f "${dest}/swarm_report.json" ]; then
    mkdir -p "$dest"
    # contents only (artifact has no nested run-id dir)
    mv "$art"/* "$dest/" 2>/dev/null || true
    rmdir "$art" 2>/dev/null || rm -rf "$art"
  fi
  if [ ! -f "${dest}/swarm_report.json" ]; then
    echo "ERROR: missing swarm_report.json under ${dest}" >&2
    ls -la parity-results/ || true
    find parity-results -maxdepth 3 -type f | head -50
    exit 1
  fi
  RUN_IDS+=("$run_id")
done

if [ ${#RUN_IDS[@]} -eq 0 ]; then
  echo "ERROR: no shard artifacts re-homed" >&2
  exit 1
fi

RUNS=$(IFS=,; echo "${RUN_IDS[*]}")
echo "Merging runs: $RUNS"
python3 scripts/parity_aggregate.py \
  --runs "$RUNS" \
  --results-root parity-results \
  --output parity-results/aggregate_report.json
```

Mirror for `nightly-aggregate` with `nightly-${{ github.run_number }}-shard-${shard}` and `nightly-shard-*`.

### Alternative (upload-side)

Stage so the artifact **includes** the run-id directory name:

```yaml
- name: Stage shard (preserve run-id dir name)
  run: |
    mkdir -p staging
    cp -a "parity-results/pr-${{ github.run_number }}-shard-${{ matrix.shard }}" staging/
- uses: actions/upload-artifact@v4
  with:
    name: parity-shard-${{ matrix.shard }}
    path: staging/
```

Then existing `ls -d parity-results/parity-shard-*/pr-*` works. Slightly more moving parts on every swarm job; re-home-on-aggregate is fewer lines total if nightly is fixed the same way.

### Verification for the CI PR

1. Open a no-op or docs-only PR (or re-run #37 after cherry-pick).  
2. All four `pr-swarm` green.  
3. Aggregate log: `Merging runs: pr-N-shard-0,pr-N-shard-1,pr-N-shard-2,pr-N-shard-3` (non-empty).  
4. `aggregate_report.json` artifact uploaded.  
5. Gate step runs (may still be weak — see below).

---

## Orthogonal debt (do not mix unless tiny) — SUPERSEDED 2026-07-11 later

**Full implement pin:** `2026-07-11-ci-gate-honesty-IMPLEMENT.md`.

Do **not** land path re-home alone. After re-home, aggregate emits `cases[]` while the gate reads `results[]` → **false green (0 cases)**. Also: PR exploit viewports produce 100% non-native rows that must not block `pr_merge`. KF ceiling still 25 vs T6 t15.

**CI-1** = path re-home + schema alias + empty-gate hard-fail + primary-viewport-only.  
**CI-2** = KF ceiling → 15 + clear stale `known_fail` flags.  
Do not conflate "aggregate finds data" with "gate is strict."

---

## Guidance by seat

### Atlas

- **#37 B2:** merge when ready on swarm-green + outside-eye APPROVE; aggregate red is **infra**, not B2.  
- **Next small PR (or same-day chore):** path re-home in `parity.yml` for pr + nightly aggregate. Title e.g. `ci: re-home shard artifacts so pr-aggregate finds swarm_report`.  
- After CI green: GradientText advance-carry (see PR37-REVIEW residual / advance-contract IMPLEMENT).  
- Do not combine B2 engine, GradientText, and CI path in one PR.

### Athena

- If Windows parity workflows copy this upload/download pattern, apply the same re-home before trusting aggregate-on-PR.  
- No Windows code required this tick.

### Pete

- Scoreboard: treat swarm-shard conclusions as the PR visual signal until the path fix lands.  
- Optional: allow Atlas to merge #37 with documented aggregate waive.

---

## Correction to prior Prometheus language

`2026-07-11-ifc-b2-PR37-REVIEW.md` called this an "empty shard merge **flake**."  
**Retract "flake":** it is a **stable layout mismatch**. Re-run does not heal it; the re-home patch does.

---

## Non-goals

- Engine changes  
- Threshold policy rewrite in the same PR (unless Atlas wants a one-liner later)  
- Prometheus merging workflows or #37
