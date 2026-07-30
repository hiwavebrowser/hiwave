#!/usr/bin/env python3
"""
collect_metrics.py - Aggregate metrics from platform submodules

Collects ACTUAL visual parity (pixel match %) and test metrics from each
platform submodule and aggregates them into metrics/unified.json.

Priority: parity_test_results.json (real pixel data) > baseline_report.json

Usage:
    python3 scripts/collect_metrics.py [--test] [--verbose]
"""

import csv
import io
import json
import sys
import urllib.request
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple
import subprocess

REPO_ROOT = Path(__file__).parent.parent
METRICS_DIR = REPO_ROOT / "metrics"
UNIFIED_FILE = METRICS_DIR / "unified.json"

# Submodule paths
SUBMODULES = {
    "macos": REPO_ROOT / "hiwave-macos",
    "windows": REPO_ROOT / "hiwave-windows",
    "linux": REPO_ROOT / "hiwave-linux",
}

# Metric source files in priority order (first found wins)
PARITY_TEST_SOURCES = [
    "parity-baseline/parity_test_results.json",
    "parity_test_results.json",
]

BASELINE_SOURCES = [
    "parity-baseline/baseline_report.json",
    "baseline_report.json",
]

# Swarm results (from parity_swarm.py)
SWARM_SOURCES = [
    "parity-results/swarm_report.json",
]

# Unified results from CI aggregation
UNIFIED_PARITY_FILE = METRICS_DIR / "parity_results.json"

# ---------------------------------------------------------------------------
# Seat metrics feeds (P1 adapter)
#
# Windows and Linux publish build + cargo-test results to an append-only
# `metrics-history` branch in their own repos. Those numbers exist ONLY there:
# a master checkout of the submodule has no metrics.json and no metrics/ dir,
# which is why this collector used to print "No metrics found" for platforms
# with green CI and hundreds of passing tests — it was reading a source that
# is empty by construction (wrong source path + parity-only early return).
#
# The CI workflow drops each feed into .cache/metrics/<platform>/ before this
# script runs; HTTPS raw is the fallback for local runs. A fetch failure
# leaves the platform NOT-MEASURED — numbers fail closed, never invented.
#
# macOS is deliberately NOT wired here: its metrics-history schema is
# parity-diff oriented and carries no build_ok. Its build badge staying
# "unknown" is the honest state until a macOS seat publishes the Win/Linux
# schema.
SEAT_FEEDS = {
    "windows": "https://raw.githubusercontent.com/hiwavebrowser/hiwave-windows/metrics-history",
    "linux": "https://raw.githubusercontent.com/hiwavebrowser/hiwave-linux/metrics-history",
}
SEAT_CACHE_DIR = REPO_ROOT / ".cache" / "metrics"

# A seat measurement older than this still publishes (it is real), but gets
# flagged so a silently dead collector cannot keep wearing fresh-looking
# numbers. Distinct from the badge-level 7-day STALE render threshold: this
# one is provenance metadata in unified.json, that one is presentation.
SEAT_STALE_AFTER_DAYS = 14

HISTORY_CSV_COLUMNS = [
    "timestamp", "commit", "branch", "build_ok",
    "passed", "failed", "ignored", "warnings",
]


def parse_history_csv(text: str) -> Optional[Dict[str, str]]:
    """Last master data row of a seat's metrics/history.csv, or None.

    Row selection is pinned: skip the header, take the LAST row whose branch
    is exactly "master" (case-sensitive, as written by the seats). PR-branch
    rows never drive public numbers. No master row -> None, and the caller
    publishes NOT-MEASURED rather than borrowing a branch row.
    """
    if not text:
        return None
    rows = list(csv.reader(io.StringIO(text)))
    if not rows:
        return None
    header = [c.strip() for c in rows[0]]
    if header[: len(HISTORY_CSV_COLUMNS)] != HISTORY_CSV_COLUMNS:
        print(f"  Warning: unexpected history.csv header: {header}")
        return None
    last_master = None
    for row in rows[1:]:
        if len(row) < len(HISTORY_CSV_COLUMNS):
            continue
        if row[2].strip() == "master":
            last_master = row
    if last_master is None:
        return None
    return dict(zip(HISTORY_CSV_COLUMNS, (c.strip() for c in last_master)))


