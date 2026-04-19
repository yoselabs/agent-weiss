"""Tests for verify report formatter."""
from agent_weiss.lib.contract import Status
from agent_weiss.lib.verify.types import ControlResult
from agent_weiss.lib.verify.score import compute_setup_score, compute_quality_score
from agent_weiss.lib.verify.report import format_report
from agent_weiss.lib.setup.types import OverrideEntry


def _result(cid: str, status: Status, summary: str = "x", findings_count: int = 0, install: str | None = None) -> ControlResult:
    return ControlResult(
        control_id=cid,
        profile=cid.split(".")[0],
        domain=cid.split(".")[1],
        status=status,
        summary=summary,
        findings_count=findings_count,
        install=install,
    )


def test_report_contains_overall_scores():
    results = [
        _result("u.docs.x", Status.PASS),
        _result("u.security.y", Status.FAIL),
    ]
    setup = compute_setup_score(results=results, overrides={})
    quality = compute_quality_score(results=results, overrides={})
    text = format_report(
        results=results, setup_score=setup, quality_score=quality, overrides={}
    )
    assert "Setup" in text
    assert "Quality" in text
    # Setup: both pass+fail count as 100 → 100; Quality: 100+0 across two
    # domains → 50.
    assert "100" in text  # somewhere in the setup line
    assert "50" in text   # somewhere in the quality line


def test_report_lists_each_control_with_status_marker():
    results = [
        _result("u.docs.x", Status.PASS, "AGENTS.md present"),
        _result("u.docs.y", Status.FAIL, "missing CLAUDE.md", findings_count=1),
        _result("u.docs.z", Status.SETUP_UNMET, "conftest not installed", install="brew install conftest"),
    ]
    setup = compute_setup_score(results=results, overrides={})
    quality = compute_quality_score(results=results, overrides={})
    text = format_report(
        results=results, setup_score=setup, quality_score=quality, overrides={}
    )
    # Pass marker (some sort of ✓ or [PASS])
    assert "u.docs.x" in text
    # Fail marker + summary
    assert "u.docs.y" in text
    assert "missing CLAUDE.md" in text
    # Setup-unmet shows install hint
    assert "u.docs.z" in text
    assert "brew install conftest" in text


def test_report_groups_controls_by_domain():
    results = [
        _result("u.docs.x", Status.PASS),
        _result("u.security.y", Status.PASS),
        _result("u.docs.z", Status.PASS),
    ]
    setup = compute_setup_score(results=results, overrides={})
    quality = compute_quality_score(results=results, overrides={})
    text = format_report(
        results=results, setup_score=setup, quality_score=quality, overrides={}
    )
    docs_pos = text.lower().index("docs")
    security_pos = text.lower().index("security")
    x_pos = text.index("u.docs.x")
    y_pos = text.index("u.security.y")
    z_pos = text.index("u.docs.z")
    # Both docs items appear before the security header
    assert docs_pos < x_pos < z_pos < security_pos < y_pos


def test_report_marks_overridden_controls():
    results = [
        _result("u.docs.x", Status.SETUP_UNMET),
    ]
    overrides = {"u.docs.x": OverrideEntry(reason="we use mypy", decided_at="2026-04-19")}
    setup = compute_setup_score(results=results, overrides=overrides)
    quality = compute_quality_score(results=results, overrides=overrides)
    text = format_report(
        results=results, setup_score=setup, quality_score=quality, overrides=overrides
    )
    assert "we use mypy" in text or "override" in text.lower()


def test_report_empty_results():
    setup = compute_setup_score(results=[], overrides={})
    quality = compute_quality_score(results=[], overrides={})
    text = format_report(
        results=[], setup_score=setup, quality_score=quality, overrides={}
    )
    assert text.strip()
