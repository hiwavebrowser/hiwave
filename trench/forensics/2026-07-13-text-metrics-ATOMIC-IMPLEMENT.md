# Atomic text-metrics epic — implement brief (gallery coupling + residual inventory)

> **SUPERSEDED for execution order / gallery hunt (2026-07-15):** use  
> `2026-07-15-text-metrics-ATOMIC-KICKOFF.md`. Night-15 closed gallery as **grid span gutters (#53)**;  
> dual-patch flips gallery to PASS t10. **§4 residual inventory + §4.4 form rules still load-bearing**  
> (re-verified in kickoff §3). Do not re-run open-ended H1–H5 hunt.

**Author:** Prometheus · **Date:** 2026-07-13 (grind tick, evening+)  
**Tree pin:** `hiwave-macos origin/master@8d7264d` (PR #51 tip; local checkout dirty+behind — **no checkout**)  
**Companions:**  
- `2026-07-13-normal-lineheight-WALL.md` (Atlas)  
- `2026-07-13-normal-lineheight-ENGINE.patch` (248 lines, model-only)  
- `2026-07-13-pr52-text-metrics-REVIEW.md` (Prometheus #52 APPROVE + order pin)  
**PR #52:** instruments only — still OPEN at brief time; **merge first**, then this epic.

---

## 0. One-screen verdict

| Claim | Status |
|---|---|
| Model for `line-height: normal` | **SETTLED** — Blink `round(ascent)+round(descent)+gap`; instruments on #52 |
| Land ENGINE.patch alone | **FORBIDDEN** — measured 24/26 → 23/26 |
| Form coupling (css-selectors) | **PROVEN** — Arial 13.33×1.2 = 16.00 coincidence; DIG-1/2 load-bearing |
| Gallery coupling | **UNNAMED until probe** — no form controls; still regressed 12.88→15.04 under correct model |
| This brief | **Implements the probe + ranked hypotheses + residual `*1.2` inventory + land order** so Atlas does not re-derive |

**Gate for merge of the atomic PR:** campaign **≥24/26** @ t15, holdout 6/6 green, css-selectors not re-red t15. Expect `about` + `image-gallery` to move (payoff cases).

---

## 1. Why gallery is the first hunt (not forms)

Forms are proven and formula-shaped (`single_line_box`, fixed Arial UA). Gallery is the **unnamed lock**:

- Websuite `image-gallery`: **zero `<img>`** — gradient placeholders + absolute caption overlays (Atlas falsified object-fit as dig; still true).
- Correct model still **hurt** gallery (12.88 → 15.04) while forms explain css-selectors. Something non-form is holding the wrong constant or amplifying Y error.
- Gallery is mostly **grid + absolute captions** (PR #51 just landed abs-overlay/caption). Line-height changes interact with that stack in ways form digs do not cover.

**Do not open the atomic PR by editing Button heights first.** Run §2 probe, name top |Δy| selectors, then edit.

---

## 2. Coupling probe (mandatory, offline Chrome, two-model A/B)

### 2.1 Inputs (all already on disk after #52 merge)

| Source | Path |
|---|---|
| Chrome ground truth | `baselines/chrome-148/websuite/image-gallery/layout-rects.json` (87 elements; VP 1280×800) |
| Chrome styles | `…/computed-styles.json` |
| Case HTML | `websuite/cases/image-gallery/index.html` |
| Flat model | current master (`LineHeight::Normal => font_size * 1.2`) |
| Metrics model | apply ENGINE.patch in a **worktree** (or temp branch); do not leave on master |

Also run the same probe on:

- `builtins/about` (last KF; pure text stack — payoff check)
- `websuite/css-selectors` (form coupling regression monitor)

### 2.2 What to emit (one table, ranked)

For each element present in **both** Chrome and RustKit layout dumps (match on `selector` string Chrome already uses):

| col | meaning |
|---|---|
| `selector` | Chrome selector |
| `Δy_flat` / `Δy_metrics` | RK.y − Chrome.y under each model |
| `Δh_flat` / `Δh_metrics` | RK.height − Chrome.height |
| `\|Δy\|_improve` | `abs(Δy_flat) − abs(Δy_metrics)` — **positive = metrics better** |
| `tag` | for filtering |

Sort by `abs(Δy_metrics)` descending, then by `abs(Δh_metrics)`.

**Ship as:** `scripts/probe_text_metrics_coupling.py` (or extend `probe_normal_lineheight.py`).  
**Hard requirement:** script must accept `--model flat|metrics` *or* two RK dumps side-by-side so the A/B is a pure post-process.

Pseudo:

```text
load chrome layout-rects.json
load rk_flat.layout-rects.json   # capture under master
load rk_metrics.layout-rects.json  # capture under patched worktree
join on selector
print top 25 by abs(dy_metrics), and top 25 by (abs(dy_flat)-abs(dy_metrics))  # who got worse
group mean |Δy| by selector prefix: body>h1, subtitle, gallery-item, image-overlay, aspect-, object-fit-
```

### 2.3 Capture note

Prefer whatever path already dumps **selector-keyed** rects (parity instrument / layout-rects export). If only the nested `*.layout.json` tree exists, walk `border_box` + tag/class — but Chrome join quality drops; invest one hour in selector export rather than fuzzy geometry matching.

Stale local dumps under `websuite/captures/image-gallery.layout.json` show absurd heights (~18k px) — **do not trust** them; re-capture on `8d7264d` (or #52 tip) after clean build.

---

## 3. Ranked hypotheses (pre-probe — falsify in order)

Chrome receipts on `image-gallery` (committed rects @ CfT-148):

| Element | Chrome y | Chrome h | Notes |
|---|---|---|---|
| `body > h1` | 40 | **38** | `font-size: 2em` → 32px on 16px root |
| `body > p.subtitle` | 88 | **18** | default 16px text; metrics model **exact** (wall: system-ui 16 → 18) |
| gallery origin (implied) | ~146 | — | 40 pad + 38 h1 + 10 mb + 18 sub + 40 mb |
| overlay `h3` (× many) | … | **18** | `font-size: 1em` |
| overlay `p` | … | **15** | `font-size: 0.8em` |
| aspect `h2` | 1044 | 24 | section header |
| body height | — | 1922 | full page |

### H1 — Header Y-cascade (global gallery shift) — **most likely primary |Δy| source**

Stack is pure normal-line-height + fixed margins:

```text
body padding-top 40
h1: 2em × normal  → Chrome h=38  (flat 1.2 ⇒ 32×1.2=38.4)
margin-bottom 10
subtitle: 1em × normal → Chrome h=18  (flat 1.2 ⇒ 19.2)
margin-bottom 40
→ gallery top
```

Flat model overstates subtitle by **+1.2px** and h1 by **~+0.4px** → gallery origin bias ~**+1.6px** under flat. Correcting normal should **pull gallery toward Chrome** on pure cascade… yet Atlas measured gallery **worse** under metrics. So either:

- RK's current h1/subtitle heights are **not** pure `to_px(Normal)` (other bugs dominate), or  
- H2/H3 dominate the pixel meter more than the 1–2px cascade.

**Probe falsification:** if mean |Δy| for all `.gallery-item` is ~constant and equals header stack error, H1 is load-bearing. If item-internal |Δy| varies by row/caption, look H2/H3.

### H2 — Absolute caption line boxes (local text / AA)

`.image-overlay` is `position: absolute; bottom: 0; padding: 15px`. Captions:

- `h3` Chrome h=18 (1em normal)  
- `p` Chrome h=15 (0.8em ≈ 12.8px font)

Absolute → out of flow for grid sizing **if** abs positioning is correct post-#51. Still paints every caption glyph. Metrics change alters line box height **inside** the overlay → bottom-aligned stack may grow upward by δ(h3)+δ(p)+gap.

**Probe falsification:** large |Δh| / |Δy| on `h3`/`p` under overlay with **near-zero** |Δy| on `.gallery-item` border boxes → pure paint/text coupling, not grid.

### H3 — Abs children still influence grid track sizing (residual #51)

If any path still contributes abs-overlay content height into row sizing, caption line-height changes **row tracks** → catastrophic multi-row Y drift (matches "correct model, worse score").

**Probe falsification:** `.gallery-item` border-box heights differ between models by more than subpixel noise despite `min-height: 200/416` in CSS. That is a **layout bug**, not a form-calibration issue — fix before recomposing controls.

### H4 — Section text / aspect flex centers

`aspect-section h2`, `.aspect-box .content` flex column labels, loading-section spans. Secondary page mass below the fold; can drag avg diff without flipping pass/fail alone.

### H5 — Forms (css-selectors only for this epic)

Not on gallery. Track in parallel on `css-selectors` probe run. See §4.

---

## 4. Residual hard-coded `font_size * 1.2` inventory (`origin/master@8d7264d`)

ENGINE.patch rewires **`line_height.to_px` call sites** via `resolve_line_height`. It does **not** touch these twins — decide each with Chrome rects under the **target** model.

### 4.1 Canonical wrong constant (rewritten by patch path)

| File | Line (approx) | Note |
|---|---|---|
| `crates/rustkit-css/src/lib.rs` | 1446 | `LineHeight::Normal => font_size * 1.2` — patch makes this fallback-only |
| same | 1461 | `as_multiplier() → Some(1.2)` for Normal — **confirm callers**; inheritance/serialization semantics |

### 4.2 Layout `to_px` sites the patch already retargets (verify still complete after rebase)

| File | Sites |
|---|---|
| `rustkit-layout/src/lib.rs` | ~1519, 1543, 2384, 4497 (incl. paint baseline path) |
| `rustkit-layout/src/flex.rs` | ~1028, 1083, 1400, 1403, 1422, 1425, 1479, 1488 |
| `rustkit-layout/src/grid.rs` | ~273, 324 |

After rebase onto post-#52 master: `git grep 'line_height\.to_px'` must be **empty** in layout (or only inside `resolve_line_height` / tests).

### 4.3 Hard-coded `* 1.2` NOT covered by ENGINE.patch — decision table

| Site | Role | Atomic-epic action |
|---|---|---|
| `lib.rs` ~1413 TextArea | `fs*1.2*rows+8` | Re-measure vs Chrome under metrics normal; rewrite only if height wrong |
| `lib.rs` ~1448 Checkbox/Radio | `fs*1.2` square | **Likely keep** as UA chrome size (not line-height); probe first |
| `lib.rs` ~1395–1452 `single_line_box` | TextInput/Button/Select | With author pad: `(fs+1)+author_pb` — **not** `to_px(Normal)`. Bare blob: `fs*1.5+8/12`. Re-validate DIG-1/2 under metrics; dual-update flex twins |
| `flex.rs` ~1048, 1352, 1456 TextArea | same as lib | **Mirror lib** — both or neither |
| `flex.rs` ~1051, 1370, 1462 Checkbox/Radio | same as lib | Mirror lib |
| `forms.rs` ~117, 147 | caret / selection height | Low board impact; twin constant after controls settle |
| `rustkit-text/.../macos.rs` ~684 | glyph atlas `ceil(fs*1.2)` | **OUT OF SCOPE** this PR — glyph tests required; separate chore |

### 4.4 Form re-composition rules (after gallery named)

1. Capture Chrome control border-boxes on `css-selectors` under committed rects (no live Chrome).  
2. Under metrics model, list RK control heights.  
3. Adjust **only** formulas that miss Chrome by ≥0.5px.  
4. Prefer keeping `single_line_box` author-pad branch; change blob constants if bare controls miss.  
5. **Never** lower KF ceilings to hide a miss.

---

## 5. Atomic land order (execution checklist for Atlas)

```text
[ ] 0. Merge #52 (instruments). CI cannot red-lock board.
[ ] 1. Worktree: apply ENGINE.patch; build; do NOT merge.
[ ] 2. Capture layout-rects (or equivalent) for:
       image-gallery, about, css-selectors
       under flat (master) AND metrics (worktree).
[ ] 3. Run coupling probe (§2). Paste top-25 table into PR body.
[ ] 4. Classify H1–H5 from table. If H3 (grid abs sizing): fix layout first.
[ ] 5. Recompose form controls (§4.3–4.4) under metrics; flex twins mandatory.
[ ] 6. Residual *1.2 decisions: keep / rewrite / defer (table in PR).
[ ] 7. Doc honesty: rustkit-css Normal comment + to_px_with_normal rustdoc
       ("already-resolved Blink-rounded normal px", not raw TextMetrics::height).
[ ] 8. Full campaign gate: ≥24/26 @ t15, holdout 6/6, css-selectors ≤ t15.
[ ] 9. Single PR (or stacked PRs with ONE merge gate). Title:
       "fix: line-height:normal from font metrics + dependents (atomic)"
[ ] 10. Port note in PR: shared resolve path; Athena ports call sites, not model.
```

### Explicit anti-patterns

- Model-only merge  
- "Fix buttons first" without gallery |Δy| table  
- object-fit dig on this case (0 `<img>`)  
- Threshold / KF games  
- Rewriting `rustkit-text` atlas height in the same PR  
- Lowering conf/min thresholds on Tank to free seats (orthogonal; do not mix)

---

## 6. Expected board shape (not a promise — a prior)

| Case | Role |
|---|---|
| `about` | Should improve if pure text metrics wall (16.49 KF) |
| `image-gallery` | Improves only if H1–H3 correctly fixed; may need layout fix beyond patch |
| `css-selectors` | Flat→metrics alone reds t15; **must** recompose or stay red |
| `images-intrinsic` | Mostly text labels; watch, don't dig object-fit |
| Holdout | Must stay 6/6 |

If after dependents the board is still 23/26 with **named** residual, stop and write a one-pager — do not thrash constants.

---

## 7. Athena / Windows

- No engine port until macOS atomic lands.  
- Instruments (#52) + this probe are pure tools once chrome-148 rects exist (page-mirror already).  
- When landing: port `resolve_line_height` call sites; do **not** re-derive Blink rounding.  
- Gradient/radial absence is orthogonal; label digests if suite differs.

---

## 8. Owners

| Seat | Action |
|---|---|
| **Atlas** | Merge #52 → probe → atomic PR per §5; Tank C3a stays parallel private track |
| **Athena** | Stand by for shared-crate port after macOS green; no re-model |
| **Prometheus** | Outside-eye on atomic PR (this brief is the pre-review checklist) |

---

*Design only. No merge, no force-push, no engine land from this seat. Files left on hub `trench/forensics` for Atlas commit lane.*
