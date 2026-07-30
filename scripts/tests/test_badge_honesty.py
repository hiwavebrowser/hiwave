"""Badges must not claim more than the metrics say.

These tests exist because the umbrella README is where HiWave makes its
cross-platform claims in public, and two badges were making claims the data did
not support:

  1. `parity-overall` printed a bare "88.1%" that was min() over platforms with
     data — and exactly one platform had data. A one-platform number was
     rendered as the project's headline.
  2. `build-<platform>` inferred build health from the PRESENCE OF A PARITY
     NUMBER. A red build with a stale parity value read "passing", and a
     platform with green CI and hundreds of passing tests read "unknown"
     because nobody had captured pixels on it.

Neither was a fabricated number. Both were true numbers with invisible scope,
which is the same class as a parity harness scoring 100.0 on an empty capture.
The point of these tests is that the class cannot come back quietly.
"""

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from generate_badges import generate_all_badges  # noqa: E402


def badge_text(svg: str) -> str:
    """The value rendered on a badge, as a reader sees it."""
    texts = re.findall(r"<text[^>]*>([^<]*)</text>", svg)
    # Badges draw each string twice (shadow + face); the value is the last one.
    return texts[-1] if texts else ""


def build_metrics(**platforms):
    return {"generated_at": "2026-07-30T00:00:00", "platforms": platforms}


# ---------------------------------------------------------------- overall parity


def test_overall_parity_shows_coverage_when_only_one_platform_measured():
    """The exact live situation: macOS measured, Windows and Linux null."""
    badges = generate_all_badges(
        build_metrics(macos={"parity": 88.14}, windows=None, linux=None)
    )
    value = badge_text(badges["parity-overall.svg"])
    assert "1/3" in value, (
        f"overall badge {value!r} hides that it covers ONE platform of three — "
        "this is the exact defect the file was fixed for"
    )
    assert "88.1" in value


def test_overall_parity_cannot_render_a_bare_percentage():
    """A bare percentage is the regression. Any N must carry its denominator."""
    for platforms in (
        {"macos": {"parity": 88.14}, "windows": None, "linux": None},
        {"macos": {"parity": 90.0}, "windows": {"parity": 80.0}, "linux": None},
        {
            "macos": {"parity": 90.0},
            "windows": {"parity": 80.0},
            "linux": {"parity": 70.0},
        },
    ):
        value = badge_text(generate_all_badges(build_metrics(**platforms))["parity-overall.svg"])
        assert re.fullmatch(r"\d+\.\d%", value) is None, (
            f"overall badge rendered bare {value!r} with no coverage"
        )
        assert "/3" in value


def test_overall_parity_is_the_worst_platform_not_the_average():
    """min() is deliberate — the project is as good as its worst platform."""
    badges = generate_all_badges(
        build_metrics(
            macos={"parity": 90.0}, windows={"parity": 80.0}, linux={"parity": 70.0}
        )
    )
    value = badge_text(badges["parity-overall.svg"])
    assert value.startswith("70.0%"), f"expected the worst platform, got {value!r}"
    assert "3/3" in value


def test_overall_parity_with_nothing_measured_says_so_with_a_denominator():
    badges = generate_all_badges(build_metrics(macos=None, windows=None, linux=None))
    value = badge_text(badges["parity-overall.svg"])
    assert "no data" in value and "0/3" in value


# ------------------------------------------------------------------ build badge


def test_build_badge_reports_a_failing_build_as_failing():
    """The dangerous case. A red build with a parity number must NOT say passing."""
    badges = generate_all_badges(
        build_metrics(macos={"build": False, "parity": 88.1}, windows=None, linux=None)
    )
    value = badge_text(badges["build-macos.svg"])
    assert value == "failing", (
        f"build badge said {value!r} for a FAILING build that happened to have a "
        "parity number — build health was being read off the wrong measurement"
    )


def test_build_badge_is_passing_without_any_parity_data():
    """Windows and Linux: green CI, hundreds of tests, no pixel capture."""
    badges = generate_all_badges(
        build_metrics(
            macos=None,
            windows={"build": True, "tests_passed": 869, "tests_total": 869},
            linux={"build": {"ok": True, "warnings": 46}, "tests_passed": 742,
                   "tests_total": 742},
        )
    )
    assert badge_text(badges["build-windows.svg"]) == "passing"
    assert badge_text(badges["build-linux.svg"]) == "passing", (
        "the dict form {'ok': True, ...} must work — platform feeds carry "
        "warning counts and run URLs beside the verdict"
    )


def test_build_badge_never_infers_passing_from_parity_alone():
    """Parity present, build UNSTATED. That is NOT-MEASURED, not passing."""
    badges = generate_all_badges(
        build_metrics(macos={"parity": 88.1}, windows=None, linux=None)
    )
    value = badge_text(badges["build-macos.svg"])
    assert value == "unknown", (
        f"build badge claimed {value!r} from a parity number alone. Build health "
        "and pixel parity are unrelated measurements."
    )


