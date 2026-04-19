"""Tests for setup scoring."""
from agent_weiss.lib.contract import Status
from agent_weiss.lib.verify.types import ControlResult
from agent_weiss.lib.verify.score import compute_setup_score, ScoreReport
from agent_weiss.lib.setup.types import OverrideEntry


def _result(cid: str, status: Status) -> ControlResult:
    return ControlResult(
        control_id=cid,
        profile=cid.split(".")[0],
        domain=cid.split(".")[1],
        status=status,
        summary="x",
    )


def test_setup_score_pass_is_100():
    results = [_result("a.b.c", Status.PASS)]
    report = compute_setup_score(results=results, overrides={})
    assert report.total == 100.0


def test_setup_score_fail_is_100_for_setup():
    """A failed quality check still means setup is satisfied — infrastructure ran."""
    results = [_result("a.b.c", Status.FAIL)]
    report = compute_setup_score(results=results, overrides={})
    assert report.total == 100.0


def test_setup_score_setup_unmet_is_0():
    results = [_result("a.b.c", Status.SETUP_UNMET)]
    report = compute_setup_score(results=results, overrides={})
    assert report.total == 0.0


def test_setup_score_override_counts_as_pass():
    """A control in overrides counts as 100 even if status was setup-unmet."""
    results = [_result("a.b.c", Status.SETUP_UNMET)]
    overrides = {"a.b.c": OverrideEntry(reason="x", decided_at="2026-04-19")}
    report = compute_setup_score(results=results, overrides=overrides)
    assert report.total == 100.0


def test_setup_score_per_domain_average():
    """Per-domain score = average of its controls. Total = average of domains."""
    results = [
        _result("a.docs.x", Status.PASS),         # 100
        _result("a.docs.y", Status.SETUP_UNMET),  # 0   → docs avg = 50
        _result("a.security.z", Status.PASS),     # 100 → security avg = 100
    ]
    report = compute_setup_score(results=results, overrides={})
    assert report.per_domain == {"docs": 50.0, "security": 100.0}
    # Total = avg of domains = (50 + 100) / 2 = 75
    assert report.total == 75.0


def test_setup_score_empty_results():
    """Empty results → total is 0 (or sentinel; pick 0)."""
    report = compute_setup_score(results=[], overrides={})
    assert report.total == 0.0
    assert report.per_domain == {}


def test_setup_score_report_includes_per_control():
    """Report carries the per-control 100/0 mapping for the formatter to consume."""
    results = [
        _result("a.docs.x", Status.PASS),
        _result("a.docs.y", Status.SETUP_UNMET),
    ]
    report = compute_setup_score(results=results, overrides={})
    assert report.per_control["a.docs.x"] == 100.0
    assert report.per_control["a.docs.y"] == 0.0
