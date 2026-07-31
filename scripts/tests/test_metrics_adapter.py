"""The umbrella must report seat numbers it READ, or report nothing.

These tests pin the P1 adapter: Windows/Linux build+test numbers flow from
each seat's append-only metrics-history CSV into unified.json. The failure
modes pinned here are the ones this project has actually shipped:

  1. The collector returned None for any platform without parity artefacts,
     so platforms with green CI and hundreds of passing tests stayed grey
     for weeks (wrong source path + parity-only early return).
  2. Numbers hand-typed from chat/design docs drifted from the CSV within a
     day (the 869 -> 872 lesson). Only the CSV drives numbers here.
  3. A parity value invented from build/tests/harness defaults. The parity
     key must be ABSENT for seat-fed platforms — "no data" is the honest
     badge until pixels are actually captured.
  4. Cargo unit tests and parity cases summed into one fraction. Different
     ontologies never share a denominator.

No test in this file touches the network.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from collect_metrics import (  # noqa: E402
    fetch_seat_metrics,
    map_seat_metrics_to_unified,
    parse_history_csv,
)
from generate_badges import generate_all_badges  # noqa: E402


HEADER = "timestamp,commit,branch,build_ok,passed,failed,ignored,warnings\n"

WINDOWS_ROW = (
    "2026-07-30T11:30:49Z,30929cf1aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa,"
    "master,True,869,0,5,49\n"
)

NOW = datetime(2026, 7, 31, 0, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# CSV row selection
# ---------------------------------------------------------------------------

class TestParseHistoryCsv:
    def test_last_master_row_wins(self):
        text = (
            HEADER
            + "2026-07-28T10:00:00Z,aaaa111,master,True,860,0,5,50\n"
            + WINDOWS_ROW
        )
        row = parse_history_csv(text)
        assert row["commit"].startswith("30929cf1")
        assert row["passed"] == "869"

    def test_branch_rows_never_drive_numbers(self):
        # A PR-branch row NEWER than the last master row must not win.
        text = (
            HEADER
            + WINDOWS_ROW
            + "2026-07-30T23:59:59Z,fffffff,athena/some-branch,True,999,0,0,0\n"
        )
        row = parse_history_csv(text)
        assert row["passed"] == "869"
        assert row["branch"] == "master"

    def test_no_master_row_returns_none(self):
        text = HEADER + "2026-07-30T11:00:00Z,abc,pr-branch,True,10,0,0,0\n"
        assert parse_history_csv(text) is None

    def test_header_only_returns_none(self):
        assert parse_history_csv(HEADER) is None

    def test_empty_returns_none(self):
        assert parse_history_csv("") is None

    def test_unexpected_header_returns_none(self):
        # A schema change on the producer side must fail closed, not misread
        # columns positionally.
        assert parse_history_csv("time,sha,ref\n2026,abc,master\n") is None

    def test_widened_schema_appended_columns_ok(self):
        # Windows PR #47 appended tests_ok + tests_exit_code to the CSV.
        # APPENDED columns are compatible (prefix match); reordered or
        # renamed ones are not. Live shape as of 2026-07-30:
        text = (
            "timestamp,commit,branch,build_ok,passed,failed,ignored,warnings,"
            "tests_ok,tests_exit_code\n"
            "2026-07-30T23:22:00Z,2bcbf0f4,master,True,896,0,5,49,True,0\n"
        )
        row = parse_history_csv(text)
        assert row["passed"] == "896"
        assert row["commit"] == "2bcbf0f4"


# ---------------------------------------------------------------------------
# Field mapping
# ---------------------------------------------------------------------------

def _windows_row():
    return parse_history_csv(HEADER + WINDOWS_ROW)


class TestFieldMap:
    def test_total_is_passed_plus_failed_recomputed(self):
        # The seat JSON's own "total" equals passed alone today, and ignored
        # tests inflate the denominator. Recompute, never trust pre-summed.
        row = parse_history_csv(
            HEADER + "2026-07-30T11:30:49Z,abc1234,master,True,860,9,5,49\n"
        )
        m = map_seat_metrics_to_unified("windows", row, now=NOW)
        assert m["tests_passed"] == 860
        assert m["tests_failed"] == 9
        assert m["tests_total"] == 869  # 860 + 9, ignored NOT included

    def test_parity_key_is_absent(self):
        m = map_seat_metrics_to_unified("windows", _windows_row(), now=NOW)
        assert "parity" not in m
        assert "parity_source" not in m

    def test_build_dict_shape(self):
        m = map_seat_metrics_to_unified("windows", _windows_row(), now=NOW)
        assert m["build"] == {"ok": True, "warnings": 49}

    def test_build_failing_row(self):
        row = parse_history_csv(
            HEADER + "2026-07-30T11:30:49Z,abc1234,master,False,0,3,0,12\n"
        )
        m = map_seat_metrics_to_unified("windows", row, now=NOW)
        assert m["build"]["ok"] is False

    def test_provenance_fields(self):
        m = map_seat_metrics_to_unified("windows", _windows_row(), now=NOW)
        assert m["tests_source"] == "cargo"
        assert m["metrics_source"] == "metrics-history/history.csv"
        assert m["git_commit"] == "30929cf"  # short form of the MEASURED commit
        assert m["metrics_commit"].startswith("30929cf1")
        assert m["measured_at"] == "2026-07-30T11:30:49Z"

    def test_fresh_measurement_not_flagged_stale(self):
        m = map_seat_metrics_to_unified("windows", _windows_row(), now=NOW)
        assert "metrics_stale" not in m

    def test_old_measurement_flagged_stale_but_still_published(self):
        row = parse_history_csv(
            HEADER + "2026-07-01T00:00:00Z,abc1234,master,True,800,0,5,49\n"
        )
        m = map_seat_metrics_to_unified("windows", row, now=NOW)
        assert m["metrics_stale"] is True
        assert m["tests_passed"] == 800  # published, not hidden

    def test_not_collected_passthrough(self):
        seat_json = {
            "not_collected": {"parity_pixel_diff": "requires a GPU adapter"}
        }
        m = map_seat_metrics_to_unified(
            "windows", _windows_row(), seat_json=seat_json, now=NOW
        )
        assert "parity_pixel_diff" in m["not_collected"]
        assert "parity" not in m  # evidence NOT to invent a number


# ---------------------------------------------------------------------------
# Fetch: fail closed
# ---------------------------------------------------------------------------

def _no_network(url, timeout=15):
    raise AssertionError(f"unexpected network call: {url}")


class TestFetchFailClosed:
    def test_unknown_platform_returns_nothing(self, tmp_path):
        assert fetch_seat_metrics("macos", cache_dir=tmp_path, read_url=_no_network) == (None, None)

    def test_cache_hit_never_touches_network(self, tmp_path):
        d = tmp_path / "windows"
        d.mkdir()
        (d / "history.csv").write_text(HEADER + WINDOWS_ROW)
        row, seat_json = fetch_seat_metrics(
            "windows",
            cache_dir=tmp_path,
            read_url=lambda url, timeout=15: (_ for _ in ()).throw(
                OSError("network down")
            ),
        )
        assert row is not None and row["passed"] == "869"
        assert seat_json is None  # metrics.json fetch failed -> optional, dropped

    def test_fetch_failure_returns_nothing(self, tmp_path):
        def dead(url, timeout=15):
            raise OSError("connection refused")

        assert fetch_seat_metrics("linux", cache_dir=tmp_path, read_url=dead) == (None, None)

    def test_csv_without_master_row_returns_nothing(self, tmp_path):
        d = tmp_path / "linux"
        d.mkdir()
        (d / "history.csv").write_text(
            HEADER + "2026-07-30T11:00:00Z,abc,pr-branch,True,10,0,0,0\n"
        )
        assert fetch_seat_metrics("linux", cache_dir=tmp_path, read_url=_no_network) == (None, None)


# ---------------------------------------------------------------------------
# Badge ontology guard (tests-overall)
# ---------------------------------------------------------------------------

def _svg_value(svg: str) -> str:
    # The value string appears in the rendered SVG text nodes.
    return svg


class TestTestsOverallOntology:
    def test_cargo_and_parity_cases_never_share_a_denominator(self):
        metrics = {
            "generated_at": "2026-07-30T12:00:00Z",
            "platforms": {
                "macos": {  # parity cases, no tests_source
                    "parity": 88.1,
                    "tests_passed": 21,
                    "tests_total": 26,
                    "last_updated": "2026-07-30T00:00:00Z",
                },
                "windows": {
                    "tests_passed": 869,
                    "tests_total": 869,
                    "tests_source": "cargo",
                },
                "linux": {
                    "tests_passed": 742,
                    "tests_total": 742,
                    "tests_source": "cargo",
                },
            },
        }
        svg = generate_all_badges(metrics)["tests-overall.svg"]
        assert "1611/1611 · cargo" in _svg_value(svg)
        # The forbidden mixed sum, in both orderings:
        assert "1632/1637" not in svg
        assert "890/895" not in svg

    def test_macos_only_behaviour_unchanged(self):
        metrics = {
            "generated_at": "2026-07-30T12:00:00Z",
            "platforms": {
                "macos": {
                    "parity": 88.1,
                    "tests_passed": 21,
                    "tests_total": 26,
                    "last_updated": "2026-07-30T00:00:00Z",
                },
            },
        }
        svg = generate_all_badges(metrics)["tests-overall.svg"]
        assert "21/26" in svg
        assert "cargo" not in svg

    def test_all_cargo_no_tag_needed(self):
        metrics = {
            "generated_at": "2026-07-30T12:00:00Z",
            "platforms": {
                "windows": {
                    "tests_passed": 869,
                    "tests_total": 869,
                    "tests_source": "cargo",
                },
                "linux": {
                    "tests_passed": 742,
                    "tests_total": 742,
                    "tests_source": "cargo",
                },
            },
        }
        svg = generate_all_badges(metrics)["tests-overall.svg"]
        assert "1611/1611" in svg
        assert "· cargo" not in svg  # no other ontology present to disambiguate

    def test_seat_fed_platform_parity_badge_stays_no_data(self):
        metrics = {
            "generated_at": "2026-07-30T12:00:00Z",
            "platforms": {
                "windows": {
                    "build": {"ok": True, "warnings": 49},
                    "tests_passed": 869,
                    "tests_total": 869,
                    "tests_source": "cargo",
                },
            },
        }
        badges = generate_all_badges(metrics)
        assert "no data" in badges["parity-windows.svg"]
        assert "passing" in badges["build-windows.svg"]