def test_build_badge_unknown_is_distinct_from_not_available():
    """Three states must stay three states: measured / not-measured / N-A."""
    badges = generate_all_badges(
        build_metrics(
            macos={},
            windows={"status": "not_available"},
            linux={"build": True},
        )
    )
    assert badge_text(badges["build-macos.svg"]) == "unknown"
    assert badge_text(badges["build-windows.svg"]) == "N/A"
    assert badge_text(badges["build-linux.svg"]) == "passing"


# ------------------------------------------------------------------- regression


def test_a_null_platform_entry_does_not_crash_any_badge():
    """windows/linux are literally null in the live unified.json."""
    badges = generate_all_badges(
        build_metrics(macos={"parity": 88.14, "tests_passed": 21, "tests_total": 26},
                      windows=None, linux=None)
    )
    assert badges, "no badges generated"
    for name, svg in badges.items():
        assert svg.strip().startswith("<svg"), f"{name} is not an svg"



# --------------------------------------------------------------- staleness guard
#
# The fourth defect, and the only one that looked right. The live umbrella
# published macOS as `parity 88.14` against `git_commit fd7e4c0` — a commit made
# 2026-07-29 — while `last_updated` said 2026-07-10. Every field was true. The
# record was a lie by juxtaposition: a twenty-day-old measurement restamped onto
# whatever commit was HEAD the night the aggregation ran.


LIVE_MACOS_DEFECT = {
    "generated_at": "2026-07-30T11:50:02.251728",
    "platforms": {
        "macos": {
            "parity": 88.14,
            "tests_passed": 21,
            "tests_total": 26,
            "git_commit": "fd7e4c0",
            "last_updated": "2026-07-10T01:34:51.035824",
        },
        "windows": None,
        "linux": None,
    },
}


def test_the_actual_live_record_is_reported_as_stale():
    """Replays the exact defect found on origin/master, values unchanged."""
    badges = generate_all_badges(LIVE_MACOS_DEFECT)
    value = badge_text(badges["parity-macos.svg"])
    assert "stale" in value, (
        f"macOS parity rendered {value!r} — a 20-day-old measurement presented "
        "as current, which is the defect this guard exists for"
    )
    assert "20d" in value, f"the age must be visible, got {value!r}"
    assert "88.1" in value, "the real measurement should still be shown, not hidden"


def test_a_stale_platform_does_not_count_toward_coverage():
    """Otherwise '1/3 measured' survives a project nobody has measured in weeks."""
    value = badge_text(generate_all_badges(LIVE_MACOS_DEFECT)["parity-overall.svg"])
    assert "0/3" in value, (
        f"overall badge said {value!r} — a stale measurement was counted as "
        "coverage, so the denominator stopped meaning 'currently measured'"
    )


def test_a_fresh_measurement_is_not_marked_stale():
    """The guard must not fire on a healthy collector."""
    fresh = {
        "generated_at": "2026-07-30T12:00:00",
        "platforms": {
            "macos": {"parity": 88.14, "last_updated": "2026-07-29T23:00:00"},
            "windows": None,
            "linux": None,
        },
    }
    assert "stale" not in badge_text(generate_all_badges(fresh)["parity-macos.svg"])
    assert "1/3" in badge_text(generate_all_badges(fresh)["parity-overall.svg"])


def test_missing_provenance_is_not_treated_as_fresh():
    """No timestamp is unknown, not current. Absence of evidence is not evidence."""
    no_ts = {
        "generated_at": "2026-07-30T12:00:00",
        "platforms": {"macos": {"parity": 88.14}, "windows": None, "linux": None},
    }
    # Cannot claim staleness without a timestamp, but must not silently bless it
    # either — the age helper returns None rather than 0.
    from generate_badges import _measured_age_days
    assert _measured_age_days({"parity": 1.0}, "2026-07-30T12:00:00") is None
    assert _measured_age_days({"last_updated": "bad"}, "2026-07-30T12:00:00") is None
    # And the badge still renders rather than crashing.
    assert badge_text(generate_all_badges(no_ts)["parity-macos.svg"]).startswith("88.1")


def test_staleness_boundary_is_the_stated_threshold():
    from generate_badges import STALE_AFTER_DAYS
    just_inside = {
        "generated_at": "2026-07-30T12:00:00",
        "platforms": {
            "macos": {"parity": 90.0,
                      "last_updated": "2026-07-24T13:00:00"},  # ~6d
            "windows": None, "linux": None,
        },
    }
    assert STALE_AFTER_DAYS == 7
    assert "stale" not in badge_text(generate_all_badges(just_inside)["parity-macos.svg"])


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