def map_seat_metrics_to_unified(
    platform: str,
    row: Dict[str, str],
    seat_json: Optional[Dict] = None,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Map a seat CSV row to the unified platform object the badges consume.

    Two rules here are load-bearing and pinned:

    - tests_total is passed + failed, RECOMPUTED. The seat JSON's own "total"
      currently equals passed alone, and ignored tests do not belong in the
      denominator. A number we can recompute is never trusted pre-summed.
    - There is NO parity key. Windows/Linux parity has never been measured;
      the harness's 100.0-on-empty-capture default is exactly the lie this
      whole stack exists to stop. The parity badge stays "no data".

    git_commit is the commit the measurement was TAKEN AT (from the CSV row),
    not whatever the submodule pointer happens to be today — restamping an old
    measurement onto a current SHA is the fourth defect, and it does not come
    back through this path.
    """
    passed = int(row["passed"])
    failed = int(row["failed"])
    metrics: Dict[str, Any] = {
        "build": {"ok": row["build_ok"] == "True", "warnings": int(row["warnings"])},
        "tests_passed": passed,
        "tests_failed": failed,
        "tests_ignored": int(row["ignored"]),
        "tests_total": passed + failed,
        "tests_source": "cargo",
        "git_commit": row["commit"][:7],
        "metrics_commit": row["commit"],
        "measured_at": row["timestamp"],
        "metrics_source": "metrics-history/history.csv",
    }
    if seat_json and isinstance(seat_json.get("not_collected"), dict):
        metrics["not_collected"] = seat_json["not_collected"]

    now = now or datetime.now(timezone.utc)
    try:
        measured = datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00"))
        if measured.tzinfo is None:
            measured = measured.replace(tzinfo=timezone.utc)
        age_days = (now - measured).total_seconds() / 86400.0
        if age_days > SEAT_STALE_AFTER_DAYS:
            metrics["metrics_stale"] = True
    except ValueError:
        pass  # unparseable timestamp: publish without the flag, badge layer guards

    return metrics


def _read_url(url: str, timeout: int = 15) -> str:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return resp.read().decode("utf-8")


def fetch_seat_metrics(
    platform: str,
    cache_dir: Optional[Path] = None,
    read_url=_read_url,
) -> Tuple[Optional[Dict[str, str]], Optional[Dict]]:
    """(last master CSV row, optional seat metrics.json) for a platform feed.

    Source ranking is pinned: the CI-fetched cache file first, HTTPS raw as
    fallback. Any failure returns (None, None) — fail closed. Numbers typed
    into exchange messages, WORK_QUEUE pins, or design docs are never a
    source; if the CSV cannot be read, the honest answer is NOT-MEASURED.
    """
    if platform not in SEAT_FEEDS:
        return None, None
    cache_dir = cache_dir if cache_dir is not None else SEAT_CACHE_DIR

    csv_text = None
    cache_csv = cache_dir / platform / "history.csv"
    if cache_csv.exists():
        csv_text = cache_csv.read_text()
    else:
        try:
            csv_text = read_url(f"{SEAT_FEEDS[platform]}/metrics/history.csv")
        except Exception as e:
            print(f"  {platform}: seat feed unreachable ({e.__class__.__name__}) — "
                  f"leaving NOT-MEASURED (numbers fail closed)")
            return None, None

    row = parse_history_csv(csv_text)
    if row is None:
        print(f"  {platform}: no master row in history.csv — leaving NOT-MEASURED")
        return None, None

    seat_json = None
    cache_json = cache_dir / platform / "metrics.json"
    if cache_json.exists():
        try:
            seat_json = json.loads(cache_json.read_text())
        except Exception:
            seat_json = None
    else:
        try:
            seat_json = json.loads(read_url(f"{SEAT_FEEDS[platform]}/metrics.json"))
        except Exception:
            seat_json = None  # optional enrichment only; the CSV row stands alone

    return row, seat_json


def get_git_commit(submodule_path: Path) -> Optional[str]:
    """Get the current git commit hash for a submodule."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=submodule_path,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()[:7]
    except Exception:
        pass
    return None


def load_json_file(filepath: Path) -> Optional[Dict]:
    """Load a JSON file, returning None if it doesn't exist or fails."""
    if not filepath.exists():
        return None
    try:
        return json.loads(filepath.read_text())
    except Exception as e:
        print(f"  Warning: Could not parse {filepath}: {e}")
        return None


def find_file(submodule_path: Path, sources: List[str]) -> tuple[Optional[Dict], Optional[str]]:
    """Find and load the first available file from sources list."""
    for source in sources:
        filepath = submodule_path / source
        data = load_json_file(filepath)
        if data:
            return data, source
    return None, None


def load_unified_parity_results() -> Optional[Dict[str, Any]]:
    """Load results from unified parity workflow (CI aggregation)."""
    if not UNIFIED_PARITY_FILE.exists():
        return None
    try:
        data = json.loads(UNIFIED_PARITY_FILE.read_text())
        return data
    except Exception as e:
        print(f"  Warning: Could not parse unified parity results: {e}")
        return None


def extract_swarm_metrics(swarm_data: Dict, verbose: bool = False) -> Dict[str, Any]:
    """
    Extract visual parity from swarm_report.json (from parity_swarm.py).

    This is the preferred source as it has median values across iterations.
    """
    results = swarm_data.get("results", [])
    summary = swarm_data.get("summary", {})

    if not results:
        return {}

    # Calculate metrics from results
    test_results = []
    total_parity = 0
    builtins_parity = 0
    builtins_count = 0
    websuite_parity = 0
    websuite_count = 0

    for r in results:
        diff_pct = r.get("diff_pct_median", 100)
        parity = 100 - diff_pct
        passed = r.get("passed", False)
        case_id = r.get("case_id", "unknown")

        # Determine type from case_id
        case_type = "websuite"
        if case_id in ["new_tab", "about", "settings", "chrome_rustkit", "shelf"]:
            case_type = "builtins"

        test_result = {
            "case_id": case_id,
            "type": case_type,
            "parity": round(parity, 2),
            "diff_pct": round(diff_pct, 2),
            "passed": passed,
            "stable": r.get("stable", False),
        }
        test_results.append(test_result)

        total_parity += parity
        if case_type == "builtins":
            builtins_parity += parity
            builtins_count += 1
        else:
            websuite_parity += parity
            websuite_count += 1

        if verbose:
            status = "PASS" if passed else "FAIL"
            print(f"    {case_id:30s} {parity:6.2f}% [{status}]")

    # Calculate averages
    avg_parity = total_parity / len(results) if results else 0
    avg_builtins = builtins_parity / builtins_count if builtins_count else 0
    avg_websuite = websuite_parity / websuite_count if websuite_count else 0

    return {
        "visual_parity": round(avg_parity, 2),
        "builtins_parity": round(avg_builtins, 2),
        "websuite_parity": round(avg_websuite, 2),
        "tests_passed": summary.get("passed", sum(1 for t in test_results if t["passed"])),
        "tests_failed": summary.get("failed", sum(1 for t in test_results if not t["passed"])),
        "tests_total": len(results),
        "tests_stable": summary.get("stable", sum(1 for t in test_results if t.get("stable", False))),
        "pass_rate": round(summary.get("pass_rate", 0), 1),
        "test_results": test_results,
    }


def extract_visual_parity(parity_test_data: Dict, verbose: bool = False) -> Dict[str, Any]:
    """
    Extract ACTUAL visual parity from parity_test_results.json.

    Visual parity = 100% - pixel diff%
    This is the TRUE measure of how closely RustKit matches Chrome.
    """
    results = parity_test_data.get("results", [])

    if not results:
        return {}

    # Calculate per-test parity
    test_results = []
    total_parity = 0
    builtins_parity = 0
    builtins_count = 0
    websuite_parity = 0
    websuite_count = 0

    for r in results:
        pixel = r.get("pixel")
        if pixel is None:
            print(f"  Warning: Missing pixel data for {r.get('case_id', 'unknown')} - using fallback diff")
            pixel = {}
        diff_pct = pixel.get("diffPercent")
        if diff_pct is None:
            diff_pct = r.get("diff_pct")
        if diff_pct is None:
            print(f"  Warning: Missing diff percent for {r.get('case_id', 'unknown')} - defaulting to 100")
            diff_pct = 100
        parity = 100 - diff_pct
        threshold = r.get("threshold", 15)
        passed = diff_pct <= threshold

        test_result = {
            "case_id": r.get("case_id"),
            "type": r.get("type", "unknown"),
            "parity": round(parity, 2),
            "diff_pct": round(diff_pct, 2),
            "threshold": threshold,
            "passed": passed,
        }
        test_results.append(test_result)

        total_parity += parity
        if r.get("type") == "builtins":
            builtins_parity += parity
            builtins_count += 1
        else:
            websuite_parity += parity
            websuite_count += 1

        if verbose:
            status = "PASS" if passed else "FAIL"
            print(f"    {r.get('case_id'):30s} {parity:6.2f}% [{status}]")

    # Calculate averages
    avg_parity = total_parity / len(results) if results else 0
    avg_builtins = builtins_parity / builtins_count if builtins_count else 0
    avg_websuite = websuite_parity / websuite_count if websuite_count else 0

    passed_count = parity_test_data.get("passed", sum(1 for t in test_results if t["passed"]))
    failed_count = parity_test_data.get("failed", sum(1 for t in test_results if not t["passed"]))

    return {
        "visual_parity": round(avg_parity, 2),
        "builtins_parity": round(avg_builtins, 2),
        "websuite_parity": round(avg_websuite, 2),
        "tests_passed": passed_count,
        "tests_failed": failed_count,
        "tests_total": len(results),
        "pass_rate": round(passed_count / len(results) * 100, 1) if results else 0,
        "test_results": test_results,
    }


def extract_baseline_metrics(baseline_data: Dict) -> Dict[str, Any]:
    """Extract supplementary metrics from baseline_report.json."""
    metrics = baseline_data.get("metrics", {})
    issue_clusters = baseline_data.get("issue_clusters", {})

    # Get performance data if available
    perf = {}
    for result in baseline_data.get("builtin_results", []) + baseline_data.get("websuite_results", []):
        result_perf = result.get("perf", {})
        if result_perf:
            perf = {
                "engine_init_ms": result_perf.get("engine_init_ms"),
                "html_load_ms": result_perf.get("html_load_ms"),
                "render_time_ms": result_perf.get("render_time_ms"),
            }
            break

    return {
        "tier_a_pass_rate": metrics.get("tier_a_pass_rate", 0),
        "issue_clusters": issue_clusters,
        "perf": perf,
    }


def collect_platform_metrics(platform: str, submodule_path: Path, verbose: bool = False) -> Optional[Dict[str, Any]]:
    """Collect metrics from a platform submodule."""
    if not submodule_path.exists():
        return None

    # Try to find swarm results first (highest priority - has median across iterations)
    swarm_data, swarm_source = find_file(submodule_path, SWARM_SOURCES)

    # Try to find parity test results (priority - this has REAL pixel data)
    parity_data, parity_source = find_file(submodule_path, PARITY_TEST_SOURCES)
    baseline_data, baseline_source = find_file(submodule_path, BASELINE_SOURCES)

    # Seat build/tests feed (Windows/Linux). Orthogonal to parity: either may
    # populate a platform row. The old code returned None the moment parity
    # artefacts were absent, which is the exact defect that kept two platforms
    # grey through weeks of green CI.
    seat_row, seat_json = fetch_seat_metrics(platform)

    if not swarm_data and not parity_data and not baseline_data and not seat_row:
        print(f"  No metrics found for {platform}")
        return None

    metrics = {}

    # Extract visual parity from swarm results (highest priority - has statistical measures)
    if swarm_data:
        print(f"  Found {swarm_source} (swarm results - preferred)")
        visual_metrics = extract_swarm_metrics(swarm_data, verbose)
        metrics.update(visual_metrics)
        metrics["parity"] = visual_metrics.get("visual_parity", 0)
        metrics["parity_source"] = "swarm_median"
        metrics["last_updated"] = swarm_data.get("timestamp", datetime.now().isoformat())

    # Fall back to parity_test_results (the REAL metric)
    elif parity_data:
        print(f"  Found {parity_source} (visual parity source)")
        visual_metrics = extract_visual_parity(parity_data, verbose)
        metrics.update(visual_metrics)
        # Use visual_parity as the main "parity" metric
        metrics["parity"] = visual_metrics.get("visual_parity", 0)
        metrics["parity_source"] = "pixel_diff"
        metrics["last_updated"] = parity_data.get("timestamp", datetime.now().isoformat())

    # Extract supplementary data from baseline report
    if baseline_data:
        if not swarm_data and not parity_data:
            print(f"  Found {baseline_source} (baseline only)")
        baseline_metrics = extract_baseline_metrics(baseline_data)

        # Only use baseline parity if we don't have real pixel data
        if "parity" not in metrics:
            tier_b = baseline_metrics.get("tier_b_weighted_mean", 100)
            metrics["parity"] = max(0, 100 - tier_b)
            metrics["parity_source"] = "baseline_estimate"
            metrics["last_updated"] = baseline_data.get("timestamp", datetime.now().isoformat())

        # Always take issue clusters and perf from baseline if available
        if baseline_metrics.get("issue_clusters"):
            metrics["issue_clusters"] = baseline_metrics["issue_clusters"]
        if baseline_metrics.get("perf"):
            metrics["perf"] = baseline_metrics["perf"]
        metrics["tier_a_pass_rate"] = baseline_metrics.get("tier_a_pass_rate", 0)

    if seat_row:
        if seat_json:
            print(f"  Found metrics-history feed (build + cargo tests, enriched)")
        else:
            print(f"  Found metrics-history feed (build + cargo tests)")
        metrics.update(map_seat_metrics_to_unified(platform, seat_row, seat_json))

    # Add git commit — only when the seat feed hasn't already pinned the
    # commit the measurement was actually taken at. The submodule pointer is
    # today's tree, not the measured tree.
    if "git_commit" not in metrics:
        metrics["git_commit"] = get_git_commit(submodule_path)

    return metrics


def calculate_perf_grade(perf: Dict) -> str:
    """Calculate overall performance grade A-F."""
    if not perf:
        return "?"

    score = 100

    engine_init = perf.get("engine_init_ms")
    if engine_init:
        if engine_init > 20:
            score -= 30
        elif engine_init > 10:
            score -= 15
        elif engine_init > 5:
            score -= 5

    render_time = perf.get("render_time_ms")
    if render_time:
        if render_time > 50:
            score -= 30
        elif render_time > 30:
            score -= 15
        elif render_time > 15:
            score -= 5

    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def load_existing_unified() -> Dict[str, Any]:
    """Load existing unified metrics or create new structure."""
    if UNIFIED_FILE.exists():
        try:
            return json.loads(UNIFIED_FILE.read_text())
        except Exception:
            pass

    return {
        "generated_at": datetime.now().isoformat(),
        "platforms": {},
        "history": []
    }


def update_history(unified: Dict, platforms: Dict) -> None:
    """Update historical data with today's metrics."""
    today = datetime.now().strftime("%Y-%m-%d")
    history = unified.get("history", [])

    # Check if we already have an entry for today
    today_entry = None
    for entry in history:
        if entry.get("date") == today:
            today_entry = entry
            break

    if not today_entry:
        today_entry = {"date": today}
        history.append(today_entry)

    # Update today's entry with platform parity values
    for platform, data in platforms.items():
        if data and "parity" in data:
            today_entry[platform] = data["parity"]

        # Also add performance data
        if data and data.get("perf"):
            if "perf" not in today_entry:
                today_entry["perf"] = {}
            for key, value in data["perf"].items():
                if value is not None:
                    today_entry["perf"][key] = value

    # Keep only last 90 days of history
    history = sorted(history, key=lambda x: x.get("date", ""))[-90:]
    unified["history"] = history


def generate_test_data() -> Dict[str, Any]:
    """Generate realistic test data showing gradual improvement."""
    base_date = datetime.now()
    from datetime import timedelta

    history = []
    # Simulate gradual improvement from ~60% to ~75% over 30 days
    for i in range(30):
        date = base_date - timedelta(days=29-i)
        base_parity = 60 + i * 0.5  # Gradual improvement
        history.append({
            "date": date.strftime("%Y-%m-%d"),
            "macos": round(base_parity + (i % 3) * 0.3, 2),
            "windows": round(base_parity - 5 + (i % 4) * 0.2, 2) if i > 10 else None,
            "linux": None,
            "perf": {
                "engine_init_ms": round(8.0 - i * 0.05, 2),
                "render_time_ms": round(25.0 - i * 0.3, 2),
            }
        })

    return {
        "generated_at": datetime.now().isoformat(),
        "platforms": {
            "macos": {
                "parity": 73.6,
                "parity_source": "pixel_diff",
                "visual_parity": 73.6,
                "builtins_parity": 85.5,
                "websuite_parity": 65.2,
                "tests_passed": 7,
                "tests_failed": 16,
                "tests_total": 23,
                "pass_rate": 30.4,
                "tier_a_pass_rate": 0.30,
                "issue_clusters": {
                    "sizing_layout": 8,
                    "paint": 4,
                    "text": 6,
                    "images": 3
                },
                "perf": {"engine_init_ms": 5.2, "render_time_ms": 18.5},
                "perf_grade": "B",
                "last_updated": datetime.now().isoformat(),
                "git_commit": "73a5d78",
            },
            "windows": {
                "parity": 68.5,
                "parity_source": "pixel_diff",
                "visual_parity": 68.5,
                "tests_passed": 5,
                "tests_failed": 18,
                "tests_total": 23,
                "pass_rate": 21.7,
                "perf_grade": "C",
                "last_updated": datetime.now().isoformat(),
                "git_commit": "22aff27",
            },
            "linux": None
        },
        "history": history,
        "overall": {
            "parity": 68.5,
            "perf_grade": "B"
        }
    }


def main():
    test_mode = "--test" in sys.argv
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    print("=" * 60)
    print("HiWave Metrics Collector - Visual Parity Edition")
    print("=" * 60)
    print("\nMetrics reflect ACTUAL pixel-level visual parity with Chrome.")
    print("Lower numbers are honest - we're tracking gradual improvement.\n")

    if test_mode:
        print("Running in TEST mode with sample data\n")
        unified = generate_test_data()
    else:
        # Load existing data (to preserve history)
        unified = load_existing_unified()

        # Collect metrics from each platform
        print("Collecting platform metrics...")
        platforms = {}

        for platform, path in SUBMODULES.items():
            print(f"\n{platform.upper()}:")
            if path.exists():
                metrics = collect_platform_metrics(platform, path, verbose)
                if metrics:
                    metrics["perf_grade"] = calculate_perf_grade(metrics.get("perf", {}))
                platforms[platform] = metrics
            else:
                print(f"  Submodule not found: {path}")
                platforms[platform] = None

        # Update unified structure
        unified["generated_at"] = datetime.now().isoformat()
        unified["platforms"] = platforms

        # Calculate overall metrics (minimum parity across platforms)
        parity_values = [
            p["parity"] for p in platforms.values()
            if p and "parity" in p
        ]
        if parity_values:
            unified["overall"] = {
                "parity": round(min(parity_values), 1),
                "perf_grade": calculate_perf_grade(
                    max(
                        (p.get("perf", {}) for p in platforms.values() if p),
                        key=lambda x: -sum(v or 999 for v in x.values()) if x else 0,
                        default={}
                    )
                )
            }

        # Update history
        update_history(unified, platforms)

    # Save unified metrics
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    UNIFIED_FILE.write_text(json.dumps(unified, indent=2))
    print(f"\nSaved to: {UNIFIED_FILE}")

    # Print summary
    print("\n" + "=" * 60)
    print("Visual Parity Summary (pixel match % vs Chrome)")
    print("=" * 60)

    for platform in ["macos", "windows", "linux"]:
        data = unified.get("platforms", {}).get(platform)
        if data:
            parity = data.get("parity")
            source = data.get("parity_source", "unknown")
            passed = data.get("tests_passed", "?")
            total = data.get("tests_total", "?")
            grade = data.get("perf_grade", "?")

            print(f"\n  {platform.upper()}:")
            if parity is not None:
                print(f"    Visual Parity:  {parity:>6.2f}%  (source: {source})")
            else:
                # No parity key means parity was never measured. Printing
                # "0.00%" here would be the harness-100.0 defect inverted.
                print(f"    Visual Parity:  not measured")
            if data.get("tests_source"):
                print(f"    Tests Source:   {data['tests_source']}")
            if data.get("builtins_parity"):
                print(f"    - Builtins:     {data['builtins_parity']:>6.2f}%")
            if data.get("websuite_parity"):
                print(f"    - Websuite:     {data['websuite_parity']:>6.2f}%")
            print(f"    Tests Passing:  {passed}/{total}")
            print(f"    Perf Grade:     {grade}")
        else:
            print(f"\n  {platform.upper()}: not available")

    overall = unified.get("overall", {})
    if overall:
        print(f"\n  OVERALL: {overall.get('parity', '?')}% visual parity")

    print(f"\nHistory: {len(unified.get('history', []))} days tracked")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
