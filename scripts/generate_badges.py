#!/usr/bin/env python3
"""
generate_badges.py - Generate SVG badges for HiWave cross-platform metrics

Reads metrics from metrics/unified.json and generates SVG badges for:
- Parity scores (per platform + overall)
- Build status
- Performance scores
- Tier A pass rates

Usage:
    python3 scripts/generate_badges.py [--test]
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

REPO_ROOT = Path(__file__).parent.parent
METRICS_FILE = REPO_ROOT / "metrics" / "unified.json"
BADGES_DIR = REPO_ROOT / "badges"

# Color scheme
COLORS = {
    "green": "#4c1",       # Bright green - excellent
    "lime": "#97ca00",     # Lime - good
    "yellow": "#dfb317",   # Yellow - warning
    "orange": "#fe7d37",   # Orange - concerning
    "red": "#e05d44",      # Red - bad
    "blue": "#007ec6",     # Blue - info
    "gray": "#9f9f9f",     # Gray - N/A or unknown
    "lightgray": "#555",   # Label background
}


def get_parity_color(parity: Optional[float]) -> str:
    """Get badge color based on parity percentage."""
    if parity is None:
        return COLORS["gray"]
    if parity >= 95:
        return COLORS["green"]
    if parity >= 90:
        return COLORS["lime"]
    if parity >= 80:
        return COLORS["yellow"]
    if parity >= 60:
        return COLORS["orange"]
    return COLORS["red"]


def get_tier_a_color(rate: Optional[float]) -> str:
    """Get badge color based on Tier A pass rate (0-1)."""
    if rate is None:
        return COLORS["gray"]
    if rate >= 1.0:
        return COLORS["green"]
    if rate >= 0.8:
        return COLORS["lime"]
    if rate >= 0.6:
        return COLORS["yellow"]
    return COLORS["red"]


def get_perf_grade(metrics: Optional[Dict]) -> Tuple[str, str]:
    """Calculate performance grade (A-F) and color from metrics."""
    if not metrics:
        return "N/A", COLORS["gray"]

    # Simple scoring: average of normalized metrics against budgets
    budgets = {
        "engine_init_ms": 50,
        "render_time_ms": 50,
        "memory_peak_mb": 200,
    }

    scores = []
    for key, budget in budgets.items():
        value = metrics.get(key)
        if value is not None:
            # Score is 100 if at or below budget, decreases linearly
            score = max(0, 100 - ((value / budget - 1) * 100)) if value > budget else 100
            scores.append(score)

    if not scores:
        return "N/A", COLORS["gray"]

    avg_score = sum(scores) / len(scores)

    if avg_score >= 90:
        return "A", COLORS["green"]
    if avg_score >= 80:
        return "B", COLORS["lime"]
    if avg_score >= 70:
        return "C", COLORS["yellow"]
    if avg_score >= 60:
        return "D", COLORS["orange"]
    return "F", COLORS["red"]


def generate_badge_svg(label: str, value: str, color: str, label_width: int = 60) -> str:
    """Generate a shields.io-style SVG badge."""
    # Calculate widths
    value_width = len(value) * 7 + 10
    total_width = label_width + value_width
    label_x = label_width / 2
    value_x = label_width + value_width / 2

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="20" role="img" aria-label="{label}: {value}">
  <title>{label}: {value}</title>
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r">
    <rect width="{total_width}" height="20" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#r)">
    <rect width="{label_width}" height="20" fill="#555"/>
    <rect x="{label_width}" width="{value_width}" height="20" fill="{color}"/>
    <rect width="{total_width}" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" text-rendering="geometricPrecision" font-size="11">
    <text x="{label_x}" y="14">{label}</text>
    <text x="{value_x}" y="14">{value}</text>
  </g>
</svg>'''
    return svg


def load_metrics() -> Dict[str, Any]:
    """Load metrics from unified.json or return empty structure."""
    if METRICS_FILE.exists():
        try:
            return json.loads(METRICS_FILE.read_text())
        except Exception as e:
            print(f"Warning: Could not load metrics: {e}")

    # Return default structure if no metrics exist
    return {
        "generated_at": datetime.now().isoformat(),
        "platforms": {
            "macos": {"parity": None, "tier_a_pass_rate": None, "perf": None, "status": "no_data"},
            "windows": {"parity": None, "tier_a_pass_rate": None, "perf": None, "status": "no_data"},
            "linux": {"parity": None, "tier_a_pass_rate": None, "perf": None, "status": "not_available"},
        }
    }


PLATFORMS = ["macos", "windows", "linux"]

# A measurement older than this is reported as STALE rather than as a current
# number. Seven days is one full weekly cycle — long enough that a normally
# running collector never trips it, short enough that a silently dead one is
# caught within a week rather than after three.
STALE_AFTER_DAYS = 7


def _measured_age_days(data: Dict[str, Any], generated_at: Optional[str]) -> Optional[float]:
    """Age of a platform's measurement at aggregation time, in days.

    Returns None when either timestamp is missing or unparseable — absence of
    provenance is NOT evidence of freshness, and the caller renders it as
    unknown rather than assuming current.

    This exists because of a real defect. The umbrella published macOS as
    `parity 88.14 @ git_commit fd7e4c0` where fd7e4c0 was committed 2026-07-29
    and `last_updated` said 2026-07-10. Every field was individually true; the
    record was a lie by juxtaposition — a twenty-day-old measurement restamped
    onto whatever commit happened to be HEAD the night the aggregation ran. A
    reader sees a confident number against a current SHA and concludes the tree
    was measured. It was not.
    """
    measured = data.get("last_updated") or data.get("measured_at")
    if not measured or not generated_at:
        return None
    try:
        m = datetime.fromisoformat(str(measured).replace("Z", "+00:00"))
        g = datetime.fromisoformat(str(generated_at).replace("Z", "+00:00"))
    except ValueError:
        return None
    if m.tzinfo != g.tzinfo:  # one naive, one aware — compare on the wall clock
        m, g = m.replace(tzinfo=None), g.replace(tzinfo=None)
    return (g - m).total_seconds() / 86400.0


def _is_stale(data: Dict[str, Any], generated_at: Optional[str]) -> bool:
    age = _measured_age_days(data, generated_at)
    return age is not None and age > STALE_AFTER_DAYS


def _build_ok(data: Dict[str, Any]) -> Optional[bool]:
    """Read a platform's build status. Returns None for NOT-MEASURED.

    Three-state on purpose (hiwave.platform_metrics.v1): True / False / None
    map to MEASURED-passing / MEASURED-failing / NOT-MEASURED. Never guess a
    fourth answer from an unrelated field — an absent build status is a real
    and reportable state, and "unknown" is the honest badge for it.

    Accepts either `build: bool` or `build: {"ok": bool}` so a platform feed can
    carry warning counts and a run URL alongside the verdict.
    """
    if not data:
        return None
    build = data.get("build")
    if isinstance(build, bool):
        return build
    if isinstance(build, dict) and isinstance(build.get("ok"), bool):
        return build["ok"]
    return None


def generate_all_badges(metrics: Dict[str, Any]) -> Dict[str, str]:
    """Generate all badges from metrics, return dict of filename -> svg content."""
    badges = {}
    platforms = metrics.get("platforms", {})
    generated_at = metrics.get("generated_at")

    # Per-platform parity badges
    for platform in PLATFORMS:
        data = platforms.get(platform) or {}
        parity = data.get("parity") if data else None

        if parity is not None and _is_stale(data, generated_at):
            # MEASURED-but-old is its own state. Showing the bare number would
            # present a three-week-old figure as current; hiding it would throw
            # away a real measurement. Say both.
            age = _measured_age_days(data, generated_at)
            value = f"{parity:.1f}% · {int(age)}d stale"
            color = COLORS["gray"]
        elif parity is not None:
            value = f"{parity:.1f}%"
            color = get_parity_color(parity)
        elif data.get("status") == "not_available":
            value = "coming soon"
            color = get_parity_color(None)
        else:
            value = "no data"
            color = get_parity_color(None)

        badges[f"parity-{platform}.svg"] = generate_badge_svg("parity", value, color)

    # Overall parity badge — worst measured platform, WITH its coverage.
    #
    # This badge is the headline number on the front page of the project, so a
    # missing denominator here is the most expensive kind. Before this change it
    # read a bare "88.1%" computed as min() over platforms that happened to have
    # data — and exactly one did. A reader saw a cross-platform claim; the truth
    # was macOS alone. Same failure as a parity harness publishing a confident
    # 100.0 on no capture: not a fabricated number, a number whose scope is
    # invisible.
    #
    # Coverage is now always shown, so N=1 cannot masquerade as N=3.
    # A stale measurement is not a current one, so it does not count toward
    # coverage. Otherwise a project where nothing has been measured for three
    # weeks still advertises "1/3 measured" and the denominator fix — the whole
    # point of this badge — quietly stops meaning what it says.
    parity_values = [
        p.get("parity") for p in platforms.values()
        if p and p.get("parity") is not None and not _is_stale(p, generated_at)
    ]
    total_platforms = len(PLATFORMS)
    if parity_values:
        overall_parity = min(parity_values)
        badges["parity-overall.svg"] = generate_badge_svg(
            "parity",
            f"{overall_parity:.1f}% · {len(parity_values)}/{total_platforms}",
            get_parity_color(overall_parity),
            label_width=50,
        )
    else:
        badges["parity-overall.svg"] = generate_badge_svg(
            "parity", f"no data · 0/{total_platforms}", COLORS["gray"], label_width=50
        )

    # Per-platform Tier A badges
    for platform in ["macos", "windows", "linux"]:
        data = platforms.get(platform) or {}
        tier_a = data.get("tier_a_pass_rate")

        if tier_a is not None:
            value = f"{tier_a * 100:.0f}%"
        elif data.get("status") == "not_available":
            value = "N/A"
        else:
            value = "no data"

        color = get_tier_a_color(tier_a)
        badges[f"tier-a-{platform}.svg"] = generate_badge_svg("tier A", value, color)

    # Per-platform performance badges
    for platform in ["macos", "windows", "linux"]:
        data = platforms.get(platform) or {}
        perf = data.get("perf")
        grade, color = get_perf_grade(perf)
        badges[f"perf-{platform}.svg"] = generate_badge_svg("perf", grade, color, label_width=40)

    # Overall performance badge
    all_perf = [p.get("perf") for p in platforms.values() if p and p.get("perf")]
    if all_perf:
        # Average the grades conceptually - just use first available for now
        grade, color = get_perf_grade(all_perf[0])
        badges["perf-score.svg"] = generate_badge_svg("perf", grade, color, label_width=40)
    else:
        badges["perf-score.svg"] = generate_badge_svg("perf", "N/A", COLORS["gray"], label_width=40)

    # Build status badges — read build status, never infer it from parity.
    #
    # This previously said "passing" whenever a parity number existed. Two ways
    # that lies, and the first is the dangerous one:
    #   - a platform with a RED build and any stale parity number read "passing"
    #   - a platform that builds and tests perfectly but has no parity capture
    #     read "unknown" forever, which is why Windows and Linux stayed blank
    #     even once they had green CI and hundreds of passing tests
    # Build health and pixel parity are unrelated measurements. Asserting one
    # from the other is not a conservative default; it is a wrong answer wearing
    # a plausible label.
    for platform in PLATFORMS:
        data = platforms.get(platform) or {}
        build_ok = _build_ok(data)
        if build_ok is True:
            value, color = "passing", COLORS["green"]
        elif build_ok is False:
            value, color = "failing", COLORS["red"]
        elif data.get("status") == "not_available":
            value, color = "N/A", COLORS["gray"]
        else:
            value, color = "unknown", COLORS["gray"]
        badges[f"build-{platform}.svg"] = generate_badge_svg("build", value, color, label_width=45)

    # Tests passing badges
    for platform in ["macos", "windows", "linux"]:
        data = platforms.get(platform) or {}
        tests_passed = data.get("tests_passed")
        tests_total = data.get("tests_total")

        if tests_passed is not None and tests_total is not None:
            value = f"{tests_passed}/{tests_total}"
            pass_rate = tests_passed / tests_total if tests_total > 0 else 0
            # Color based on pass rate
            if pass_rate >= 0.8:
                color = COLORS["green"]
            elif pass_rate >= 0.5:
                color = COLORS["yellow"]
            elif pass_rate >= 0.3:
                color = COLORS["orange"]
            else:
                color = COLORS["red"]
        elif data.get("status") == "not_available":
            value, color = "N/A", COLORS["gray"]
        else:
            value, color = "no data", COLORS["gray"]

        badges[f"tests-{platform}.svg"] = generate_badge_svg("tests", value, color, label_width=40)

    # Overall tests passing badge
    total_passed = 0
    total_tests = 0
    for p in platforms.values():
        if p and p.get("tests_passed") is not None:
            total_passed += p.get("tests_passed", 0)
            total_tests += p.get("tests_total", 0)

    if total_tests > 0:
        value = f"{total_passed}/{total_tests}"
        pass_rate = total_passed / total_tests
        if pass_rate >= 0.8:
            color = COLORS["green"]
        elif pass_rate >= 0.5:
            color = COLORS["yellow"]
        elif pass_rate >= 0.3:
            color = COLORS["orange"]
        else:
            color = COLORS["red"]
        badges["tests-overall.svg"] = generate_badge_svg("tests", value, color, label_width=40)
    else:
        badges["tests-overall.svg"] = generate_badge_svg("tests", "no data", COLORS["gray"], label_width=40)

    return badges


def save_badges(badges: Dict[str, str]) -> None:
    """Save all badges to the badges directory."""
    BADGES_DIR.mkdir(parents=True, exist_ok=True)

    for filename, content in badges.items():
        filepath = BADGES_DIR / filename
        filepath.write_text(content)
        print(f"  Generated: {filename}")


def main():
    test_mode = "--test" in sys.argv

    print("=" * 50)
    print("HiWave Badge Generator")
    print("=" * 50)

    # Load metrics
    print("\nLoading metrics...")
    metrics = load_metrics()

    if test_mode:
        # Generate test data
        print("Running in TEST mode with sample data")
        metrics = {
            "generated_at": datetime.now().isoformat(),
            "platforms": {
                "macos": {
                    "parity": 98.7,
                    "tier_a_pass_rate": 1.0,
                    "perf": {"engine_init_ms": 4.5, "render_time_ms": 12.3, "memory_peak_mb": 145}
                },
                "windows": {
                    "parity": 85.2,
                    "tier_a_pass_rate": 0.8,
                    "perf": {"engine_init_ms": 6.2, "render_time_ms": 18.5, "memory_peak_mb": 180}
                },
                "linux": {
                    "parity": None,
                    "status": "not_available"
                }
            }
        }

    # Generate badges
    print("\nGenerating badges...")
    badges = generate_all_badges(metrics)

    # Save badges
    print(f"\nSaving to {BADGES_DIR}/")
    save_badges(badges)

    print(f"\nGenerated {len(badges)} badges successfully!")

    # Summary
    print("\nBadge Summary:")
    platforms = metrics.get("platforms", {})
    for platform in ["macos", "windows", "linux"]:
        data = platforms.get(platform) or {}
        parity = data.get("parity")
        status = "not available" if data.get("status") == "not_available" else (
            f"{parity:.1f}%" if parity else "no data"
        )
        print(f"  {platform}: {status}")


if __name__ == "__main__":
    main()
