# Test suite fidelity — make tests hard, stop coding to the meter

**Author:** Prometheus · **Date:** 2026-07-11  
**Audience:** Atlas (macOS / campaign owner), Athena (Windows / shared-crate peer)  
**Hub audited:** `hiwave/hiwave-macos` @ `1b56b01` (+ windows websuite/WPT sketch)  
**Mode:** design recommendations only — no production engine code from this seat

Pete asked: improve testing fidelity; harden visual scripts; recommendations **to both workers**; make tests hard enough for difficult work; **prevent coding-to-pass-the-tests**.

---

## Executive diagnosis

The campaign stack is a strong **progress meter** and a weak **correctness oracle**.

| Layer | What it is | Fidelity today |
|-------|------------|----------------|
| 26-case registry (`cases/registry.json`) | Fixed HTML + chrome-148 baselines, t15 pass | Good dig target, **overfit magnet** |
| `parity_test` / swarm | Capture → pixelmatch → optional style/rect side channels | **Pass/fail is pixel-only** |
| `parity_gate` | CI thresholds | **PR workflow overrides to max-diff 25%** — almost never blocks |
| Layout / style compare | Captured, partially implemented | **Does not gate** |
| WPT Tier-1 (`trench/WPT_TIER1_SUBSET.md`) | Designed | **Not a live gate** |
| Unit tests (layout ~239) | Contract tests | Good but **not coupled to visual claims** |
| Windows WPT tree | Handful of stub reftests | Not a real suite |

**The failure mode to kill:** agents (and humans) iterate until the 26 pages look greener without generalizing. That is already visible in history: stale claims, special-case pre-pass fixes, thresholds that absorb residual wrongness (sticky t25, text t20).

---

## What is already good (keep)

1. **Chrome for Testing pin** (148.0.7778.216) + `cases/registry.json` single source of truth (R0).  
2. **Pass rate @ t15** as campaign metric (beats average-diff polishing).  
3. **Dimension hard-fail** (no soft crop) + baseline-audit CI.  
4. **Blank-frame detection.**  
5. **Repro fixtures** under `parity-tests/repro/` (falsification culture).  
6. **Stylesheet inlining in parity-capture** (external `<link>` no longer silently missing).  
7. **Multi-viewport exploit path** in swarm (exists; underused as a *gate*).

---

## Fidelity holes (ranked by “lets you cheat”)

### H1 — Single fixed suite = overfitting surface (critical)

26 HTML files are the entire scoreboard. Any agent can memorize:

- exact selectors / DOM shape of sticky-scroll header  
- exact flex tree of settings  
- exact section titles of css-selectors  

**Symptom of success-without-correctness:** case N goes green; a 10-line DOM reorder of the same case goes red; a WPT reftest of the same feature never ran.

### H2 — Soft per-case thresholds absorb wrongness

```text
THRESHOLDS (parity_lib.py):
  sticky_scroll: 25%   text_rendering: 20%   gradients: 15%   default: 15%
```

A page can be **visibly wrong** and still “pass.” Campaign t15 is intentional for trench morale; it must not be the only bar forever, and **sticky@25 is a free-pass zone** for the historically worst layout class.

### H3 — CI PR gate is decorative

`.github/workflows/parity.yml` pr-aggregate:

```text
parity_gate.py --level pr_merge --max-diff 25
```

`level_defaults(pr_merge)` wants **0.5%**, but **`--max-diff 25` overrides it**. A PR can land with multi-percent per-case diffs and still “pass the gate.” That trains the fleet to ignore CI visual signal.

### H4 — Triple verification is computed, not enforced

`parity_test.py` builds `styles` and `rects` comparisons, then:

```text
result["passed"] = diff_pct <= result["threshold"]   # pixels only
```

You can “fix” by paint coincidence (wrong layout boxes, right-ish pixels) or fail with correct structure and noisy AA. Layout oracle (`layout_oracle_gate.py`) still stubs RustKit matching. `compare_layouts.py` matching is incomplete.

### H5 — No holdout / adversarial set

Nothing is reserved from dig sessions. Nothing auto-mutates campaign HTML (reorder, extra wrapper, synonym class names, second viewport). No “if your fix is general, these holdouts move too.”

### H6 — Instrument blind spots (from 2026-07-11 instrument audit)

- Alpha forced to 255 on PPM path.  
- `includeAA: true` (stricter than pixelmatch default — good for digs, bad if scores compared naively to external tools).  
- Cross-seat capture color contracts differ (macOS Unorm raw sRGB vs Windows linear→Srgb).  

### H7 — Windows suite parity not equal to macOS campaign gate

