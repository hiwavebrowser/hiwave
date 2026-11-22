# Code Churn Analysis Report

**Generated:** 2026-11-22 05:44:42

## Overview

- **Repositories Analyzed:** hiwave-macos, hiwave-linux, hiwave-windows
- **Total Files Modified:** 4524
- **Total Commits Analyzed:** 24226
- **Cross-Repo Files:** 3175
- **Line Range Bucket Size:** 50 lines

## Repository Statistics

**Total lines across all repos:** 4,309,763

| Repository | Total Lines | Total Files | Commits | Branch |
|------------|-------------|-------------|---------|--------|
| hiwave-macos | 1,645,421 | 3,630 | 5,837 | HEAD |
| hiwave-linux | 1,382,153 | 3,065 | 505 | HEAD |
| hiwave-windows | 1,282,189 | 2,688 | 465 | HEAD |

### Lines by File Type

- **hiwave-macos:** .rs (642,084), .json (522,962), .js (145,203), .ts (57,642), .md (56,878)
- **hiwave-linux:** .rs (645,189), .json (457,160), .ttf (40,894), .png (39,666), .md (39,481)
- **hiwave-windows:** .rs (635,581), .json (395,380), .ttf (40,894), .png (35,988), .py (35,697)

## Top 10 Highest-Churn Files

| Rank | File | Churn Score | Modifications | Repos |
|------|------|-------------|---------------|-------|
| 1 | `crates/rustkit-engine/src/lib.rs` | 4110 | 1370 | hiwave-linux, hiwave-macos, hiwave-windows |
| 2 | `crates/rustkit-layout/src/lib.rs` | 1344 | 448 | hiwave-linux, hiwave-macos, hiwave-windows |
| 3 | `crates/rustkit-bindings/src/lib.rs` | 1020 | 340 | hiwave-linux, hiwave-macos, hiwave-windows |
| 4 | `crates/rustkit-bindings/src/dom.rs` | 705 | 235 | hiwave-linux, hiwave-macos, hiwave-windows |
| 5 | `crates/hiwave-app/src/main.rs` | 642 | 214 | hiwave-linux, hiwave-macos, hiwave-windows |
| 6 | `crates/rustkit-css/src/lib.rs` | 612 | 204 | hiwave-linux, hiwave-macos, hiwave-windows |
| 7 | `crates/rustkit-layout/src/grid.rs` | 540 | 180 | hiwave-linux, hiwave-macos, hiwave-windows |
| 8 | `crates/rustkit-renderer/src/lib.rs` | 501 | 167 | hiwave-linux, hiwave-macos, hiwave-windows |
| 9 | `crates/rustkit-layout/src/flex.rs` | 474 | 158 | hiwave-linux, hiwave-macos, hiwave-windows |
| 10 | `Cargo.lock` | 465 | 155 | hiwave-linux, hiwave-macos, hiwave-windows |

## Top 10 Highest-Churn Line Ranges

| Rank | File | Line Range | Touches | Repos |
|------|------|------------|---------|-------|
| 1 | `...y-baseline/captures/sticky-scroll.ppm` | 0-50 | 164 | hiwave-macos |
| 2 | `parity-baseline/baseline_report.json` | 50-100 | 150 | hiwave-macos |
| 3 | `trench/wpt/last-run.json` | 0-50 | 149 | hiwave-macos |
| 4 | `...y-baseline/captures/css-selectors.ppm` | 150-200 | 147 | hiwave-macos |
| 5 | `...y-baseline/captures/sticky-scroll.ppm` | 50-100 | 138 | hiwave-macos |
| 6 | `crates/rustkit-engine/src/lib.rs` | 450-500 | 128 | hiwave-linux, hiwave-macos, hiwave-windows |
| 7 | `...y-baseline/captures/sticky-scroll.ppm` | 100-150 | 124 | hiwave-macos |
| 8 | `parity-baseline/parity_test_results.json` | 0-50 | 121 | hiwave-macos |
| 9 | `...y-baseline/captures/css-selectors.ppm` | 250-300 | 118 | hiwave-macos |
| 10 | `...y-baseline/captures/css-selectors.ppm` | 300-350 | 116 | hiwave-macos |

