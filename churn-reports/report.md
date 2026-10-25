# Code Churn Analysis Report

**Generated:** 2026-10-25 03:45:35

## Overview

- **Repositories Analyzed:** hiwave-macos, hiwave-linux, hiwave-windows
- **Total Files Modified:** 3243
- **Total Commits Analyzed:** 10188
- **Cross-Repo Files:** 770
- **Line Range Bucket Size:** 50 lines

## Repository Statistics

**Total lines across all repos:** 2,163,726

| Repository | Total Lines | Total Files | Commits | Branch |
|------------|-------------|-------------|---------|--------|
| hiwave-macos | 1,274,370 | 2,340 | 2,755 | HEAD |
| hiwave-linux | 328,638 | 607 | 6 | HEAD |
| hiwave-windows | 560,718 | 797 | 94 | HEAD |

### Lines by File Type

- **hiwave-macos:** .json (454,952), .rs (406,262), .js (138,180), .ts (57,642), .md (45,842)
- **hiwave-linux:** .json (137,135), .rs (66,969), .ttf (40,850), .png (20,321), .md (12,907)
- **hiwave-windows:** .json (327,249), .rs (71,630), .ttf (40,850), .png (31,482), .html (18,759)

## Top 10 Highest-Churn Files

| Rank | File | Churn Score | Modifications | Repos |
|------|------|-------------|---------------|-------|
| 1 | `crates/rustkit-engine/src/lib.rs` | 1746 | 582 | hiwave-linux, hiwave-macos, hiwave-windows |
| 2 | `crates/rustkit-layout/src/lib.rs` | 690 | 230 | hiwave-linux, hiwave-macos, hiwave-windows |
| 3 | `crates/rustkit-bindings/src/lib.rs` | 345 | 115 | hiwave-linux, hiwave-macos, hiwave-windows |
| 4 | `crates/rustkit-layout/src/grid.rs` | 345 | 115 | hiwave-linux, hiwave-macos, hiwave-windows |
| 5 | `Cargo.lock` | 264 | 88 | hiwave-linux, hiwave-macos, hiwave-windows |
| 6 | `crates/rustkit-renderer/src/lib.rs` | 258 | 86 | hiwave-linux, hiwave-macos, hiwave-windows |
| 7 | `crates/rustkit-layout/src/flex.rs` | 258 | 86 | hiwave-linux, hiwave-macos, hiwave-windows |
| 8 | `crates/rustkit-css/src/lib.rs` | 222 | 74 | hiwave-linux, hiwave-macos, hiwave-windows |
| 9 | `crates/hiwave-app/src/main.rs` | 216 | 72 | hiwave-linux, hiwave-macos, hiwave-windows |
| 10 | `crates/rustkit-js/src/lib.rs` | 141 | 47 | hiwave-linux, hiwave-macos, hiwave-windows |

## Top 10 Highest-Churn Line Ranges

| Rank | File | Line Range | Touches | Repos |
|------|------|------------|---------|-------|
| 1 | `...y-baseline/captures/sticky-scroll.ppm` | 0-50 | 164 | hiwave-macos |
| 2 | `parity-baseline/baseline_report.json` | 50-100 | 150 | hiwave-macos |
| 3 | `trench/wpt/last-run.json` | 0-50 | 149 | hiwave-macos |
| 4 | `...y-baseline/captures/css-selectors.ppm` | 150-200 | 147 | hiwave-macos |
| 5 | `...y-baseline/captures/sticky-scroll.ppm` | 50-100 | 138 | hiwave-macos |
| 6 | `...y-baseline/captures/sticky-scroll.ppm` | 100-150 | 124 | hiwave-macos |
| 7 | `parity-baseline/parity_test_results.json` | 0-50 | 121 | hiwave-macos |
| 8 | `...y-baseline/captures/css-selectors.ppm` | 250-300 | 118 | hiwave-macos |
| 9 | `...y-baseline/captures/css-selectors.ppm` | 300-350 | 116 | hiwave-macos |
| 10 | `parity-baseline/baseline_report.json` | 0-50 | 115 | hiwave-macos |

## Cross-Repository Files

Files modified across multiple repositories may indicate:
- Core shared functionality
- Platform-specific adaptations of common code
- Potential candidates for refactoring into shared modules

| File | Modifications | Repos | Lines +/- |
|------|---------------|-------|-----------|
| `crates/rustkit-engine/src/lib.rs` | 582 | hiwave-linux, hiwave-macos, hiwave-windows | +53046/-7568 |
| `crates/rustkit-layout/src/lib.rs` | 230 | hiwave-linux, hiwave-macos, hiwave-windows | +25362/-2205 |
| `crates/rustkit-bindings/src/lib.rs` | 115 | hiwave-linux, hiwave-macos, hiwave-windows | +6954/-366 |
| `crates/rustkit-layout/src/grid.rs` | 115 | hiwave-linux, hiwave-macos, hiwave-windows | +12911/-1084 |
| `Cargo.lock` | 88 | hiwave-linux, hiwave-macos, hiwave-windows | +27956/-3341 |
| `crates/rustkit-renderer/src/lib.rs` | 86 | hiwave-linux, hiwave-macos, hiwave-windows | +14983/-1938 |
| `crates/rustkit-layout/src/flex.rs` | 86 | hiwave-linux, hiwave-macos, hiwave-windows | +9105/-723 |
| `crates/rustkit-css/src/lib.rs` | 74 | hiwave-linux, hiwave-macos, hiwave-windows | +7438/-336 |
| `crates/hiwave-app/src/main.rs` | 72 | hiwave-linux, hiwave-macos, hiwave-windows | +13943/-1180 |
| `crates/rustkit-js/src/lib.rs` | 47 | hiwave-linux, hiwave-macos, hiwave-windows | +3796/-538 |
| `Cargo.toml` | 43 | hiwave-linux, hiwave-macos, hiwave-windows | +453/-65 |
| `crates/rustkit-layout/src/text.rs` | 42 | hiwave-linux, hiwave-macos, hiwave-windows | +6875/-381 |
| `crates/hiwave-app/src/webview_rustkit.rs` | 56 | hiwave-macos, hiwave-windows | +2503/-398 |
| `crates/rustkit-viewhost/src/lib.rs` | 30 | hiwave-linux, hiwave-macos, hiwave-windows | +4903/-233 |
| `crates/rustkit-text/src/macos.rs` | 29 | hiwave-linux, hiwave-macos, hiwave-windows | +2921/-326 |