Windows has websuite copies + tiny `tests/wpt/*` stubs; CI visual gate history was thin. Divergent suites → divergent “done” definitions and shared-crate PRs optimized for one seat’s 26 pages.

### H8 — Unit tests don’t prove the claim the PR sells

Example: flex max-content / inheritance / advances. Unit tests exist, but PR narratives cite pixel deltas on named campaign cases. **No rule:** “pixel claim requires a named unit + a fixture that would fail without the fix.”

---

## Principles (both seats — non-negotiable)

1. **Campaign pages are a meter, not a curriculum.** Fixes must be justified by CSS/layout contracts + minimal fixtures.  
2. **Holdout fails ⇒ ship blocked**, even if campaign looks greener.  
3. **Pixels gate paint; boxes gate layout; styles gate cascade.** At least two of three for layout PRs.  
4. **No case-id branches in engine code.** If a dig needs `if case == "sticky-scroll"`, the test suite failed first.  
5. **Falsification fixture in every dig PR** (already culture — make it CI-visible).  
6. **Tighten thresholds only when instrument is honest** (alpha/color contracts documented).

---

## Recommendations — Atlas (macOS, campaign + scripts owner)

### A1. Land a **Holdout Suite** (highest anti-overfit ROI) — 1–2 days

- New scope in `cases/registry.json`: `"scope": "holdout"`.  
- **10–15 cases** Atlas authors (or Pete approves); **Prometheus/Athena dig sessions must not edit holdout HTML**.  
- Construction rules:
  - Same *features* as campaign (flex header, sticky, grid cards, cascade, gradients) but **different DOM/CSS** (no copy-paste of campaign trees).  
  - Include **perturbed clones**: campaign case with an extra wrapper `div`, class rename, section reorder, `dir`/`lang` noise.  
- Gate: **holdout pass rate reported every dig**; PR fails if holdout mean regresses > budget even if campaign improves.  
- Baselines: chrome-148 pin, same capture path.

### A2. Wire **structural gates** into pass/fail — 1 day

In `parity_test.py` / `parity_lib.py` aggregation:

| PR class | Must pass |
|----------|-----------|
| Layout (flex/grid/position/IFC) | pixels **and** rect max-delta ≤ N px on top-K elements (or fail `rects`) |
| Cascade / inheritance | pixels **and** style oracle on declared properties |
| Paint-only (gradient, gamma) | pixels + solid color probe fixture |

Start with **hard fail if `rects.error` or unmatched ratio > X`**, even if rough. Incomplete matcher is better as a **fail-open warning** only if explicitly tagged `oracle:soft`; default `oracle:hard` for new micros.

Ship `export_layout_json` quality contract: stable `data-testid` or `id` on campaign+holdout elements so matching isn’t positional heuristics.

### A3. Fix the **PR CI lie** — half day

Change `parity.yml` pr-aggregate:

- Remove `--max-diff 25` **or** replace with a **ratchet**:  
  `max_diff = min(25, max(campaign_p90 + 2, 8))` stored from last master run.  
- Near-term honest floor: **max-diff 15 (t15)** for full suite, **max-diff 8** for builtins+micro.  
- Separate job: **holdout-only gate** once A1 exists.  
- Keep `level pr_merge` variance/stability when iterations ≥ 2.

### A4. Multi-viewport as **gate**, not only exploit — 1 day

Native viewport pass is necessary, not sufficient. Require for merge on layout PRs:

- Case must pass (or not regress) on **two of** `{native, 800x600, 1280x800}`  
- R0 already hard-fails dimension mismatch — good.

Stops “looks perfect at 800×1000 only” overfitting (flex-positioning class).

### A5. Threshold policy rewrite — process, not grind

| Tier | Meaning | Suggested use |
|------|---------|----------------|
| **t15 campaign** | Trench progress meter (keep) | Digests, noon scoreboard |
| **t8 builtins+micro** | Product chrome + micro contracts | PR gate for those scopes |
| **t5 holdout layout subset** | Hard correctness | Nightly / release |
| **Per-case soft thresholds** | Phase out | Cap sticky/text specials; plan to collapse to t15 then t10 |

Do **not** lower thresholds by expanding AA ignore or crop. Instrument honesty first (F1 solid-color smoke already recommended).

### A6. Fixture factory for **adversarial micros** — ongoing

Every closed dig adds **two** artifacts, not one:

1. Minimal repro that **failed before** (existing culture).  
2. **Sibling adversarial** that changes DOM structure but not the CSS claim (wrapper, sibling insert, media-free width change). Both enter micro or holdout.

Script sketch: `scripts/mutate_case.py --wrap --shuffle-sections` for CI nightly noise (non-gating first week, gating week two).

### A7. Land **WPT Tier-1 runner** as orthogonal meter — multi-day

`trench/WPT_TIER1_SUBSET.md` already specifies the menu. Atlas owns:

- Pin WPT commit in `BASELINE-macos.md`  
- Report `Tier1 K/N` **separate** from 26-case campaign  
- Never average WPT into t15 (different animal)

This is the real “hard stuff” lane for IFC / text / flex.

### A8. Banlist for digs (process)

Post on WORK_QUEUE / PATH_FORWARD:

- No PR whose only validation is “campaign case X −N pp” without unit + repro.  
- No threshold raise without Pete.  
- No baseline re-pin without binary diff summary + approval.

---

## Recommendations — Athena (Windows, shared crates, paint stack)

### W1. **Mirror the registry + pin**, not a private suite

- Same `cases/registry.json` schema (or submodule/shared file).  
- Same chrome-148 (or explicit Windows pin if CfT differs — **document delta**).  
- Scoreboard columns: Windows pass@t15 **and** holdout when A1 exists.  
- Divergent HTML trees are a fidelity bug, not a feature.

### W2. **Kill decorative CI**

If Windows CI only builds, add:

- `parity-capture` (or Windows equivalent) on **builtins + micro** every PR  
- Gate at **t15** initially, ratchet down  
- Publish artifacts (PPM/PNG + layout.json) like macOS

Shared-crate PRs must show **both seats** or an explicit “macOS-only surface” label.

### W3. Paint/gamma lessons → **instrument tests**, not just PR #14

Portable probes as **CI fixtures** (both seats):

| Probe | Expect |
|-------|--------|
| `#1a1a2e` corner | exact (26,26,46) on honest path |
| 2-stop linear gradient strip | stop colors at known pixels |
| letter-spacing measure vs ink | within 0.5px once advance-contract lands |

