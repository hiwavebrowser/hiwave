# Viewport & resolution coverage plan

**Author:** Prometheus · **Date:** 2026-07-10  
**Ask:** Support virtually all resolutions; today we only exercise a handful — audit correctness and plan coverage.  
**Audience:** Atlas (harness + engine), Athena (Windows parity), Pete (policy).

---

## 1. What we do today (facts)

### 1.1 Campaign metric = **one size per case**, not “all screens”

In `scripts/parity_lib.py` / `parity_test.py`, each case carries a **default (width, height)**:

| Bucket | Typical sizes in use |
|--------|----------------------|
| Builtins | 1280×800, 800×600, **1024×768**, **1280×100**, **1280×120** |
| Websuite | 1280×800, 800×1200, 800×1000, 800×600 |
| Micro | 800×600, 800×800, 900×1000, 800×1400, … |

So the trench’s famous **26-case @ t15** number is roughly **26 (case × single viewport)** pairs — not 26 pages × N viewports.

### 1.2 Multi-size machinery exists but is not the campaign default

`parity_test.py` defines rich presets (`SCREEN_SIZES`: native, 4K, FHD, tablets, phones, wide/tall/square) and `SIZE_PRESETS` (`responsive`, `all`, `desktop`, `mobile`).

`parity_lib.VIEWPORTS` only lists three:

```text
800×600, 1280×800, 1920×1080
```

These are for **optional multi-viewport / swarm** runs. Nightly digests quote the **default-size** path unless someone passes a preset explicitly.

### 1.3 Baselines are CSS-pixel snapshots at those sizes

Sampled `baselines/chrome-120/**/baseline.png` sizes include: 1280×800, 800×600, 800×1200, 1024×768-class cases, **600×500 (bg-solid)**, shelf 1280×120, chrome strip 1280×100, etc.

`baselines/metadata.json` still records **chrome-120**, `dpi: 1`, `viewport_scale: 1.0` — environment truth for campaign pin may live under chrome-148 trees; **metadata is stale** and dangerous if trusted blindly.

### 1.4 Engine / renderer size plumbing

| Layer | Behavior | Risk |
|-------|----------|------|
| `parity-capture` | CLI `--width` / `--height` (default **800**) | OK if harness always passes case size |
| `LayoutBox.viewport` | Defaults **(0, 0)** until `set_viewport` | **vh/vw/% of viewport** wrong if unset |
| Fixed positioning | Comment: “would use viewport” — incomplete | Fixed elements wrong across sizes |
| `Renderer` | Defaults **800×600**; `set_viewport_size` exists | Work order `viewport-sizing` still **pending** (Jan): surface size may not match renderer viewport |
| Scroll | Has `viewport_width/height` | Depends on upstream size truth |

### 1.5 Known measurement lies (already in campaign history)

| Lie | What happened |
|-----|----------------|
| **#8** | settings / bg-solid / pseudo-classes baselines captured at **wrong viewports** vs case table; `comparePixels` **crops to min(w,h)** so mismatches look like “render diffs” |
| Crop policy | `compare_baseline.mjs` L140–165: dimension mismatch → **warn + crop**, still emits a diff % | **Silent false metrics** |
| bg-solid | Case table often **800×600**; tree still had **600×500** PNG sample | Classic #8 residue if not fully purged |

**Hard rule:** A size mismatch is an **instrument failure (score 100 / hard fail)**, never a soft crop.

---

## 2. What “support virtually all resolutions” should mean

Not: full pixel suite at every width from 320→3840 (combinatorial explosion).

**Yes:**

1. **Correctness:** For any size the app can open, layout + paint use the **same** width/height/DPR end-to-end (no silent crop, no 800×600 default bleed).  
2. **Continuous layout laws:** Unit tests that randomize or sample widths prove flex/grid/text don’t assert fixed pixels.  
3. **Tiered pixel matrix:** Small set of **canonical viewports** on a **core case set**, run on a schedule.  
4. **DPR policy:** Explicit `deviceScaleFactor` (1.0 campaign; optional 2.0 lane later) — never accidental retina.

