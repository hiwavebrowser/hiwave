# Claude Session Notes - Cross-Platform Metrics Visualization

**Last Updated:** 2026-01-10

## What Was Accomplished

### 1. Cross-Platform Metrics Visualization System (hiwave umbrella repo)

Created automated badge and chart generation for tracking visual parity across platforms:

**Scripts Created:**
- `scripts/collect_metrics.py` - Aggregates REAL visual parity (pixel match %) from submodules
- `scripts/generate_badges.py` - Generates 18 shields.io-style SVG badges
- `scripts/generate_charts.py` - Generates trend charts using pygal

**Badges Generated:**
- `parity-{platform}.svg` - Visual parity percentage
- `tests-{platform}.svg` - Tests passing (e.g., 7/23)
- `build-{platform}.svg` - Build status
- `perf-{platform}.svg` - Performance grade
- `tier-a-{platform}.svg` - Tier A pass rate
- Plus overall badges

**CI Workflow:**
- `.github/workflows/metrics.yml` - Runs daily, on dispatch, or manual trigger

### 2. Parity CI Overhaul (hiwave-macos)

Updated `.github/workflows/parity.yml` with:
- Sharded swarm testing (4 parallel runners)
- PR gate, commit gate, and nightly runs
- Metrics dispatch to umbrella repo on success

**New Scripts Added:**
- `scripts/parity_swarm.py` - Parallel test execution
- `scripts/parity_aggregate.py` - Merges shard results
- `scripts/parity_lib.py` - Shared utilities

### 3. Current Metrics (Real Data)

| Metric | macOS | Windows | Linux |
|--------|-------|---------|-------|
| Visual Parity | 75.18% | no data | no data |
| - Builtins | 92.27% | - | - |
| - Websuite | 70.44% | - | - |
| Tests Passing | 7/23 | - | - |

## Key Files

**Umbrella Repo (hiwave):**
- `metrics/unified.json` - Aggregated metrics data
- `badges/*.svg` - Generated badges
- `charts/*.svg` - Generated trend charts
- `README.md` - Updated with Platform Status table

**macOS Repo (hiwave-macos):**
- `parity-baseline/parity_test_results.json` - Source of real pixel diff data
- `.github/workflows/parity.yml` - CI with metrics dispatch

## Setup Required for Full Functionality

1. **Create `UMBRELLA_PAT` secret** in hiwave-macos repo:
   - Fine-grained PAT with Contents + Actions permissions on hiwave repo
   - Add as repository secret

2. **For Windows/Linux:**
   - Generate `parity_test_results.json` in same format as macOS
   - Add metrics dispatch to their CI workflows

## Commands for Testing Locally

```bash
cd /Users/petecopeland/Repos/hiwave

# Update submodules first
git submodule update --remote

# Run full pipeline
python3 scripts/collect_metrics.py
python3 scripts/generate_badges.py
python3 scripts/generate_charts.py

# View results
open badges/parity-macos.svg
open charts/parity-trend.svg
```

## Notes

- Metrics use ACTUAL pixel diff from `parity_test_results.json` (not baseline estimates)
- Visual parity = 100% - diffPercent (honest representation)
- History builds up over time as CI runs - started fresh 2026-01-10
- Charts will show trends as more data points accumulate