## Divergent Modification Patterns

Files with significantly different modification patterns across repos:

### `crates/rustkit-engine/src/lib.rs`

**Divergence Score:** 1.00

| Repository | Modifications | Active Line Ranges |
|------------|---------------|-------------------|
| hiwave-windows | 19 | 26 |
| hiwave-macos | 562 | 539 |
| hiwave-linux | 1 | 1 |

### `crates/rustkit-layout/src/lib.rs`

**Divergence Score:** 1.00

| Repository | Modifications | Active Line Ranges |
|------------|---------------|-------------------|
| hiwave-windows | 11 | 18 |
| hiwave-macos | 218 | 223 |
| hiwave-linux | 1 | 1 |

### `Cargo.lock`

**Divergence Score:** 0.99

| Repository | Modifications | Active Line Ranges |
|------------|---------------|-------------------|
| hiwave-windows | 43 | 148 |
| hiwave-macos | 44 | 158 |
| hiwave-linux | 1 | 1 |

### `crates/rustkit-renderer/src/lib.rs`

**Divergence Score:** 0.99

| Repository | Modifications | Active Line Ranges |
|------------|---------------|-------------------|
| hiwave-windows | 2 | 6 |
| hiwave-macos | 83 | 138 |
| hiwave-linux | 1 | 1 |

### `crates/rustkit-layout/src/grid.rs`

**Divergence Score:** 0.99

| Repository | Modifications | Active Line Ranges |
|------------|---------------|-------------------|
| hiwave-windows | 1 | 1 |
| hiwave-macos | 113 | 118 |
| hiwave-linux | 1 | 1 |

### `crates/rustkit-bindings/src/lib.rs`

**Divergence Score:** 0.99

| Repository | Modifications | Active Line Ranges |
|------------|---------------|-------------------|
| hiwave-windows | 8 | 13 |
| hiwave-macos | 106 | 51 |
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
| hiwave-windows | 1 | 1 |
| hiwave-macos | 3 | 91 |

### `crates/rustkit-layout/src/flex.rs`

**Divergence Score:** 0.99

| Repository | Modifications | Active Line Ranges |
|------------|---------------|-------------------|
| hiwave-windows | 1 | 1 |
| hiwave-macos | 84 | 60 |
| hiwave-linux | 1 | 1 |

### `baselines/chrome-120/micro/pseudo-classes/computed-styles.json`

**Divergence Score:** 0.99

| Repository | Modifications | Active Line Ranges |
|------------|---------------|-------------------|
| hiwave-windows | 1 | 1 |
| hiwave-macos | 3 | 75 |
| hiwave-linux | 1 | 1 |

## Recommendations

Based on the churn analysis, consider reviewing the following areas:

1. **High Churn Files - Architectural Review**
   - These files have been modified frequently across multiple repos. Consider reviewing their architecture for potential simplification or abstraction.
   - Files: `crates/rustkit-engine/src/lib.rs`, `crates/rustkit-layout/src/lib.rs`, `crates/rustkit-bindings/src/lib.rs`, `crates/rustkit-layout/src/grid.rs`, `Cargo.lock`

2. **Line Range Hotspots**
   - Specific line ranges in these files are being modified repeatedly. This may indicate ongoing bug fixes or feature adjustments in localized areas.
   - Files: `parity-baseline/captures/css-selectors.ppm`, `parity-baseline/baseline_report.json`, `parity-baseline/captures/sticky-scroll.ppm`, `parity-baseline/parity_test_results.json`, `trench/wpt/last-run.json`

3. **Cross-Platform Synchronization**
   - These files are modified across all repositories. Consider creating a shared module or ensuring changes are consistently applied.
   - Files: `crates/rustkit-engine/src/lib.rs`, `crates/rustkit-layout/src/lib.rs`, `crates/rustkit-bindings/src/lib.rs`, `crates/rustkit-layout/src/grid.rs`, `Cargo.lock`

4. **Divergent Development Patterns**
   - These files show different modification patterns across repos. This may indicate platform-specific implementations that could benefit from a unified approach.
   - Files: `crates/rustkit-engine/src/lib.rs`, `crates/rustkit-layout/src/lib.rs`, `Cargo.lock`, `crates/rustkit-renderer/src/lib.rs`, `crates/rustkit-layout/src/grid.rs`

5. **Many Single-Touch Files**
   - 1687 files (52%) were only modified once. This is healthy and indicates stable code.

---

*This report was automatically generated by the Code Churn Analysis Tool.*