These are hard to fake with page-specific CSS.

### W4. **WPT / reftest starter is not optional long-term**

Replace `tests/wpt/{layout,reftest}` stubs with the **same Tier-1 list** Atlas pins, even if runner is dumb (pass/fail screenshot or box dump). Depth > breadth.

### W5. Windows-specific anti-overfit

- DirectWrite vs CoreText: **contract tests** (advance sums, wrap points) not “settings looks fine.”  
- Never land a flex/IFC fix validated only on Windows builtins if macOS holdout exists — dual report.

### W6. Shared-crate PR template (Athena + Atlas)

```text
Claim:
Unit proof:
Repro HTML (before red / after green):
Adversarial sibling:
Campaign delta (secondary):
Holdout delta (blocking when present):
Other seat:
```

---

## Cross-seat package (do together)

| ID | Work | Owner | Blocks coding-to-tests? |
|----|------|-------|-------------------------|
| **T0** | Fix PR gate max-diff (25 → honest) | Atlas | Yes |
| **T1** | Holdout suite + gate column | Atlas author, both consume | **Yes (primary)** |
| **T2** | Pixel+rect dual gate for layout PRs | Atlas scripts; Athena mirrors | Yes |
| **T3** | data-testid stable layout export | Both engines | Enables T2 |
| **T4** | WPT Tier-1 runner + pin | Atlas lead, Athena port | Yes (generalization) |
| **T5** | Instrument smokes (color, alpha later) | Both | Prevents false greens |
| **T6** | Threshold collapse plan (sticky 25→15→10) | Pete lock + Atlas | Yes |
| **T7** | Adversarial mutate nightly | Atlas scripts | Yes |

Suggested order: **T0 → T1 → T2/T3 → T5 → T4 → T6/T7**.

---

## What “hard” looks like in 30 days

- Dig PR that greens sticky-scroll but reds holdout-sticky-variant → **blocked**.  
- Layout PR without rect oracle → **blocked**.  
- CI max-diff no longer 25.  
- Digest line: `campaign P/N @ t15 | holdout P/N @ t10 | tier1 K/M` — three numbers, no averaging.  
- Agents argue contracts and fixtures, not “how do I shave 0.4 pp off article-typography.”

---

## Explicit non-goals (this round)

- Full WPT import.  
- Perceptual SSIM as sole score (pixelmatch + boxes is enough if gated right).  
- Lowering thresholds by ignoring more AA.  
- Deleting the 26-case campaign (keep as meter).

---

## Falsification of *this* plan

If after T0–T2:

1. Agents still only cite campaign pp, or  
2. Holdout moves 1:1 with every campaign hack (holdout too similar), or  
3. Rect gate is always skipped via `oracle:soft`,  

…then fidelity did not improve — rewrite holdout for diversity and remove soft escape hatches.

— Prometheus  
Docs: this file; prior instrument audit `2026-07-11-instrument-colorspace-AUDIT.md`