## Cross-Repository Files

Files modified across multiple repositories may indicate:
- Core shared functionality
- Platform-specific adaptations of common code
- Potential candidates for refactoring into shared modules

| File | Modifications | Repos | Lines +/- |
|------|---------------|-------|-----------|
| `crates/rustkit-engine/src/lib.rs` | 1370 | hiwave-linux, hiwave-macos, hiwave-windows | +342336/-169842 |
| `crates/rustkit-layout/src/lib.rs` | 448 | hiwave-linux, hiwave-macos, hiwave-windows | +81165/-8571 |
| `crates/rustkit-bindings/src/lib.rs` | 340 | hiwave-linux, hiwave-macos, hiwave-windows | +23001/-2629 |
| `crates/rustkit-bindings/src/dom.rs` | 235 | hiwave-linux, hiwave-macos, hiwave-windows | +28627/-3472 |
| `crates/hiwave-app/src/main.rs` | 214 | hiwave-linux, hiwave-macos, hiwave-windows | +20286/-3647 |
| `crates/rustkit-css/src/lib.rs` | 204 | hiwave-linux, hiwave-macos, hiwave-windows | +21811/-3146 |
| `crates/rustkit-layout/src/grid.rs` | 180 | hiwave-linux, hiwave-macos, hiwave-windows | +36469/-3644 |
| `crates/rustkit-renderer/src/lib.rs` | 167 | hiwave-linux, hiwave-macos, hiwave-windows | +45423/-9698 |
| `crates/rustkit-layout/src/flex.rs` | 158 | hiwave-linux, hiwave-macos, hiwave-windows | +24993/-3081 |
| `Cargo.lock` | 155 | hiwave-linux, hiwave-macos, hiwave-windows | +30940/-5685 |
| `crates/parity-capture/src/main.rs` | 140 | hiwave-linux, hiwave-macos, hiwave-windows | +13502/-783 |
| `crates/hiwave-app/src/webview_rustkit.rs` | 119 | hiwave-linux, hiwave-macos, hiwave-windows | +8035/-684 |
| `crates/rustkit-js/src/lib.rs` | 110 | hiwave-linux, hiwave-macos, hiwave-windows | +12405/-1175 |
| `crates/rustkit-layout/src/text.rs` | 103 | hiwave-linux, hiwave-macos, hiwave-windows | +16798/-1928 |
| `crates/rustkit-engine/src/layout_ctx.rs` | 96 | hiwave-linux, hiwave-macos, hiwave-windows | +5239/-2068 |

## Divergent Modification Patterns

Files with significantly different modification patterns across repos:

### `tools/parity_oracle/eval_order_cases.json`

**Divergence Score:** 0.99

| Repository | Modifications | Active Line Ranges |
|------------|---------------|-------------------|
| hiwave-windows | 1 | 1 |
| hiwave-macos | 4 | 121 |
| hiwave-linux | 1 | 1 |

### `baselines/chrome-120/builtins/settings/layout-rects.json`

**Divergence Score:** 0.99

| Repository | Modifications | Active Line Ranges |
|------------|---------------|-------------------|
| hiwave-windows | 1 | 1 |
| hiwave-macos | 4 | 91 |
| hiwave-linux | 1 | 1 |

### `baselines/chrome-148/builtins/settings/layout-rects.json`

**Divergence Score:** 0.99

| Repository | Modifications | Active Line Ranges |
|------------|---------------|-------------------|
| hiwave-windows | 4 | 91 |
| hiwave-macos | 3 | 91 |
| hiwave-linux | 1 | 1 |

### `baselines/chrome-148/builtins/about/layout-rects.json`

**Divergence Score:** 0.99

| Repository | Modifications | Active Line Ranges |
|------------|---------------|-------------------|
| hiwave-windows | 3 | 81 |
| hiwave-macos | 2 | 1 |
| hiwave-linux | 1 | 1 |

