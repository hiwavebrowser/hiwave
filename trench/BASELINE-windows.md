# Trench Baseline — Windows
Captured 2026-07-07 (Phase 0, night 1). Seat: Athena.

## Pin
- **Chrome for Testing 148.0.7778.216 (win64)** — downloaded via `@puppeteer/browsers`,
  launched through `PARITY_CHROME_PATH` (system Chrome had already drifted to 149.0.7827.201;
  CfT cannot drift). GL backend: `--use-angle=swiftshader` (Chrome ≥148 removed
  `--use-gl=swiftshader`; old flag breaks screenshots entirely).
- Baseline tree: `baselines/chrome-148/` in hiwave-windows, 21/21 cases captured,
  structurally identical to the retired chrome-120 tree. `metadata.json` records the binary.
- Baseline decay found: 2 case sources deleted since chrome-120 (`builtins/chrome_rustkit`,
  `micro/bg-pure`) — cases retired, not silently skipped.

## Headline numbers (true pixel diff, RustKit PPM vs pinned-Chrome PNG)
- **Pass rate: 1/12 (8.3%) @ threshold 15**
- **Mean diff: 65.5%  →  ~34.5% visual parity**
- (macOS same night: 80.2% visual parity, 46.2% pass rate — Windows is the far-behind seat.)

## Per-case ledger (worst first)
| case | type | diff % |
|---|---|---|
| new_tab | builtin | 99.60 |
| shelf | builtin | 99.51 |
| image-gallery | websuite | 99.45 |
| settings | builtin | 99.10 |
| gradient-backgrounds | websuite | 98.91 |
| about | builtin | 98.36 |
| card-grid | websuite | 64.74 |
| sticky-scroll | websuite | 43.55 |
| css-selectors | websuite | 34.02 |
| flex-positioning | websuite | 21.46 |
| article-typography | websuite | 16.79 |
| form-elements | websuite | **10.18 ← only pass** |

## Bucket reading
- **Builtins are a failure CLASS (4/4 at ~99%)** — the app's own UI pages barely render.
  Same class as macOS `settings` (100%), but here it is every builtin.
- **Paint bucket dead: gradients + images ~99%** — gradient fills and image decode/draw
  produce near-nothing. PPM autopsy: pages are ~90% white + gray boxes; text pixels exist.
- **Static-web layout/text is the healthy tail** (10–44%) — text renders, simple flex works.
- **January's "59% text" does NOT describe today's Windows profile.** Text is the *best*
  bucket now; paint and builtins are the worst. Re-verified, not inherited — as the plan demanded.

## Root-cause lead (recorded, not chased tonight — harness first)
RustKit's exported layout tree reports **width=0.0 on every box** (root of `about`:
w=0, h=4640 on an 800×600 viewport — the infinite single column Pete reported in
January). Paint draws viewport-driven anyway, which is why pixels exist while the
layout tree is degenerate. Likely upstream of both the builtin collapse and several
websuite diffs. First candidate for `athena/trench-<metric>` night sessions.

## Caveats
- One compare emitted a dimension-mismatch warning (RustKit 1024×768 case) — that
  case's diff % may be inflated; verify when the harness gets dimension guards.
- The heuristic layout estimator (`estimated_diff_pct`) saturates at 100% while the
  zero-width bug lives; the pixel path above is the campaign metric, not the heuristic.

## Proposed Phase-2 metric (Windows seat)
**Unified pass rate @ threshold 15 vs pinned Chrome 148** — same formula as macOS for
convergence, page-by-page wins, not gameable by averaging. Nightly focus order from the
data: (1) zero-width layout tree, (2) builtin render collapse, (3) gradient/image paint.

## Harness fixes shipped tonight (portable-fix flags for macOS)
- `--use-gl=swiftshader` → `--use-angle=swiftshader` (Chrome ≥148 hard-breaks capture otherwise). **PORTABLE**
- `PARITY_CHROME_PATH` env passthrough in `deterministic.mjs` (pinned CfT binary, refuses missing path). **PORTABLE**
- `capture_all_baselines.mjs` — regenerates a full baseline tree from a reference tree's
  structure + viewports; reports missing sources instead of skipping. **PORTABLE**
- 25 bare `open()` calls in parity scripts → `encoding="utf-8"` (cp1252 crash on Windows; harmless on POSIX). **PORTABLE (hygiene)**
- `parity_archive.py` latest-symlink → `latest.txt` fallback (WinError 1314 without elevation). **PORTABLE (hygiene)**
- `parity_lib.py` baseline dir → `chrome-148` (env-overridable via `PARITY_BASELINE_SET`).
