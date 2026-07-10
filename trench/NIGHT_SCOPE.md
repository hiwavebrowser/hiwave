# HiWave night scope — 2026-07-10 (Prometheus)

**Pete direction:** keep working on HiWave.  
**macOS leads** (Windows deferred for major new tasking; portable notes still post).  
**Author:** Prometheus · advise only — Atlas executes.

---

## Scoreboard (honest)

| Basis | Pass @ t15 | Notes |
|-------|------------|--------|
| Campaign high (PR #22 tree) | **21/26 (80.8%)**, avg **11.9** | Open PR: inline-block border-box + strut descent |
| Daytime high 2026-07-09 | 19/26 (73.1%) | After line-box phases 1–2 merged (#15/#16) |
| Phase 0 re-pin | 9/26 (34.6%) | Historical floor after CfT 148 |

**PR #22 (OPEN):** https://github.com/hiwavebrowser/hiwave-macos/pull/22  
- backgrounds 27.3 → **12.98 PASS**  
- Zero regressions claimed; residual **+1.7px/row** strut font-metric (ledger, do not chase)  
- **Action:** Athena post-hoc or Pete merge under latency if dark; **do not start a second shared-crate dig on the same line metrics until #22 is in or explicitly abandoned**

---

## Tonight's one unit (Atlas — pick ONE)

### Unit A — **Land #22 + re-measure master** (preferred if review lag)

1. Get #22 merged (Athena ack or Pete latency merge).  
2. Full suite on clean master @ pinned CfT 148.  
3. Digest: new committed baseline pass rate (not PR-tree asterisk).  
4. Refresh worst-fail table for tomorrow.

**Done when:** master digests quote a **committed** N/26, not "with PR #22 applied."

### Unit B — **Next pixel dig: settings closest flip** (if #22 already merging)

Target: **settings** (~19-ish historically; confirm on post-#22 tree) — often the nearest t15 flip.  
Discipline: per-element y-table / first-divergence (same method as #22).  
Candidates if settings already near pass after #22:

| Priority | Case family | Why |
|----------|-------------|-----|
| 1 | **settings** residual | Closest historical flip; form controls / bg-clip-text |
| 2 | **css-selectors** residual | Selector/cascade paint, not "another line-box rewrite" |
| 3 | **gpu-gradient-regression** residual | Now measurable post image/layout groundwork |
| 4 | **sticky-scroll** | Paint-dominated; **scoped dig only**, not nightly nibble |

**Refuse:** mid-word break "fixes", unconditional strut on all atomics, fastrender detours (parity metric = **rustkit-***).

### Unit C — **Phase 0.5 WPT stub** (only if pixel dig blocked on review)

Stand up **Tier-1 ≤200** css-text / css-inline subset runner path + one Friday number.  
Does **not** replace campaign metric. Spec: `LINE_BOX_WPT_ROADMAP.md` §5–6.

---

## Line-box lane status (do not re-litigate)

| Slice | Status |
|-------|--------|
| 0–1 Production wrap + min-content text | **SHIPPED** (#15/#16) |
| A Mandatory breaks | cheap follow-on — only if suite proves need |
| B Advance-based breaks | after more atomic-inline ground from #22 |
| **True IFC / mixed-inline line boxes** | **Architectural** — Friday design item, **not** a 2h nightly rewrite |
| #22 strut/border-box | **In review** — slice of real line metrics, not full IFC |

Digests must not say "line boxes done" until mixed inlines share one line (slice E in roadmap).

---

## Explicit non-goals tonight

- Windows major tasking (macOS leads)  
- Engine re-unify (fastrender vs rustkit) — Friday only  
- Matching Chrome's +1.7px strut font delta  
- New infrastructure layers  

---

## Prometheus grind (this seat)

Queue reseeded to HiWave only. Headless ticks will:

1. Keep this file + roadmap honest against digests/PRs.  
2. Produce **small design/forensic briefs** Atlas can execute (repro HTML, first-divergence notes) — not parallel rustkit PRs.  
3. Post exchange notes when a dig looks mis-aimed (Chrome-parity trap).

---

## Pete one-liners

- **Merge #22** if Athena is dark past latency → unblocks honest master metric.  
- Next night after land: **settings or css-selectors**, not "start IFC."  
- IFC = Friday scope, multi-session design, then trench.
