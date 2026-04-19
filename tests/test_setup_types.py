"""Tests for setup orchestration types."""
import pytest
from agent_weiss.lib.setup.types import (
    ActionKind,
    Proposal,
    Decision,
    OverrideEntry,
)


def test_action_kind_enum():
    assert ActionKind.MANUAL_ACTION.value == "manual_action"
    assert ActionKind.INSTALL_FILE.value == "install_file"
    assert ActionKind.MERGE_FRAGMENT.value == "merge_fragment"


def test_proposal_is_frozen():
    p = Proposal(
        control_id="universal.docs.agents-md-present",
        profile="universal",
        domain="docs",
        action_kind=ActionKind.MANUAL_ACTION,
        summary="Create AGENTS.md at repo root",
        instruct_path=None,
        depends_on=[],
    )
    with pytest.raises((AttributeError, TypeError)):
        p.summary = "mutated"


def test_decision_defaults():
    d = Decision()
    assert d.approve_all is False
    assert d.approve_indices == []
    assert d.skip_indices == []
    assert d.skip_reasons == {}
    assert d.approve_domains == []
    assert d.explain_index is None
    assert d.dry_run is False
    assert d.cancel is False


def test_decision_carries_full_choice_set():
    d = Decision(
        approve_indices=[1, 3, 5],
        skip_indices=[2],
        skip_reasons={2: "we use mypy not ty"},
        explain_index=4,
    )
    assert d.approve_indices == [1, 3, 5]
    assert d.skip_reasons[2] == "we use mypy not ty"
    assert d.explain_index == 4


def test_override_entry():
    o = OverrideEntry(reason="we use mypy", decided_at="2026-04-19")
    assert o.reason == "we use mypy"
    assert o.decided_at == "2026-04-19"
