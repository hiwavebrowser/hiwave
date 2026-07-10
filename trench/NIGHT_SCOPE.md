# HiWave night scope — 2026-07-10 (Prometheus, post-#22)

**Pete direction:** keep working on HiWave.  
**macOS leads** (Windows deferred for major new tasking; portable notes still post).  
**Author:** Prometheus · advise only — Atlas executes.

---

## Scoreboard (honest)

| Basis | Pass @ t15 | Notes |
|-------|------------|--------|
| **#22 MERGED** master `c305ef0` | **re-measure required** | Merge 2026-07-10T13:15Z — do not quote PR-tree asterisk |
| Campaign high (pre-merge PR #22 tree) | **21/26 (80.8%)**, avg **11.9** | Expect committed ≈ this if suite stable |
| Daytime high 2026-07-09 | 19/26 (73.1%) | After line-box #15/#16 |
| Pre-#22 committed | 20/26 (76.9%) | backgrounds still fail until #22 |

**PR #22:** MERGED — https://github.com/hiwavebrowser/hiwave-macos/pull/22  
- backgrounds 27.3 → **12.98 PASS** on PR tree  
- Residual **+1.7px/row** strut font-metric (ledger, do not chase)  
- **Action:** Atlas full-suite on **committed** master + digest; then settings dig

**Forensic for next code unit:**  
`hiwave/trench/forensics/2026-07-10-post22-settings.md`

---

## Tonight's one unit (Atlas — pick ONE)

### Unit A — **Re-measure master + settings flex-item height** (preferred)

1. Clean master @ pinned CfT 148 — full suite → **committed** N/26, avg.  
2. Dig: flex **§11b** overwrites definite cross size (`flex.rs`) — repro already on master  
   `parity-tests/repro/toggle-height.html` (Case B: 26 → 40.4 as flex item).  
3. Fix: skip 11b expansion when `has_explicit_cross_size`; regression test; re-measure settings.  
4. Cap 2h. Absolute `inset:0` slider (4px) + h1/p margin collapse = secondary only if A alone does not flip.

**Done when:** digest quotes committed N/26 without “with PR #22 applied,” and either settings moved or a minimal PR is open with toggle Case B green.

### Unit B — **css-selectors residual** (only if settings already banked / blocked on review)

Selector/cascade paint — not another line-box rewrite. Confirm post-#22 score first.

### Unit C — **Phase 0.5 WPT stub** (only if pixel dig blocked)

Tier-1 ≤200 css-text / css-inline list + runner path. Spec: `LINE_BOX_WPT_ROADMAP.md` §5–6. Does not replace campaign metric.

---

## Line-box lane status (do not re-litigate)

| Slice | Status |
|-------|--------|
| 0–1 Production wrap + min-content text | **SHIPPED** (#15/#16) |
| A Mandatory breaks | cheap follow-on — only if suite proves need |
| B Advance-based breaks | after more atomic-inline ground |
| **True IFC / mixed-inline line boxes** | **Architectural** — Friday design, **not** a 2h nightly rewrite |
| #22 strut/border-box | **SHIPPED** on master |

Digests must not say "line boxes done" until mixed inlines share one line (slice E in roadmap).

---

## Explicit non-goals tonight

- Windows major tasking (macOS leads)  
- Engine re-unify (fastrender vs rustkit) — Friday only  
- Matching Chrome's +1.7px strut font delta  
- Full IFC rewrite / mid-word break hacks  
- New infrastructure layers  

---

## Prometheus grind (this seat)

1. Keep this file + roadmap honest against digests/PRs.  
2. Produce **small design/forensic briefs** Atlas can execute — not parallel rustkit PRs.  
3. Post exchange notes when a dig looks mis-aimed (Chrome-parity trap).

---

## Pete one-liners

- **#22 is in** — next metric truth is committed re-measure.  
- Next code dig: **settings flex-item definite height** (not IFC).  
- IFC = Friday scope, multi-session design, then trench.
