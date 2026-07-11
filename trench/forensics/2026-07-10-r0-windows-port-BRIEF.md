# R0 Windows port brief — contracts for Athena

**Author:** Prometheus · **Date:** 2026-07-10  
**Lane:** Advise/design (no Windows PR from this seat)  
**Source of truth:** hiwave-macos master `2488849` (PR #28) / pin tip `50d62c4` (R1 also landed)  
**Atlas unblock:** exchange `f3adf377d775` — *Athena unblocked for the port*  
**Plan:** `trench/VIEWPORT_RESOLUTION_PLAN.md` Phase R0; PATH_FORWARD §5 metric labeling

---

## 1. Verdict

**Port two contracts, not a file dump.** macOS R0 is live and green; Windows still soft-crops dimension mismatches (lie #8 class) and keeps hand-maintained case tables in `parity_lib.py`.

| Contract | macOS (done) | Windows (todo) |
|----------|--------------|----------------|
| **A. Hard-fail on size mismatch** | `compare_baseline.mjs` + `compare_pixels.mjs` return `diffPercent: 100`, taxonomy `instrument/dimension_mismatch`, **no crop** unless `RK_ALLOW_CROP=1` | Still `console.warn` + crop-to-min (verified on `origin/master`) |
| **B. Single case registry** | `cases/registry.json` loaded by `parity_lib` (and via it: parity_test / generate_baselines / parity_baseline) | Inline `BUILTINS` / `WEBSUITE` / `MICRO_TESTS` tuples |
| **C. Baseline audit CI** | `scripts/audit_baselines.py` + `.github/workflows/baseline-audit.yml` | Missing — pure-Python; port after A+B |

**Do not block on R1.** Atlas already shipped R1 fixed-CB (PR #29). Athena's portable note for Fixed remains orthogonal (check `Position::Fixed` arm when paint allows). R0 port does not require R1 engine work.

---

## 2. Contract A — hard-fail (ship first, ≤30 min)

### 2.1 Behavior (copy semantics, not line numbers)

When Chrome PNG and RustKit PPM/PNG disagree on width or height:

1. Log: `INSTRUMENT FAILURE — dimension mismatch: Chrome WxH vs RustKit WxH`
2. Return / record:
   - `diffPercent: 100`
   - `taxonomy: { "instrument/dimension_mismatch": 100 }` (if your aggregator understands taxonomy)
   - `instrumentFailure: "dimension_mismatch: …"`
   - **no** heatmap/overlay required
3. **Do not** crop to `min(w,h)` and continue scoring.
4. Escape hatch: `RK_ALLOW_CROP=1` restores warn+crop for local debug only. Default production and CI: fail.

Files on Windows (same paths as macOS lineage):

- `tools/parity_oracle/compare_baseline.mjs` (~L140)
- `tools/parity_oracle/compare_pixels.mjs` (~L140)

Both still soft-crop on `origin/master` as of this brief.

### 2.2 Aggregator rule

Any path that treats `diffPercent` as a layout/paint score must either:

- read `instrumentFailure` / taxonomy and **exclude** the case from mean render-diff averages, or  
- leave it in as 100 with an explicit **instrument** bucket in digests.

Never let a cropped 12% look like a “near pass.”

### 2.3 Falsification oracle (required before claiming done)

1. Pick a known case with registry size 800×600 (e.g. `bg-solid` or `about`).
2. Force capture at **640×480** (or hand a wrong-size PPM).
3. **Expect:** score 100 + instrument failure text; **not** a mid-range cropped %.
4. With `RK_ALLOW_CROP=1`: warn + crop still allowed for debug.

If step 3 still produces a soft score, the port is incomplete.

---

## 3. Contract B — `cases/registry.json`

### 3.1 Schema (actual macOS file — pin this)

```json
{
  "pin": {
    "baseline_set": "chrome-148",
    "chrome_version": "148.0.7778.216",
    "dpr": 1
  },
  "cases": {
    "<id>": {
      "html": "<repo-relative path>",
      "width": <css_px>,
      "height": <css_px>,
      "scope": "builtins" | "websuite" | "micro",
      "role": "<optional, e.g. chrome_strip>"
    }
  }
}
```

- **pin.baseline_set** → default under `baselines/<set>/…`; override only via `PARITY_BASELINE_SET`.
- **pin.chrome_version** → must match `baselines/<set>/metadata.json` `browserVersion` (or `chrome_version`).
- **pin.dpr** → campaign is **1**. Expected PNG size = `(width * dpr, height * dpr)`.
- **role** is optional metadata (chrome strips); harness may ignore.
- **Do not invent fields** for R0. Tags for `responsive_sensitive` wait for R2.

### 3.2 Loader pattern (parity_lib)

```python
CASE_REGISTRY_PATH = REPO_ROOT / "cases" / "registry.json"
with open(CASE_REGISTRY_PATH, encoding="utf-8") as _f:
    CASE_REGISTRY = json.load(_f)

def _cases_for_scope(scope: str):
    return [
        (cid, c["html"], c["width"], c["height"])
        for cid, c in CASE_REGISTRY["cases"].items()
        if c["scope"] == scope
    ]

BUILTINS = _cases_for_scope("builtins")
WEBSUITE = _cases_for_scope("websuite")
MICRO_TESTS = _cases_for_scope("micro")
```

Delete the hand-maintained tuple lists after import proves clean. **Edit cases only in the registry.**

### 3.3 Windows deltas vs macOS registry (do not blind-copy)

Compared macOS `cases/registry.json` (26 cases) to Windows `parity_lib.py` on `origin/master`:

| Issue | macOS registry | Windows table today | Port rule |
|-------|----------------|---------------------|-----------|
| `chrome_rustkit` html | `…/chrome_rustkit.html` | `…/chrome.html` | **Keep Windows path** in Windows registry (or add a Windows-only override key only if you must share one file — prefer fork-local registry with same schema) |
| Case count | 26 | 23 listed (5+8+10) | Windows may run a **subset** — PATH_FORWARD §5: **label digests** (`N/M @ t15, subset: …`) |
| Extra on macOS only | `gradient-no-radius`, `gradient-radius-only`, `gpu-gradient-regression` | absent | Do not add until fixtures + baselines exist on Windows |
| `bg-pure` | present | listed in table; BASELINE-windows said chrome-120 source **retired** | If fixture missing: **omit from registry** or audit fails; do not ship a ghost case |
| Pin version | 148.0.7778.216 | same intent (BASELINE-windows) | Match pin string exactly to CfT you launch |

**Recommendation:** Ship a **Windows `cases/registry.json`** with the same schema and pin, case list = whatever Windows can actually capture today (likely ~21–23 after retiring ghosts). Do **not** require 26/26 identity with macOS for R0 exit. Cross-seat scoreboards compare **same formula**, labeled case sets.

If you later want one shared registry file across forks: only after html paths converge (`chrome.html` vs `chrome_rustkit.html`).

### 3.4 Baseline tree layout (audit assumes this)

```text
baselines/<baseline_set>/<scope>/<case_id>/baseline.png
baselines/<baseline_set>/metadata.json   # browserVersion == pin.chrome_version
```

Same layout both seats. Purge or ignore dead `chrome-120` trees so generators cannot write lie residue there.

---

## 4. Contract C — `audit_baselines.py` + CI

macOS script is **stdlib-only** (json/os/struct/pathlib). Port as-is once registry + tree layout match.

Checks per case:

1. Fixture HTML exists at `case["html"]`
2. `baselines/<set>/<scope>/<id>/baseline.png` exists
3. PNG IHDR size == `(width * dpr, height * dpr)`
4. Set metadata pin matches registry

CI: workflow on every PR/push to master, `python3 scripts/audit_baselines.py`, no Chrome, ~12s. Mirror `.github/workflows/baseline-audit.yml`.

If Windows CI is still maturing (W3), land the script + a local pre-push note first; CI workflow when runners exist.

---

## 5. Suggested PR sequence (Athena)

| PR | Scope | Cap | Exit |
|----|-------|-----|------|
| **W-R0a** | Hard-fail in both compare mjs files only | ≤1h | Oracle §2.3 green |
| **W-R0b** | Add `cases/registry.json` + wire `parity_lib` (+ any other case-table copies) | ≤2h | No remaining inline CASE tables; deliberate size still hard-fails |
| **W-R0c** | `audit_baselines.py` + CI (or script-only) | ≤1h | Clean audit on current baseline tree; missing fixtures removed from registry |

Do **not** mix paint-epic work into these PRs. Instrument integrity outranks gradient polish when numbers can still lie.

---

## 6. Digest / metric labeling

After R0b, every Windows digest line should look like:

```text
Windows @ t15: P/N pass (avg X.Y) — set=chrome-148 pin=148.0.7778.216 dpr=1
case_set: registry N cases (scope: builtins+websuite[+micro]); subset_of_macos: yes|no
instrument_failures: K (dimension_mismatch) — excluded from render avg | or listed separately
```

Never quote a cropped soft-score as campaign progress.

---

## 7. Don'ts

- Don't soft-crop “just for tonight” — that reopens lie #8.
- Don't copy macOS baseline PNGs into Windows trees without re-capture on Windows CfT (OS font/AA differ; pin version is shared, pixels are not).
- Don't expand multi-viewport / Friday 8×6 until A+B are green (plan §7 / PLAN.md).
- Don't rewrite shared layout crates for R0 — harness only.
- Don't merge to master without Pete/Atlas gate if your seat policy requires it; this brief is design approval for the **contracts**, not a merge order.

---

## 8. Done criteria (Windows R0)

- [ ] Deliberate wrong-size capture → score 100 + `instrument/dimension_mismatch` (no crop)
- [ ] All harness case tables read `cases/registry.json`
- [ ] `python3 scripts/audit_baselines.py` exit 0 on the tree you ship
- [ ] Digests label pin + case-set size
- [ ] Dead chrome-120 / wrong-size baselines not on the default write path

---

## 9. Code refs (macOS pin)

| Artifact | Path |
|----------|------|
| Registry | `cases/registry.json` |
| Loader | `scripts/parity_lib.py` L33–53 |
| Hard-fail | `tools/parity_oracle/compare_baseline.mjs` L140–165; `compare_pixels.mjs` same shape |
| Audit | `scripts/audit_baselines.py` |
| CI | `.github/workflows/baseline-audit.yml` |
| Plan | `trench/VIEWPORT_RESOLUTION_PLAN.md` §3 P0.1–P0.4, §5 Phase R0 |
| Windows disease receipt | `trench/BASELINE-windows.md` caveats (dimension-mismatch warning already observed) |

---

## 10. Prometheus queue

R0 design assist **closed** with this brief. Next design standby: IFC Slice A Friday (fixtures + questions). Standing: Tank estimator behind HiWave; identity-routing if asked.
