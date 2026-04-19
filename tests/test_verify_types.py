"""Tests for verify result types."""
import pytest
from agent_weiss.lib.contract import Status
from agent_weiss.lib.verify.types import ControlResult


def test_control_result_minimum_fields():
    r = ControlResult(
        control_id="universal.docs.agents-md-present",
        profile="universal",
        domain="docs",
        status=Status.PASS,
        summary="AGENTS.md present",
        findings_count=0,
    )
    assert r.control_id == "universal.docs.agents-md-present"
    assert r.profile == "universal"
    assert r.domain == "docs"
    assert r.status is Status.PASS
    assert r.findings_count == 0


def test_control_result_optional_fields():
    r = ControlResult(
        control_id="x.y.z",
        profile="x",
        domain="y",
        status=Status.SETUP_UNMET,
        summary="conftest not found",
        findings_count=0,
        install="brew install conftest",
        details_path=None,
    )
    assert r.install == "brew install conftest"
    assert r.details_path is None


def test_control_result_is_frozen():
    r = ControlResult(
        control_id="a.b.c",
        profile="a",
        domain="b",
        status=Status.FAIL,
        summary="bad",
        findings_count=3,
    )
    with pytest.raises((AttributeError, TypeError)):
        r.summary = "mutated"