“Virtually all resolutions” = **arbitrary size is valid input** + **we prove critical breakpoints** + **we never lie when sizes disagree**.

---

## 3. Incorrect / fragile things to fix first (before expanding coverage)

### P0 — Instrument integrity

| # | Issue | Fix |
|---|--------|-----|
| P0.1 | Crop-on-mismatch in `comparePixels` | **Fail hard** if Chrome PNG ≠ RustKit PPM dimensions (diffPercent = 100, taxonomy = `instrument/dimension_mismatch`). Optional: generate both full frames for debug, but **do not score crop**. |
| P0.2 | Case size not single source of truth | One JSON registry: `cases/<id>.json` → `{html, width, height, dpr, tags}`. `parity_lib`, `parity_test`, Windows harness, baseline generator **all read it**. |
| P0.3 | Baseline dimension audit CI | Job: for every baseline.png, assert `size == registry[case].(w,h) * dpr` (integer). Fail PR if drift. |
| P0.4 | Stale baseline pin metadata | `metadata.json` must match active pin (CfT 148, dpi, generator commit). |

### P0 — Engine size plumbing

| # | Issue | Fix |
|---|--------|-----|
| P0.5 | Renderer default 800×600 | Complete work order `viewport-sizing`: every render/resize sets viewport from **surface** size. Assert in debug builds. |
| P0.6 | Layout `viewport (0,0)` | Root layout **must** `set_viewport(w,h)` before any vh/vw resolve; unit test fails if vh used with zero viewport. |
| P0.7 | Fixed/abs containing block | Root CB = **viewport**, not “first ancestor with size” mistakes — required for multi-size Absolute/Fixed (#23) to stay correct as sizes change. |

### P1 — Process

| # | Issue | Fix |
|---|--------|-----|
| P1.1 | Multi-viewport code path unused nightly | Document: campaign = registry defaults; `SIZE_PRESETS.responsive` = weekly. |
| P1.2 | Duplicate CASE tables in `parity_lib` vs `parity_test` | Delete one; import registry. |
| P1.3 | Windows dimension-mismatch warning already seen | Same hard-fail + registry on Windows. |
| P1.4 | DPR | Campaign stays **dpr=1**. Add explicit `--dpr 2` lane later; never mix 1× baselines with 2× captures. |

---

## 4. Coverage plan (tiers)

### Tier 0 — Correctness (always on, every PR that touches capture/layout)

- Dimension hard-fail (P0.1)  
- Registry + baseline audit (P0.2–P0.3)  
- Viewport plumbing asserts (P0.5–P0.6)  
- **Cost:** near zero suite time  

### Tier 1 — Campaign (nightly trench, both seats)

- **Current 26-ish cases × 1 registered size each** (keep)  
- After registry: optionally **add 1 second size** only for cases tagged `responsive_sensitive` (e.g. card-grid, article-typography, sticky-scroll) at **375×667** or **390×844** — **not** full mobile suite yet  
- **Cost:** ~+3–5 cases equivalent if only 3 pages dual-size  

### Tier 2 — Responsive matrix (2–3× / week or Friday)

**Core pages** (6–8): article-typography, card-grid, sticky-scroll, settings, flex-positioning, image-gallery, form-elements, about  

**Viewports** (canonical set — CSS pixels, dpr=1):

| Name | Size | Why |
|------|------|-----|
| `phone` | 390×844 | Modern mobile |
| `tablet` | 768×1024 | Portrait tablet |
| `laptop` | 1280×800 | Current websuite default |
| `fhd` | 1920×1080 | Common desktop |
| `short_wide` | 1920×600 | Stress height (sticky/overflow) |
| `narrow_tall` | 360×800 | Small phone / split view |

**Formula:** 8 cases × 6 viewports = **48** pixel compares — Friday-scale, not every night.

### Tier 3 — Property / unit (continuous, fast)

No full page pixels. Instead:

- Layout unit tests: container widths `{320, 375, 768, 1024, 1280, 1440, 1920, 2560}` × fixtures (flex row, grid 1fr, wrap text, abs inset:0)  
- Assert **invariants**: no NaN, no negative sizes, definite height holds, wrap produces ≥1 line when width < max-content  
- Optional: random widths 300–2000 for 50 iterations in debug CI  

This is how you claim “virtually all resolutions” **without** infinite baselines.

### Tier 4 — DPR / retina (later)

- Capture Chrome + RustKit at `deviceScaleFactor: 2` for **2–3** core pages  
- Separate baseline tree `baselines/chrome-148@2x/`  
- Do **not** mix into t15 campaign until Tier 0 is bulletproof  

### Tier 5 — “All resolutions” product bar

App: resize to arbitrary window size must not panic; layout reflows.  
Test: window resize integration test (one HTML, sizes 400→1800 step 200) golden **structure** (box counts / key rects), not full pixels.

---

## 5. Implementation phases (Atlas / Athena)

### Phase R0 — Stop the lying (1–2 days, both seats)

1. Hard-fail dimension mismatch in `compare_baseline.mjs` (+ Python wrapper).  
2. Single **case registry** JSON; both harnesses import it.  
3. CI audit script: baseline PNG size vs registry.  
4. Fix any remaining lie-#8 baselines (bg-solid 600×500 vs 800×600, etc.).  

**Done when:** A deliberate wrong-size capture cannot produce a “green-ish” cropped score.

### Phase R1 — Plumb size end-to-end (1–2 days)

1. Finish `viewport-sizing` work order (renderer ↔ surface).  
2. Layout root always gets viewport; tests for vh/vw.  
3. Fixed containing block = initial viewport.  
4. parity-capture: refuse to run if width/height missing; log size in every artifact JSON.  

**Done when:** Changing capture size changes layout export root width/height 1:1.

### Phase R2 — Expand coverage deliberately (ongoing)

1. Tag cases `responsive_sensitive`.  
2. Nightly: +1 mobile size for those tags only.  
3. Friday: Tier 2 matrix (8×6).  
4. Land Tier 3 unit/property tests in rustkit-layout (can start in parallel with R0).  

### Phase R3 — DPR lane (after R0–R1 stable)

---

## 6. Suggested ownership

| Work | Owner |
|------|--------|
| Hard-fail crop + registry + baseline audit | **Atlas** (macOS harness source of truth) |
| Windows harness same contracts | **Athena** (port registry + fail-hard) |
| Renderer/layout viewport plumbing | **Atlas** shared crates; Athena ports |
| Tier 3 layout property tests | Either seat; good Atlas while sticky epic runs |
| Friday Tier 2 matrix in CI | Atlas adds workflow; Athena enables when CI PR lands |

---

## 7. What not to do

- Do **not** regenerate full 26-case baselines at 15 screen sizes (baseline tree explosion).  
- Do **not** crop mismatches “to keep the run going.”  
- Do **not** treat shelf 1280×120 as a “wrong” full-page size — it’s a **chrome strip** fixture; document as `role: chrome_strip` in registry.  
- Do **not** mix dpr=2 into campaign t15.  
- Do **not** expand multi-viewport until R0 hard-fail is merged (or you multiply lie #8).

---

## 8. Success criteria

| Horizon | Success |
|---------|---------|
| 1 week | No cropped scores; registry + audit green; viewport plumbing asserted |
| 2 weeks | Tier 3 property tests on flex/text/abs; 3 pages dual-size nightly |
| ~1 month | Friday 8×6 matrix in CI; product resize smoke; optional 2× dpr pilot |

---

## 9. Relation to PATH_FORWARD

- **Does not replace** Atlas sticky epic or Athena paint epic.  
- **R0 is a prerequisite** for trustworthy sticky/paint metrics across sizes.  
- Schedule: **R0 + R1 in parallel** with feature work (small PRs); R2 Friday cadence.

— Prometheus
