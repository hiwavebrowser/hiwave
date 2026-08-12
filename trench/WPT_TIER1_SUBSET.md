# WPT Tier-1 subset (≤200) — Friday north-star seed

**Author:** Prometheus · **Date:** 2026-07-10 · **Updated:** 2026-07-15  
**Purpose:** **Seed source for the MANIFEST** (was: menu). W0a landed 2026-07-29 — the live list is
`hiwave-macos:trench/wpt/MANIFEST.json`, pinned to WPT `a6f29b0` (PR #69). This file is where the seed
came from and where the next growth round shops; it is no longer the thing a runner reads.  
**Rule:** Prefer tests that fail if wrap/line metrics/cascade are wrong; skip Chrome-bug reftests.  
**Gate:** Phase 0.5 **GATE OPEN** — implement pin `trench/forensics/2026-07-15-wpt-phase05-GATE-OPEN.md` (W0a manifest → W0b engine reftest → W0c Friday field). Dig preconditions met (wrap production, IFC A–C, gallery closed); runner still stub until W0b.  
**Seed size for first K/N:** ≤30 from this menu (see GATE-OPEN §4), not the full ~200 ceiling.

Sources: css-text-3, css-inline-3, css-flexbox-1 (minimal). Paths are WPT-relative
(`css/css-text/...`). Exact filenames vary by WPT pin — resolve against the pin
Atlas chooses for the runner — now resolved: `hiwave-macos:trench/wpt/MANIFEST.json` (JSON, not YAML),
14 entries verified verbatim against pinned directory listings.

---

## Tier-1A — css-text (wrap & white-space) ~80

**white-space / soft wrap**

- `css/css-text/white-space/white-space-collapse-*` (normal, pre, pre-wrap, pre-line, break-spaces) — pick ≤15 representative
- `css/css-text/white-space/pre-wrap-001` … small set of line-break visuals
- `css/css-text/line-breaking/*` — basic break opportunities only (skip complex UAX14 deep)

**overflow-wrap / word-break**

- `css/css-text/overflow-wrap/overflow-wrap-break-word-*` (≤10)
- `css/css-text/word-break/word-break-normal-*` (unbreakable overflows — our §5.2 contract)
- `css/css-text/word-break/word-break-break-all-*` (≤5) — only after normal is green

**text-align**

- `css/css-text/text-align/text-align-*.html` start/end/left/right/center (≤12)

**Skip for Tier-1:** hanging-punctuation, text-spacing-trim deep, full justification algorithms.

---

## Tier-1B — css-inline / line boxes ~40

- `css/css-inline/baseline-source/*` (≤10) if present in pin
- Line-height / strut class: `css/css-inline/animation/*` **skip**; prefer static:
  - vertical-align baseline/middle/sub/super (≤15)
- Mixed inline: strong/em/a on one line (if reftests exist under css-inline or html/rendering)

**Goal signal:** mixed inlines share a line (IFC slice E) — when these go green, digests may say “line boxes.”

---

## Tier-1C — flex (settings-class bugs) ~40

- `css/css-flexbox/flex-item-*/height-*` definite height vs content (≤15)
- `css/css-flexbox/align-items-*` (≤10)
- `css/css-flexbox/flex-wrap-*` basic (≤10) — card-grid class

**Skip:** nested grid+flex extravaganzas, order-heavy suites.

---

## Tier-1D — smoke HTML (local, not WPT) ~10

Keep campaign websuite cases as **orthogonal** meter; do not double-count as WPT.

---

## Runner contract (when Atlas builds it)

1. Pin WPT commit hash in `trench/BASELINE-macos.md`.  
2. Report: `Tier1 pass = K/N`, separate from campaign t15.  
3. Failures → link to slice ladder in `LINE_BOX_WPT_ROADMAP.md`, not random digs.  
4. Cap runtime: full Tier-1 under 5 minutes CI.

---

## This week’s ask

**Do not block pixel digs on this list.** Atlas lands §11b settings first.  
Prometheus/Atlas: resolve exact paths against pin when Phase 0.5 starts; this file is the **menu**.
