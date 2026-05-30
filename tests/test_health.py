"""Tests for the self-healing health system."""

from pathlib import Path
import tempfile

from foragedj.health import HealthReport, check_paths, check_config, run_full_health_check


def test_health_report_basic():
    report = HealthReport()
    report.add_check("Test Check", "ok", "Everything fine")
    assert not report.has_errors()
    assert len(report.checks) == 1


def test_check_paths_creates_dirs():
    with tempfile.TemporaryDirectory() as tmp:
        from foragedj import health
        original_dirs = health.REQUIRED_DIRS
        test_dir = Path(tmp) / "test_required"
        health.REQUIRED_DIRS = [test_dir]

        report = HealthReport()
        check_paths(report)

        assert test_dir.exists()
        assert any("Created" in f for f in report.fixes_applied)

        health.REQUIRED_DIRS = original_dirs


def test_full_health_check_runs_without_crashing():
    """The most important integration test — does the whole self-healing checker work?"""
    report = run_full_health_check(fix=False)
    # It should always produce a report, even on a fresh/partial checkout
    assert isinstance(report, HealthReport)
    assert len(report.checks) > 5  # We expect many different checks now