### `baselines/chrome-120/micro/pseudo-classes/computed-styles.json`

**Divergence Score:** 0.99

| Repository | Modifications | Active Line Ranges |
|------------|---------------|-------------------|
| hiwave-windows | 1 | 1 |
| hiwave-macos | 3 | 75 |
| hiwave-linux | 1 | 1 |

### `baselines/chrome-148/micro/pseudo-classes/computed-styles.json`

**Divergence Score:** 0.99

| Repository | Modifications | Active Line Ranges |
|------------|---------------|-------------------|
| hiwave-windows | 2 | 75 |
| hiwave-macos | 3 | 1 |
| hiwave-linux | 1 | 1 |

### `baselines/chrome-148/micro/form-controls/computed-styles.json`

**Divergence Score:** 0.99

| Repository | Modifications | Active Line Ranges |
|------------|---------------|-------------------|
| hiwave-windows | 2 | 74 |
| hiwave-macos | 2 | 1 |
| hiwave-linux | 1 | 1 |

### `baselines/chrome-148/micro/rounded-corners/computed-styles.json`

**Divergence Score:** 0.98

| Repository | Modifications | Active Line Ranges |
|------------|---------------|-------------------|
| hiwave-windows | 2 | 55 |
| hiwave-macos | 2 | 1 |
| hiwave-linux | 1 | 1 |

### `baselines/chrome-148/micro/images-intrinsic/computed-styles.json`

**Divergence Score:** 0.98

| Repository | Modifications | Active Line Ranges |
|------------|---------------|-------------------|
| hiwave-windows | 2 | 51 |
| hiwave-macos | 2 | 1 |
| hiwave-linux | 1 | 1 |

### `baselines/chrome-148/micro/gradients/computed-styles.json`

**Divergence Score:** 0.98

| Repository | Modifications | Active Line Ranges |
|------------|---------------|-------------------|
| hiwave-windows | 2 | 48 |
| hiwave-macos | 2 | 1 |
| hiwave-linux | 1 | 1 |

## Recommendations

Based on the churn analysis, consider reviewing the following areas:

1. **High Churn Files - Architectural Review**
   - These files have been modified frequently across multiple repos. Consider reviewing their architecture for potential simplification or abstraction.
   - Files: `crates/rustkit-engine/src/lib.rs`, `crates/rustkit-layout/src/lib.rs`, `crates/rustkit-bindings/src/lib.rs`, `crates/rustkit-bindings/src/dom.rs`, `crates/hiwave-app/src/main.rs`

2. **Line Range Hotspots**
   - Specific line ranges in these files are being modified repeatedly. This may indicate ongoing bug fixes or feature adjustments in localized areas.
   - Files: `parity-baseline/captures/css-selectors.ppm`, `parity-baseline/baseline_report.json`, `parity-baseline/parity_test_results.json`, `parity-baseline/captures/sticky-scroll.ppm`, `trench/wpt/last-run.json`

3. **Cross-Platform Synchronization**
   - These files are modified across all repositories. Consider creating a shared module or ensuring changes are consistently applied.
   - Files: `crates/rustkit-engine/src/lib.rs`, `crates/rustkit-layout/src/lib.rs`, `crates/rustkit-bindings/src/lib.rs`, `crates/rustkit-bindings/src/dom.rs`, `crates/hiwave-app/src/main.rs`

4. **Divergent Development Patterns**
   - These files show different modification patterns across repos. This may indicate platform-specific implementations that could benefit from a unified approach.
   - Files: `tools/parity_oracle/eval_order_cases.json`, `baselines/chrome-120/builtins/settings/layout-rects.json`, `baselines/chrome-148/builtins/settings/layout-rects.json`, `baselines/chrome-148/builtins/about/layout-rects.json`, `baselines/chrome-120/micro/pseudo-classes/computed-styles.json`

---

*This report was automatically generated by the Code Churn Analysis Tool.*