"""Tests for quality scoring."""
from agent_weiss.lib.contract import Status
from agent_weiss.lib.verify.types import ControlResult
from agent_weiss.lib.verify.score import compute_quality_score, ScoreReport
from agent_weiss.lib.setup.types import OverrideEntry


def _result(cid: str, status: Status) -> ControlResult:
    return ControlResult(
        control_id=cid,
        profile=cid.split(".")[0],
        domain=cid.split(".")[1],
        status=status,
        summary="x",
    )


def test_quality_pass_is_100():
    results = [_result("a.b.c", Status.PASS)]
    report = compute_quality_score(results=results, overrides={})
    assert report.total == 100.0


def test_quality_fail_is_0():
    results = [_result("a.b.c", Status.FAIL)]
    report = compute_quality_score(results=results, overrides={})
    assert report.total == 0.0


def test_quality_setup_unmet_is_excluded():
    """Setup-unmet controls are not counted at all (don't penalize quality)."""
    results = [
        _result("a.b.c", Status.PASS),
        _result("a.b.d", Status.SETUP_UNMET),
    ]
    report = compute_quality_score(results=results, overrides={})
    # Only c is measurable → 100
    assert report.total == 100.0
    assert "a.b.d" not in report.per_control


def test_quality_override_counts_as_pass():
    """Overridden controls count as 100 in quality (the user's call is final)."""
    results = [_result("a.b.c", Status.SETUP_UNMET)]
    overrides = {"a.b.c": OverrideEntry(reason="x", decided_at="2026-04-19")}
    report = compute_quality_score(results=results, overrides=overrides)
    assert report.total == 100.0
    assert report.per_control["a.b.c"] == 100.0


def test_quality_per_domain_excludes_unmeasurable():
    """A domain with all setup-unmet controls is excluded from the total."""
    results = [
        _result("a.docs.x", Status.PASS),         # docs measurable: 100
        _result("a.security.y", Status.SETUP_UNMET),  # security: no measurable
        _result("a.security.z", Status.SETUP_UNMET),
    ]
    report = compute_quality_score(results=results, overrides={})
    # Only docs in per_domain
    assert "docs" in report.per_domain
    assert "security" not in report.per_domain
    assert report.total == 100.0


def test_quality_mixed_per_domain():
    """Mixed pass/fail in a domain averages; setup-unmet excluded from that average."""
    results = [
        _result("a.docs.x", Status.PASS),         # 100
        _result("a.docs.y", Status.FAIL),         # 0
        _result("a.docs.z", Status.SETUP_UNMET),  # excluded
    ]
    # docs avg of measurable: (100 + 0) / 2 = 50
    report = compute_quality_score(results=results, overrides={})
    assert report.per_domain["docs"] == 50.0


def test_quality_empty_results():
    report = compute_quality_score(results=[], overrides={})
    assert report.total == 0.0
    assert report.per_domain == {}
